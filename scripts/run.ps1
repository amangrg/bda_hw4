param(
  [string]$Python = "python"
)

# Change to project root and make src importable
Push-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))
$env:PYTHONPATH = "$PWD;$($env:PYTHONPATH)"

# Datasets (adjust paths if yours differ)
$chess   = "data\chess.dat"
$retail  = "data\retail.dat"
$outdir  = "output"

# Support sets
$chessSupports  = 3000
$retailSupports = @()
for ($s=700; $s -le 1200; $s+=100) { $retailSupports += $s }

# Small helper to run one job
function Run-Job($datasetPath, $support, [bool]$useOpt) {
  $args = @("scripts\benchmark.py", $datasetPath, $support.ToString(), "--outdir", $outdir)
  if ($useOpt) { $args += @("--hash-prune","--txn-reduction") }
  Write-Host ">>> $Python $($args -join ' ')" -ForegroundColor Cyan
  & $Python @args
}

# CHESS: baseline + optimized
Write-Host "`n== CHESS ==" -ForegroundColor Yellow
foreach ($ms in $chessSupports) {
  Run-Job $chess $ms $false
  Run-Job $chess $ms $true
}

# RETAIL: baseline + optimized
Write-Host "`n== RETAIL ==" -ForegroundColor Yellow
foreach ($ms in $retailSupports) {
  Run-Job $retail $ms $false
  Run-Job $retail $ms $true
}

Write-Host "`nAll done. Outputs and metrics are in '$outdir'." -ForegroundColor Green
Pop-Location
