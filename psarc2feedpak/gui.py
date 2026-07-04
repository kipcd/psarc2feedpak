"""A small tkinter front-end for the converter.

Pick one or more .psarc files, pick an output folder, hit Convert. Conversion
runs on a worker thread; log lines are pushed back to the UI through a queue so
the window stays responsive.
"""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from .audio import Tools
from .convert import convert, ConversionError

APP_TITLE = "psarc2feedpak"


class App:
    def __init__(self, root):
        self.root = root
        self.paths = []
        self.outdir = tk.StringVar(value="(same folder as each input)")
        self.msgs = queue.Queue()
        self.busy = False

        root.title(APP_TITLE)
        root.minsize(560, 420)

        pad = {"padx": 10, "pady": 6}
        top = ttk.Frame(root)
        top.pack(fill="x", **pad)

        ttk.Button(top, text="Add .psarc files…", command=self.pick_files
                   ).pack(side="left")
        self.count_lbl = ttk.Label(top, text="no files selected")
        self.count_lbl.pack(side="left", padx=10)
        ttk.Button(top, text="Clear", command=self.clear_files).pack(side="right")

        out = ttk.Frame(root)
        out.pack(fill="x", **pad)
        ttk.Button(out, text="Output folder…", command=self.pick_outdir
                   ).pack(side="left")
        ttk.Label(out, textvariable=self.outdir).pack(side="left", padx=10)

        self.log = tk.Text(root, height=16, wrap="word", state="disabled",
                           font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", **pad)
        self.convert_btn = ttk.Button(bottom, text="Convert",
                                      command=self.start, state="disabled")
        self.convert_btn.pack(side="right")
        self.status = ttk.Label(bottom, text="")
        self.status.pack(side="left")

        self._check_tools()
        self.root.after(100, self._drain)

    # --- tool check --------------------------------------------------------
    def _check_tools(self):
        missing = Tools().missing()
        if missing:
            self._write("Heads up: " + " and ".join(missing) + " not found. "
                        "Charts will still convert, but audio won't. "
                        "See the README for how to add them.\n")

    # --- file selection ----------------------------------------------------
    def pick_files(self):
        picked = filedialog.askopenfilenames(
            title="Choose Rocksmith .psarc files",
            filetypes=[("Rocksmith CDLC", "*.psarc"), ("All files", "*.*")])
        for p in picked:
            if p not in self.paths:
                self.paths.append(p)
        self._refresh_count()

    def clear_files(self):
        self.paths.clear()
        self._refresh_count()

    def pick_outdir(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.outdir.set(d)

    def _refresh_count(self):
        n = len(self.paths)
        self.count_lbl.config(
            text="no files selected" if n == 0
            else f"{n} file{'s' if n != 1 else ''} selected")
        if not self.busy:
            self.convert_btn.config(state="normal" if n else "disabled")

    # --- conversion --------------------------------------------------------
    def start(self):
        if self.busy or not self.paths:
            return
        self.busy = True
        self.convert_btn.config(state="disabled")
        self.status.config(text="Converting…")
        files = list(self.paths)
        outdir = self.outdir.get()
        out = None if outdir.startswith("(") else outdir
        threading.Thread(target=self._work, args=(files, out), daemon=True).start()

    def _work(self, files, outdir):
        ok = 0
        for i, src in enumerate(files, 1):
            src = Path(src)
            self.msgs.put(("log", f"\n[{i}/{len(files)}] {src.name}\n"))
            dest = None
            if outdir:
                dest = str(Path(outdir) / (src.stem + ".feedpak"))
            try:
                convert(src, dest, log=lambda m: self.msgs.put(("log", m + "\n")))
                ok += 1
            except ConversionError as e:
                self.msgs.put(("log", f"  FAILED: {e}\n"))
            except Exception as e:  # unexpected — show it rather than dying silently
                self.msgs.put(("log", f"  ERROR: {e}\n"))
        self.msgs.put(("done", f"Done — {ok}/{len(files)} converted."))

    # --- queue pump --------------------------------------------------------
    def _drain(self):
        try:
            while True:
                kind, payload = self.msgs.get_nowait()
                if kind == "log":
                    self._write(payload)
                elif kind == "done":
                    self.busy = False
                    self.status.config(text=payload)
                    self._refresh_count()
        except queue.Empty:
            pass
        self.root.after(100, self._drain)

    def _write(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
