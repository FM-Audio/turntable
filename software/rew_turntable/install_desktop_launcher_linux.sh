#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$(dirname "$(readlink -f "$0")")"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/64x64/apps"
mkdir -p "$DESKTOP_DIR" "$ICON_DIR"
cp "$APP_DIR/assets/fm_audio_logo.png" "$ICON_DIR/fm-audio-rew-turntable.png"
cat > "$DESKTOP_DIR/fm-audio-rew-turntable.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=FM-Audio REW Turntable
Comment=REW-Drehteller Messreihen steuern
Exec=sh -c 'cd "$APP_DIR" && python3 rew_turntable_gui.py'
Icon=fm-audio-rew-turntable
Terminal=false
Categories=AudioVideo;Audio;Science;
StartupNotify=true
EOF
chmod +x "$DESKTOP_DIR/fm-audio-rew-turntable.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
printf 'Desktop launcher installed: %s\n' "$DESKTOP_DIR/fm-audio-rew-turntable.desktop"
