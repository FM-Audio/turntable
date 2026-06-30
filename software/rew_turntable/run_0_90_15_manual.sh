#!/usr/bin/env bash
# REW group-measurement helper for FM-Audio turntable.
# Equivalent workflow to ARTA's "Spatial impulse response group record":
# rotate 0..90 degrees in 15-degree steps and wait for one REW measurement per angle.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "$SCRIPT_DIR/rew_turntable_runner.py" \
  --turntable-ip "${TURNTABLE_IP:-192.168.178.191}" \
  --rew-url "${REW_URL:-http://127.0.0.1:4735}" \
  --mode "${REW_TURNTABLE_MODE:-manual}" \
  --angles "${REW_TURNTABLE_ANGLES:-0:90:15}" \
  --settle-s "${REW_TURNTABLE_SETTLE_S:-3}" \
  --measure-timeout "${REW_TURNTABLE_MEASURE_TIMEOUT:-180}" \
  --start-frequency "${REW_TURNTABLE_START_FREQ:-150}" \
  --end-frequency "${REW_TURNTABLE_END_FREQ:-20000}" \
  --sweep-length "${REW_TURNTABLE_SWEEP_LENGTH:-512k}" \
  --name-template "${REW_TURNTABLE_NAME_TEMPLATE:-Angle {angle} deg}"
