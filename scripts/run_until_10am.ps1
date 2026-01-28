$ErrorActionPreference = 'Stop'

$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
$root = Split-Path -Parent $scriptDir
$reports = Join-Path $root 'reports'
if (!(Test-Path $reports)) {
    New-Item -ItemType Directory -Force -Path $reports | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $reports ("merged-until-10am-" + $timestamp + ".log")

function Write-Log([string]$message) {
    $line = "[{0}] {1}" -f (Get-Date -Format o), $message
    $line | Tee-Object -FilePath $logPath -Append | Out-Null
}

$now = Get-Date
$target = Get-Date -Year 2026 -Month 1 -Day 28 -Hour 10 -Minute 0 -Second 0
if ($now -ge $target) {
    Write-Log \"Target time already passed: $($target.ToString('o'))\"
    exit 1
}

Write-Log ("Target end time: {0}" -f $target.ToString('o'))

$runner = Join-Path $root 'brain/run_shotgun_test.py'
while ((Get-Date) -lt $target) {
    if (Test-Path $runner) {
        $remaining = [int][Math]::Ceiling(($target - (Get-Date)).TotalMinutes)
        if ($remaining -le 0) { break }
        Write-Log ("Running shotgun test for {0} minutes" -f $remaining)
        docker compose -f (Join-Path $root 'docker-compose.yml') up -d ft_bot 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null
        docker compose -f (Join-Path $root 'docker-compose.yml') run --rm runner `
            python brain/run_shotgun_test.py --duration-min $remaining 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null
        Write-Log "Shotgun test finished"
        break
    } else {
        Write-Log "Missing brain/run_shotgun_test.py. Waiting 60s for build to complete."
        Start-Sleep -Seconds 60
    }
}

Write-Log "Run-until-10am script exiting"
