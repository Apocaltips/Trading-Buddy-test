$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$reports = Join-Path $root 'reports'
$comparisonDir = Join-Path $reports 'comparison'
New-Item -ItemType Directory -Force -Path $comparisonDir | Out-Null

$latest = Get-ChildItem -Path $reports -Filter '*.json' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $latest) {
    Write-Host 'No report JSON found.'
    exit 1
}

$metrics = Get-Content $latest.FullName | ConvertFrom-Json
$summaryPath = Join-Path $comparisonDir 'summary.md'

$lines = @(
    '# Comparison Summary',
    '',
    "Report: $($latest.Name)",
    "Start (UTC): $($metrics.start_utc)",
    "End (UTC): $($metrics.end_utc)",
    "Duration (sec): $($metrics.duration_sec)",
    '',
    '## Summary Metrics',
    "- Trades total: $($metrics.trades_total)",
    "- Trades/hour: $($metrics.trades_per_hour)",
    "- Win rate: $($metrics.win_rate)",
    "- Net PnL: $($metrics.net_pnl)",
    "- Net PnL/hour: $($metrics.net_pnl_per_hour)",
    "- Fee drag: $($metrics.fee_drag)",
    "- Max drawdown: $($metrics.max_drawdown)",
    '',
    '## Chart Metrics',
    "- Confluence scores: $($metrics.confluence_scores)",
    "- Pattern counts: $($metrics.pattern_counts)",
    '',
    '## Notes',
    '- Baseline: 10-hour Mac run',
    '- This is a smoke-test comparison only'
)

$lines | Set-Content -Path $summaryPath
Copy-Item -Path $latest.FullName -Destination (Join-Path $comparisonDir $latest.Name) -Force

Write-Host "Comparison summary written to $summaryPath"
