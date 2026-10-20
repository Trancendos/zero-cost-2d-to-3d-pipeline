# aaf_detect_hardware.ps1 - AAF execution profile detection (DRAFT)
# Mirrors deriveProfile() in aaf/adaptive-core/adaptive_core.ts - keep in sync.
# Exit codes: 0 = profile written | 1 = detection failure
$ErrorActionPreference = "Stop"
$dataDir = Join-Path $PSScriptRoot "aaf-data"
if (-not (Test-Path $dataDir)) { New-Item -ItemType Directory -Path $dataDir | Out-Null }

$nvidiaSmiOk = $false
$gpuName = $null
$gpuVramMb = $null

try {
  $gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1
  if ($gpu) {
    $gpuName = $gpu.Name
    # AdapterRAM is uint32 and wraps above 4 GB; treat >=4000 as "4096+"
    $gpuVramMb = if ($gpu.AdapterRAM -gt 0) { [math]::Min([double]$gpu.AdapterRAM / 1MB, 4096) } else { $null }
  }
} catch { $gpuName = $null }

try { if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
  $smi = & nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>$null
  if ($LASTEXITCODE -eq 0 -and $smi) {
    $nvidiaSmiOk = $true
    $parts = ($smi | Select-Object -First 1) -split ","
    $gpuName = $parts[0].Trim()
    $gpuVramMb = [double]$parts[1].Trim()
  }
}} catch { $nvidiaSmiOk = $false }

$ramGb = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)

# Port of deriveProfile() - keep in sync with the Adaptive Core
$mode = "offline"
if ($nvidiaSmiOk -and $gpuVramMb -ge 6000) { $mode = "gpu-local" }
elseif ($ramGb -ge 8) { $mode = "cpu-local" }
elseif ($ramGb -ge 4) { $mode = "cpu-local-degraded" }

$profile = [ordered]@{
  schema = "aaf.execution-profile.v1"
  detected_utc = (Get-Date).ToUniversalTime().ToString("o")
  os = "windows"
  cuda = $nvidiaSmiOk
  gpu = $gpuName
  gpu_vram_mb = $gpuVramMb
  ram_gb = $ramGb
  mode = $mode
}
$profile | ConvertTo-Json | Out-File (Join-Path $dataDir "execution_profile.json") -Encoding utf8
Write-Host ("AAF execution profile: " + $mode + " (cuda=" + $nvidiaSmiOk + ", ram=" + $ramGb + "GB)")
