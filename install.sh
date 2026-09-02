#!/bin/bash
# Sonic Scratch installer for macOS.
#   curl -fsSL https://raw.githubusercontent.com/johnwards/sonic-scratch/main/install.sh | bash
#
# Installs Sonic Pi if needed, copies the bridge into Application Support and
# creates "Sonic Scratch.app" in Applications. The app is built here on your
# machine, so macOS doesn't treat it as an untrusted download.
set -euo pipefail

REPO="${SONIC_SCRATCH_REPO:-johnwards/sonic-scratch}"
REF="${SONIC_SCRATCH_REF:-main}"
DEST="$HOME/Library/Application Support/Sonic Scratch"
APP_DIR="/Applications"
[ -w "$APP_DIR" ] || APP_DIR="$HOME/Applications"
APP="$APP_DIR/Sonic Scratch.app"

say() { printf '\n\033[1;35m==>\033[0m %s\n' "$*"; }

if [ "$(uname)" != "Darwin" ]; then
  echo "This installer is for macOS. On Windows, run install.ps1 (see the README)."
  exit 1
fi

# 1. Sonic Pi
if [ ! -d "/Applications/Sonic Pi.app" ]; then
  if command -v brew >/dev/null 2>&1; then
    say "Installing Sonic Pi with Homebrew (this can take a few minutes)"
    brew install --cask sonic-pi
  else
    say "Sonic Pi isn't installed"
    echo "Download it from https://sonic-pi.net, drag it into Applications, then run this installer again."
    open "https://sonic-pi.net" || true
    exit 1
  fi
fi

# 2. Files
say "Installing Sonic Scratch into $DEST"
mkdir -p "$DEST"
if [ -n "${SONIC_SCRATCH_SRC:-}" ]; then
  cp -R "$SONIC_SCRATCH_SRC"/. "$DEST"/
else
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$REF.tar.gz" | tar -xz --strip-components=1 -C "$DEST"
fi
chmod +x "$DEST"/bin/*.command

# 3. The app
say "Creating $APP"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Sonic Scratch</string>
  <key>CFBundleDisplayName</key><string>Sonic Scratch</string>
  <key>CFBundleIdentifier</key><string>net.sonic-pi.scratch.launcher</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>sonic-scratch</string>
  <key>CFBundleIconFile</key><string>icon</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
</dict></plist>
EOF
cat > "$APP/Contents/MacOS/sonic-scratch" <<EOF
#!/bin/bash
# Opens the bridge in a Terminal window so the Sonic Pi log is visible.
exec open -a Terminal "$DEST/bin/sonic-scratch.command"
EOF
chmod +x "$APP/Contents/MacOS/sonic-scratch"

# Icon: render the SVG with the system's Quick Look, then pack it. Purely cosmetic, so never fatal.
(
  set -e
  TMP="$(mktemp -d)"
  qlmanage -t -s 1024 -o "$TMP" "$DEST/icon.svg" >/dev/null 2>&1
  PNG="$TMP/icon.svg.png"
  [ -f "$PNG" ]
  mkdir -p "$TMP/icon.iconset"
  for s in 16 32 128 256 512; do
    sips -z $s $s "$PNG" --out "$TMP/icon.iconset/icon_${s}x${s}.png" >/dev/null
    sips -z $((s*2)) $((s*2)) "$PNG" --out "$TMP/icon.iconset/icon_${s}x${s}@2x.png" >/dev/null
  done
  iconutil -c icns "$TMP/icon.iconset" -o "$APP/Contents/Resources/icon.icns"
  rm -rf "$TMP"
) || echo "(couldn't build an icon, carrying on)"
touch "$APP"

say "Done"
echo "Sonic Scratch is in $APP_DIR."
echo "Double-click it to start. It boots Sonic Pi and opens Scratch in your browser."
echo "The first time, your browser asks whether turbowarp.org may connect to devices on your local network: click Allow."
if [ -z "${SONIC_SCRATCH_NO_LAUNCH:-}" ] && [ -t 0 ]; then
  read -r -p "Start it now? [Y/n] " ans
  case "$ans" in n|N) ;; *) open "$APP" ;; esac
fi
