# aaf_watchdog.ps1 - AAF proactive maintenance (DRAFT)
# Zero-cost proactive layer: orphaned temp cleanup + weights integrity check.
# Register as a scheduled task (run once from an admin shell, adjust the -File path):
#   schtasks /Create /TN "AAF Watchdog" /SC DAILY /MO 1 /TR "powershell -ExecutionPolicy Bypass -File aaf_watchdog.ps1" /ST 09:00
$ErrorActionPreference = "Continue"
$log = Join-Path $PSScriptRoot "aaf-data/watchdog.jsonl"
function Log($event, $detail) {
  @{ time = (Get-Date).ToUniversalTime().ToString("o"); event = $event; detail = $detail } |
    ConvertTo-Json -Compress | Add-Content $log
}

# 1. Orphaned temp GLBs older than 24h (prototype delete=False cleanup)
Get-ChildItem $env:TEMP -Filter "aaf-*.glb" -ErrorAction SilentlyContinue |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddHours(-24) } |
  ForEach-Object { Log "temp-cleanup" $_.Name; Remove-Item $_.FullName -ErrorAction SilentlyContinue }

# 2. Weights snapshot integrity (if a recorded hash file exists)
$hashFile = Join-Path $PSScriptRoot "aaf-data/weights.sha256"
$weightsDir = Join-Path $PSScriptRoot "aaf-data/model-snapshot"
if ((Test-Path $hashFile) -and (Test-Path $weightsDir)) {
  $expected = (Get-Content $hashFile)[0].Split(" ")[0].Trim()
  $actual = (Get-FileHash (Join-Path $weightsDir "*.safetensors") -Algorithm SHA256 -ErrorAction SilentlyContinue |
    Select-Object -First 1).Hash.ToLower()
  if ($actual -ne $expected) { Log "weights-hash-mismatch" ("expected=" + $expected + " actual=" + $actual) }
}

# 3. Stale running jobs (SQLite check left to the API poller; watchdog only guards files)
Log "watchdog-run" "ok"
