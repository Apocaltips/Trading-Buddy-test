param(
    [int]$intervalMin = 10,
    [int]$iterations = 6
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$reports = Join-Path $root 'reports'
if (!(Test-Path $reports)) {
    New-Item -ItemType Directory -Force -Path $reports | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $reports ("monitor-" + $timestamp + ".log")

function Write-Log([string]$message) {
    $line = "[{0}] {1}" -f (Get-Date -Format o), $message
    $line | Tee-Object -FilePath $logPath -Append | Out-Null
}

function Check-Containers {
    try {
        $ps = docker ps --format "{{.Names}}|{{.Image}}|{{.Status}}"
    } catch {
        Write-Log "WARN: docker ps failed: $_"
        return
    }

    $ft = $ps | Select-String -Pattern 'freqtrade'
    $runner = $ps | Select-String -Pattern 'runner'

    if ($ft) {
        Write-Log "OK: ft_bot running -> $($ft.ToString().Trim())"
    } else {
        Write-Log "WARN: ft_bot not running"
    }

    if ($runner) {
        Write-Log "OK: runner running -> $($runner.ToString().Trim())"
    } else {
        Write-Log "WARN: runner not running"
    }
}

function Check-Api {
    try {
        $token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('freqtrade:changeme'))
        $headers = @{ Authorization = "Basic $token" }
        $resp = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/ping" -Headers $headers -TimeoutSec 5
        Write-Log "OK: Freqtrade API ping -> $resp"
    } catch {
        Write-Log "WARN: Freqtrade API ping failed: $_"
    }
}

function Check-Signals {
    $py = @"
import os, sqlite3, statistics
from datetime import datetime, timezone

root = r"""$root"""
path = os.path.join(root, "shared_data", "signals.db")
if not os.path.exists(path):
    path = "/shared_data/signals.db"

try:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT pair, price_snapshot, inserted_at, ts_utc FROM signal_bus ORDER BY inserted_at DESC LIMIT 20")
    rows = cur.fetchall()
finally:
    try:
        conn.close()
    except Exception:
        pass

if not rows:
    print("NO_SIGNALS")
    raise SystemExit(0)

prices = [float(r[1]) for r in rows if r[1] is not None]
std = statistics.pstdev(prices) if len(prices) > 1 else 0.0
latest = rows[0]
inserted = latest[2] or latest[3]
age_min = None
if inserted:
    try:
        ts = datetime.fromisoformat(str(inserted).replace("Z", "+00:00"))
        age_min = (datetime.now(timezone.utc) - ts).total_seconds() / 60.0
    except Exception:
        age_min = None

print(f"SAMPLES={len(rows)} PRICE_STD={std:.3f} AGE_MIN={age_min if age_min is not None else 'NA'}")
if std < 2.0:
    print("LOW_VARIANCE=1")
"@

    try {
        $output = $py | python -
        foreach ($line in $output) {
            Write-Log $line
        }
    } catch {
        Write-Log "WARN: signal check failed: $_"
    }
}

Write-Log "Monitoring started"
for ($i = 1; $i -le $iterations; $i++) {
    Write-Log "Check $i/$iterations"
    Check-Containers
    Check-Api
    Check-Signals
    if ($i -lt $iterations) {
        Start-Sleep -Seconds ($intervalMin * 60)
    }
}

Write-Log "Monitoring finished"
