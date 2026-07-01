#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
exec python3 rew_turntable_gui.py "$@"
