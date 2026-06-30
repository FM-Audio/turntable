#!/usr/bin/env python3
"""
REW Turntable Runner for FM-Audio ARTA Turntable
================================================

Controls the existing Arduino turntable over UDP and coordinates measurements
with Room EQ Wizard (REW) through the REW 5.40+ HTTP API.

Important:
- REW API defaults to localhost:4735 and should normally be accessed from the
  same computer that runs REW.
- Starting automated sweep measurements through the REW API requires a REW Pro
  upgrade license. Without Pro, use --mode manual: the script rotates the
  turntable, then waits until you manually create the measurement in REW.

Existing Arduino protocol:
- UDP target: turntable_ip:10049
- Payload: ASCII integer/float angle, e.g. "0", "15", "-30"
- Reply: short text from Arduino
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from dataclasses import dataclass
from typing import Any, Iterable
from urllib import error, request


DEFAULT_TURNTABLE_PORT = 10049
DEFAULT_REW_URL = "http://127.0.0.1:4735"


@dataclass
class RewResult:
    ok: bool
    status: int | None = None
    data: Any = None
    error: str | None = None


class TurntableClient:
    def __init__(self, host: str, port: int = DEFAULT_TURNTABLE_PORT, timeout: float = 10.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def move_to(self, angle: float) -> str:
        payload = ("%g" % angle).encode("ascii")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        started = time.time()
        try:
            sock.sendto(payload, (self.host, self.port))
            data, addr = sock.recvfrom(2048)
            elapsed = time.time() - started
            return f"reply_from={addr[0]}:{addr[1]} elapsed={elapsed:.2f}s text={data.decode('utf-8', 'replace')}"
        finally:
            sock.close()


class RewClient:
    def __init__(self, base_url: str = DEFAULT_REW_URL, timeout: float = 20.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, body: Any = None) -> RewResult:
        url = self.base_url + path
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(url, data=data, method=method, headers=headers)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                parsed = None
                if raw:
                    try:
                        parsed = json.loads(raw)
                    except json.JSONDecodeError:
                        parsed = raw
                return RewResult(ok=True, status=resp.status, data=parsed)
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            return RewResult(ok=False, status=exc.code, error=raw or str(exc))
        except Exception as exc:  # noqa: BLE001 - CLI should report any connection error clearly
            return RewResult(ok=False, error=f"{type(exc).__name__}: {exc}")

    def get(self, path: str) -> RewResult:
        return self._request("GET", path)

    def post(self, path: str, body: Any = None) -> RewResult:
        return self._request("POST", path, body)

    def put(self, path: str, body: Any = None) -> RewResult:
        return self._request("PUT", path, body)

    def health(self) -> RewResult:
        return self.get("/application/commands")

    def measurements(self) -> list[dict[str, Any]]:
        res = self.get("/measurements")
        if not res.ok:
            raise RuntimeError(f"REW /measurements failed: {res.error}")
        if isinstance(res.data, list):
            return res.data
        return []

    def measurement_count(self) -> int:
        return len(self.measurements())

    def set_next_name(self, name: str) -> None:
        # REW accepts partial data models for PUT/POST. If this fails we keep going;
        # naming can also be handled after the measurement.
        self.put("/measure/naming", {"name": name})

    def set_notes(self, notes: str) -> None:
        self.post("/measure/notes", notes)

    def start_spl_measurement(self) -> RewResult:
        # Same command used by REW API example tools for a sweep/SPL measurement.
        return self.post("/measure/command", {"command": "SPL"})

    def wait_for_new_measurement(self, count_before: int, timeout_s: float) -> dict[str, Any] | None:
        end = time.time() + timeout_s
        while time.time() < end:
            measurements = self.measurements()
            if len(measurements) > count_before:
                return measurements[-1]
            time.sleep(0.5)
        return None


def parse_angles(spec: str) -> list[float]:
    """Parse angles from either comma list or start:stop:step."""
    spec = spec.strip()
    if ":" in spec:
        parts = [float(p) for p in spec.split(":")]
        if len(parts) != 3:
            raise ValueError("range format must be start:stop:step, e.g. 0:180:15")
        start, stop, step = parts
        if step == 0:
            raise ValueError("step must not be zero")
        vals = []
        x = start
        if step > 0:
            while x <= stop + 1e-9:
                vals.append(round(x, 6))
                x += step
        else:
            while x >= stop - 1e-9:
                vals.append(round(x, 6))
                x += step
        return vals
    return [float(p.strip()) for p in spec.split(",") if p.strip()]


def print_json(label: str, value: Any) -> None:
    print(label)
    print(json.dumps(value, indent=2, ensure_ascii=False))


def run_sequence(args: argparse.Namespace) -> int:
    turntable = TurntableClient(args.turntable_ip, args.turntable_port, timeout=args.turntable_timeout)
    rew = RewClient(args.rew_url, timeout=args.rew_timeout)
    angles = parse_angles(args.angles)

    if args.mode in {"auto", "manual"}:
        health = rew.health()
        if not health.ok:
            print(f"ERROR: REW API not reachable at {args.rew_url}: {health.error}", file=sys.stderr)
            print("Start REW 5.40+ with API enabled, e.g. roomeqwizard.exe -api", file=sys.stderr)
            return 2
        print("REW API reachable.")

    for angle in angles:
        label = args.name_template.format(angle=("%g" % angle))
        print(f"\n=== angle {angle:g}° ===")

        if args.dry_run:
            print(f"DRY-RUN turntable -> {args.turntable_ip}:{args.turntable_port} angle={angle:g}")
        else:
            print(turntable.move_to(angle))

        if args.settle_s > 0:
            print(f"settle {args.settle_s:g}s")
            time.sleep(args.settle_s)

        if args.mode == "turntable-only":
            continue

        count_before = rew.measurement_count()
        rew.set_next_name(label)
        rew.set_notes(f"Turntable angle: {angle:g} degrees")

        if args.mode == "manual":
            print(f"Manual mode: start/save the REW measurement now for {angle:g}°. Waiting for new measurement...")
        else:
            result = rew.start_spl_measurement()
            if not result.ok:
                print(f"ERROR: REW auto measurement failed: HTTP {result.status} {result.error}", file=sys.stderr)
                print("If this mentions licensing, use --mode manual or install REW Pro upgrade.", file=sys.stderr)
                return 3
            print(f"REW measurement command accepted: HTTP {result.status}")

        new_measurement = rew.wait_for_new_measurement(count_before, args.measure_timeout)
        if new_measurement is None:
            print(f"ERROR: no new REW measurement detected within {args.measure_timeout:g}s", file=sys.stderr)
            return 4
        print_json("New measurement:", new_measurement)

    print("\nDone.")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Control FM-Audio Arduino turntable and coordinate REW measurements.")
    parser.add_argument("--turntable-ip", required=True, help="Arduino turntable IP address, e.g. 192.168.178.191")
    parser.add_argument("--turntable-port", type=int, default=DEFAULT_TURNTABLE_PORT)
    parser.add_argument("--turntable-timeout", type=float, default=10.0)
    parser.add_argument("--rew-url", default=DEFAULT_REW_URL, help="REW API base URL, default http://127.0.0.1:4735")
    parser.add_argument("--rew-timeout", type=float, default=20.0)
    parser.add_argument("--angles", default="0:180:15", help="Comma list or range start:stop:step, e.g. 0,15,30 or 0:180:15")
    parser.add_argument("--settle-s", type=float, default=3.0, help="Wait time after moving before measurement")
    parser.add_argument("--measure-timeout", type=float, default=120.0)
    parser.add_argument("--name-template", default="Angle {angle} deg")
    parser.add_argument("--mode", choices=["turntable-only", "manual", "auto"], default="manual")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return run_sequence(args)


if __name__ == "__main__":
    raise SystemExit(main())
