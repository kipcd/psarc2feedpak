"""Wwise .wem and .dds handling via external tools (vgmstream, ffmpeg)."""

import shutil
import subprocess
import sys
from pathlib import Path


def _search_dirs():
    """Where to look for bundled tools, most-specific first.

    Covers running from source and running as a PyInstaller build, where the
    binaries sit next to the .exe (or in its _MEIPASS temp dir) under tools/.
    """
    roots = []
    if getattr(sys, "frozen", False):
        roots += [Path(sys.executable).resolve().parent,
                  Path(getattr(sys, "_MEIPASS", "."))]
    roots.append(Path(__file__).resolve().parent.parent)  # repo root from source
    dirs = []
    for r in roots:
        dirs += [r / "tools" / "vgmstream", r / "tools", r]
    return dirs


def find(name, extra_dirs=()):
    for d in list(extra_dirs) + _search_dirs():
        exe = Path(d) / f"{name}.exe"
        if exe.exists():
            return str(exe)
    return shutil.which(name)


# Keep the child tools from flashing a console window under a windowed GUI build.
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, creationflags=_NO_WINDOW)
    if p.returncode != 0:
        raise RuntimeError(f"{Path(cmd[0]).name} failed:\n{p.stderr[-800:]}")


class Tools:
    """Bundles the external binaries so callers fail early if they're missing."""

    def __init__(self):
        self.vgmstream = find("vgmstream-cli")
        self.ffmpeg = find("ffmpeg")

    @property
    def can_audio(self):
        return bool(self.vgmstream and self.ffmpeg)

    def missing(self):
        out = []
        if not self.vgmstream:
            out.append("vgmstream-cli")
        if not self.ffmpeg:
            out.append("ffmpeg")
        return out

    def wem_to_ogg(self, wem_bytes, out_ogg, scratch, quality=5):
        wem = scratch / "_a.wem"
        wav = scratch / "_a.wav"
        wem.write_bytes(wem_bytes)
        _run([self.vgmstream, "-o", str(wav), str(wem)])
        _run([self.ffmpeg, "-y", "-i", str(wav),
              "-c:a", "libvorbis", "-q:a", str(quality), str(out_ogg)])
        wem.unlink()
        wav.unlink()

    def dds_to_png(self, dds_bytes, out_png, scratch):
        dds = scratch / "_c.dds"
        dds.write_bytes(dds_bytes)
        _run([self.ffmpeg, "-y", "-i", str(dds), str(out_png)])
        dds.unlink()
