$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$reports = Join-Path $root 'reports'
if (!(Test-Path $reports)) {
    New-Item -ItemType Directory -Force -Path $reports | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $reports ("plumbing-test-" + $timestamp + ".log")

function Write-Log([string]$message) {
    $line = "[{0}] {1}" -f (Get-Date -Format o), $message
    $line | Tee-Object -FilePath $logPath -Append | Out-Null
}

Write-Log "Plumbing test starting (5 min)"

python (Join-Path $root 'shared_data/init_db.py') 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null

Write-Log "Starting docker compose"
docker compose -f (Join-Path $root 'docker-compose.yml') up -d ft_bot 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null

$runner = Join-Path $root 'brain/run_shotgun_test.py'
if (!(Test-Path $runner)) {
    Write-Log "Missing brain/run_shotgun_test.py"
    exit 1
}

Write-Log "Running shotgun test for 5 minutes"
docker compose -f (Join-Path $root 'docker-compose.yml') run --rm runner `
    python brain/run_shotgun_test.py --duration-min 5 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null

Write-Log "Plumbing test finished"
