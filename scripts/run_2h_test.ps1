$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$reports = Join-Path $root 'reports'
if (!(Test-Path $reports)) {
    New-Item -ItemType Directory -Force -Path $reports | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $reports ("merged-2h-" + $timestamp + ".log")

function Write-Log([string]$message) {
    $line = "[{0}] {1}" -f (Get-Date -Format o), $message
    $line | Tee-Object -FilePath $logPath -Append | Out-Null
}

Write-Log "2-hour test starting"

$required = @(
    'docker-compose.yml',
    'shared_data/init_db.py',
    'freqtrade/user_data/config.json',
    'brain'
)
$missing = @()
foreach ($item in $required) {
    $path = Join-Path $root $item
    if (!(Test-Path $path)) {
        $missing += $item
    }
}

if ($missing.Count -gt 0) {
    Write-Log ("Missing required items: " + ($missing -join ', '))
    exit 1
}

Write-Log "Initializing DB"
python (Join-Path $root 'shared_data/init_db.py') 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null

Write-Log "Starting docker compose"
docker compose -f (Join-Path $root 'docker-compose.yml') up -d ft_bot 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null

$runner = Join-Path $root 'brain/run_shotgun_test.py'
if (!(Test-Path $runner)) {
    Write-Log "Missing brain/run_shotgun_test.py. Build the merged system before running the 2-hour test."
    exit 1
}

Write-Log "Running shotgun test for 120 minutes"
docker compose -f (Join-Path $root 'docker-compose.yml') run --rm runner `
    python brain/run_shotgun_test.py --duration-min 120 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null

Write-Log "2-hour test finished"
