#!/usr/bin/env python3
"""Small desktop GUI for using the FM-Audio turntable with REW.

This is the REW counterpart to ARTA's "Spatial impulse response group record"
workflow: choose start/stop/step, then let the program rotate the turntable and
coordinate one REW measurement per angle.
"""

from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from rew_turntable_runner import (
    DEFAULT_REW_URL,
    DEFAULT_TURNTABLE_PORT,
    RewClient,
    TurntableClient,
    parse_angles,
)

DEFAULT_TURNTABLE_IP = "192.168.178.191"


class RewTurntableGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("REW Turntable Controller")
        self.geometry("920x700")
        self.minsize(820, 620)

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.stop_event = threading.Event()

        self.turntable_ip = tk.StringVar(value=DEFAULT_TURNTABLE_IP)
        self.turntable_port = tk.IntVar(value=DEFAULT_TURNTABLE_PORT)
        self.rew_url = tk.StringVar(value=DEFAULT_REW_URL)
        self.start_angle = tk.DoubleVar(value=0.0)
        self.stop_angle = tk.DoubleVar(value=135.0)
        self.step_angle = tk.DoubleVar(value=10.0)
        self.single_angle = tk.DoubleVar(value=0.0)
        self.settle_s = tk.DoubleVar(value=3.0)
        self.measure_timeout = tk.DoubleVar(value=180.0)
        self.mode = tk.StringVar(value="manual")
        self.name_template = tk.StringVar(value="Angle {angle} deg")

        self._build_ui()
        self.after(100, self._drain_log_queue)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)

        title = ttk.Label(
            root,
            text="REW-Drehteller: Messreihe starten wie in ARTA",
            font=("TkDefaultFont", 15, "bold"),
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        conn = ttk.LabelFrame(root, text="Verbindung")
        conn.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for i in range(8):
            conn.columnconfigure(i, weight=1 if i in (1, 5) else 0)

        ttk.Label(conn, text="Turntable IP").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(conn, textvariable=self.turntable_ip, width=18).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(conn, text="UDP Port").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        ttk.Entry(conn, textvariable=self.turntable_port, width=8).grid(row=0, column=3, sticky="w", padx=6, pady=6)
        ttk.Label(conn, text="REW API URL").grid(row=0, column=4, sticky="w", padx=6, pady=6)
        ttk.Entry(conn, textvariable=self.rew_url, width=28).grid(row=0, column=5, sticky="ew", padx=6, pady=6)
        ttk.Button(conn, text="REW prüfen", command=self.check_rew).grid(row=0, column=6, padx=6, pady=6)
        ttk.Button(conn, text="Teller 0°", command=lambda: self.move_single(0.0)).grid(row=0, column=7, padx=6, pady=6)

        seq = ttk.LabelFrame(root, text="Messreihe")
        seq.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for i in range(12):
            seq.columnconfigure(i, weight=1 if i in (1, 3, 5, 11) else 0)

        ttk.Label(seq, text="Start °").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ttk.Entry(seq, textvariable=self.start_angle, width=8).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        ttk.Label(seq, text="Ende °").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ttk.Entry(seq, textvariable=self.stop_angle, width=8).grid(row=0, column=3, padx=6, pady=6, sticky="ew")
        ttk.Label(seq, text="Schritt °").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        ttk.Entry(seq, textvariable=self.step_angle, width=8).grid(row=0, column=5, padx=6, pady=6, sticky="ew")
        ttk.Label(seq, text="Pause s").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        ttk.Entry(seq, textvariable=self.settle_s, width=8).grid(row=0, column=7, padx=6, pady=6, sticky="ew")
        ttk.Label(seq, text="Timeout s").grid(row=0, column=8, padx=6, pady=6, sticky="w")
        ttk.Entry(seq, textvariable=self.measure_timeout, width=8).grid(row=0, column=9, padx=6, pady=6, sticky="ew")

        mode_box = ttk.Frame(seq)
        mode_box.grid(row=1, column=0, columnspan=6, sticky="w", padx=6, pady=6)
        ttk.Label(mode_box, text="Modus:").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Radiobutton(mode_box, text="Manuell: ich starte jede REW-Messung", value="manual", variable=self.mode).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(mode_box, text="Auto: REW per API starten", value="auto", variable=self.mode).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(mode_box, text="Nur drehen", value="turntable-only", variable=self.mode).pack(side=tk.LEFT, padx=4)

        ttk.Label(seq, text="Name").grid(row=1, column=6, padx=6, pady=6, sticky="w")
        ttk.Entry(seq, textvariable=self.name_template).grid(row=1, column=7, columnspan=5, sticky="ew", padx=6, pady=6)

        buttons = ttk.Frame(seq)
        buttons.grid(row=2, column=0, columnspan=12, sticky="ew", padx=6, pady=(6, 8))
        ttk.Button(buttons, text="Winkel anzeigen", command=self.preview_angles).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(buttons, text="Messreihe starten", command=self.start_sequence).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(buttons, text="Stop nach aktuellem Schritt", command=self.stop_sequence).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(buttons, text="Einzelwinkel °").pack(side=tk.LEFT)
        ttk.Entry(buttons, textvariable=self.single_angle, width=8).pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="Einzelwinkel fahren", command=lambda: self.move_single()).pack(side=tk.LEFT)

        log_frame = ttk.LabelFrame(root, text="Protokoll / Bedienhinweise")
        log_frame.grid(row=3, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=18)
        scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        self.log(
            "Bereit. Beispiel: Start 0°, Ende 135°, Schritt 10° eingeben und 'Messreihe starten'.\n"
            "Im manuellen Modus fährt das Programm den Winkel an und wartet, bis in REW eine neue Messung entstanden ist."
        )

    def log(self, text: str) -> None:
        self.log_queue.put(text)

    def _drain_log_queue(self) -> None:
        while True:
            try:
                text = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log_text.insert(tk.END, text.rstrip() + "\n")
            self.log_text.see(tk.END)
        self.after(100, self._drain_log_queue)

    def get_angles(self) -> list[float]:
        return parse_angles(f"{self.start_angle.get()}:{self.stop_angle.get()}:{self.step_angle.get()}")

    def make_turntable(self) -> TurntableClient:
        return TurntableClient(self.turntable_ip.get().strip(), int(self.turntable_port.get()), timeout=20.0)

    def make_rew(self) -> RewClient:
        return RewClient(self.rew_url.get().strip(), timeout=20.0)

    def check_rew(self) -> None:
        def work() -> None:
            rew = self.make_rew()
            res = rew.health()
            if res.ok:
                self.log(f"REW API OK: {self.rew_url.get()}")
            else:
                self.log(f"REW API FEHLER: {res.error}")
        self._start_worker(work)

    def preview_angles(self) -> None:
        try:
            angles = self.get_angles()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ungültige Winkel", str(exc))
            return
        self.log("Winkelreihe: " + ", ".join(f"{a:g}°" for a in angles))

    def move_single(self, angle: float | None = None) -> None:
        if angle is None:
            angle = self.single_angle.get()

        def work() -> None:
            self.log(f"Fahre Einzelwinkel {angle:g}° ...")
            try:
                reply = self.make_turntable().move_to(float(angle))
                self.log(reply)
            except Exception as exc:  # noqa: BLE001
                self.log(f"FEHLER beim Fahren: {type(exc).__name__}: {exc}")
        self._start_worker(work)

    def start_sequence(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Läuft bereits", "Es läuft bereits ein Vorgang.")
            return
        try:
            angles = self.get_angles()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ungültige Winkel", str(exc))
            return
        if not angles:
            messagebox.showerror("Keine Winkel", "Die Winkelreihe ist leer.")
            return
        if self.mode.get() == "auto":
            if not messagebox.askyesno(
                "Auto-Messung starten?",
                "Auto-Modus startet REW-Messungen per API. Pegel, Mikrofon und Lautsprecher müssen bereit sein. Fortfahren?",
            ):
                return
        self.stop_event.clear()
        self._start_worker(lambda: self._run_sequence(angles))

    def stop_sequence(self) -> None:
        self.stop_event.set()
        self.log("Stop angefordert: Abbruch nach aktuellem Schritt bzw. nach aktueller Messwartezeit.")

    def _start_worker(self, fn: Any) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Läuft bereits", "Bitte warten, bis der aktuelle Vorgang fertig ist.")
            return
        self.worker = threading.Thread(target=fn, daemon=True)
        self.worker.start()

    def _run_sequence(self, angles: list[float]) -> None:
        turntable = self.make_turntable()
        rew = self.make_rew()
        mode = self.mode.get()
        settle_s = float(self.settle_s.get())
        measure_timeout = float(self.measure_timeout.get())
        name_template = self.name_template.get()

        self.log("Starte Messreihe: " + ", ".join(f"{a:g}°" for a in angles))
        if mode in {"manual", "auto"}:
            health = rew.health()
            if not health.ok:
                self.log(f"ABBRUCH: REW API nicht erreichbar: {health.error}")
                return
            self.log("REW API OK.")

        for angle in angles:
            if self.stop_event.is_set():
                self.log("Messreihe gestoppt.")
                return

            self.log(f"\n=== {angle:g}° ===")
            try:
                self.log(turntable.move_to(angle))
            except Exception as exc:  # noqa: BLE001
                self.log(f"ABBRUCH: Turntable-Fehler: {type(exc).__name__}: {exc}")
                return

            if settle_s > 0:
                self.log(f"Warte {settle_s:g} s Einschwingzeit ...")
                end = time.time() + settle_s
                while time.time() < end:
                    if self.stop_event.is_set():
                        self.log("Messreihe gestoppt.")
                        return
                    time.sleep(0.1)

            if mode == "turntable-only":
                continue

            try:
                count_before = rew.measurement_count()
                label = name_template.format(angle=("%g" % angle))
                rew.set_next_name(label)
                rew.set_notes(f"Turntable angle: {angle:g} degrees")
            except Exception as exc:  # noqa: BLE001
                self.log(f"ABBRUCH: REW-Vorbereitung fehlgeschlagen: {type(exc).__name__}: {exc}")
                return

            if mode == "manual":
                self.log(f"Jetzt in REW die Messung für {angle:g}° starten. Ich warte auf eine neue Messung ...")
            else:
                result = rew.start_spl_measurement()
                if not result.ok:
                    self.log(f"ABBRUCH: REW Auto-Messung fehlgeschlagen: HTTP {result.status} {result.error}")
                    self.log("Wenn REW eine Lizenzmeldung zeigt: manuellen Modus verwenden oder REW Pro aktivieren.")
                    return
                self.log(f"REW-Messbefehl angenommen: HTTP {result.status}")

            found = self._wait_for_new_measurement(rew, count_before, measure_timeout)
            if found is None:
                self.log(f"ABBRUCH: Keine neue REW-Messung innerhalb von {measure_timeout:g} s erkannt.")
                return
            self.log(f"Messung erkannt: {found.get('title', '<ohne Titel>')} uuid={found.get('uuid', '<unbekannt>')}")

        self.log("\nMessreihe fertig.")

    def _wait_for_new_measurement(self, rew: RewClient, count_before: int, timeout_s: float) -> dict[str, Any] | None:
        end = time.time() + timeout_s
        while time.time() < end:
            if self.stop_event.is_set():
                return None
            try:
                measurements = rew.measurements()
            except Exception as exc:  # noqa: BLE001
                self.log(f"REW-Abfragefehler: {type(exc).__name__}: {exc}")
                time.sleep(1)
                continue
            if len(measurements) > count_before:
                return measurements[-1]
            time.sleep(0.5)
        return None


def main() -> int:
    app = RewTurntableGui()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
