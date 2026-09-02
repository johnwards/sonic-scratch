# Sonic Scratch installer for Windows. Run in PowerShell:
#   irm https://raw.githubusercontent.com/johnwards/sonic-scratch/main/install.ps1 | iex
#
# Finds Sonic Pi, copies the bridge into %LOCALAPPDATA%\SonicScratch and puts a
# "Sonic Scratch" shortcut on the Desktop and in the Start Menu.
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"  # Invoke-WebRequest is very slow with the progress bar on

$Repo = if ($env:SONIC_SCRATCH_REPO) { $env:SONIC_SCRATCH_REPO } else { "johnwards/sonic-scratch" }
$Ref  = if ($env:SONIC_SCRATCH_REF)  { $env:SONIC_SCRATCH_REF }  else { "main" }
$Dest = Join-Path $env:LOCALAPPDATA "SonicScratch"

function Say($msg) { Write-Host "`n==> $msg" -ForegroundColor Magenta }

function Find-SonicPi {
    $candidates = @()
    foreach ($base in @($env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if ($base) { $candidates += (Join-Path $base "Sonic Pi") }
    }
    if ($env:LOCALAPPDATA) { $candidates += (Join-Path $env:LOCALAPPDATA "Programs\Sonic Pi") }
    $keys = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    foreach ($k in $keys) {
        Get-ItemProperty $k -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -like "Sonic Pi*" -and $_.InstallLocation } |
            ForEach-Object { $candidates += $_.InstallLocation.TrimEnd("\") }
    }
    foreach ($c in $candidates) {
        if (Test-Path (Join-Path $c "app\server\native\ruby\bin\ruby.exe")) { return $c }
    }
    return $null
}

# 1. Sonic Pi
$SonicPi = Find-SonicPi
if (-not $SonicPi) {
    Say "Sonic Pi isn't installed"
    Write-Host "Download and install it from https://sonic-pi.net, then run this installer again."
    Start-Process "https://sonic-pi.net"
    return
}
Say "Found Sonic Pi at $SonicPi"

# 2. Files
Say "Installing Sonic Scratch into $Dest"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
if ($env:SONIC_SCRATCH_SRC) {
    Copy-Item -Recurse -Force (Join-Path $env:SONIC_SCRATCH_SRC "*") $Dest
} else {
    $zip = Join-Path $env:TEMP "sonic-scratch.zip"
    $tmp = Join-Path $env:TEMP "sonic-scratch-unzip"
    Invoke-WebRequest "https://github.com/$Repo/archive/refs/heads/$Ref.zip" -OutFile $zip
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Expand-Archive $zip -DestinationPath $tmp -Force
    $inner = Get-ChildItem $tmp -Directory | Select-Object -First 1
    Copy-Item -Recurse -Force (Join-Path $inner.FullName "*") $Dest
    Remove-Item -Recurse -Force $tmp, $zip -ErrorAction SilentlyContinue
}
Set-Content -Path (Join-Path $Dest "sonicpi-path.txt") -Value $SonicPi -NoNewline

# 3. Shortcuts
Say "Creating shortcuts"
$launcher = Join-Path $Dest "bin\sonic-scratch.cmd"
$exe = Get-ChildItem $SonicPi -Filter "*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
$shell = New-Object -ComObject WScript.Shell
$places = @(
    [Environment]::GetFolderPath("Desktop"),
    (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs")
)
foreach ($dir in $places) {
    if (-not (Test-Path $dir)) { continue }
    $lnk = $shell.CreateShortcut((Join-Path $dir "Sonic Scratch.lnk"))
    $lnk.TargetPath = $launcher
    $lnk.WorkingDirectory = $Dest
    $lnk.Description = "Sonic Pi blocks for Scratch"
    if ($exe) { $lnk.IconLocation = "$($exe.FullName),0" }
    $lnk.Save()
}

Say "Done"
Write-Host "Double-click 'Sonic Scratch' on your Desktop to start. It boots Sonic Pi and opens Scratch in your browser."
Write-Host "The first time, your browser asks whether turbowarp.org may connect to devices on your local network: click Allow."
if (-not $env:SONIC_SCRATCH_NO_LAUNCH) {
    $ans = Read-Host "Start it now? [Y/n]"
    if ($ans -notmatch "^[nN]") { Start-Process $launcher -WorkingDirectory $Dest }
}
