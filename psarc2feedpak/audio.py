"""Wwise .wem and .dds handling via external tools (vgmstream, ffmpeg)."""

import shutil
import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_VENDORED = [_HERE.parent / "tools" / "vgmstream", _HERE.parent / "tools"]


def find(name, extra_dirs=()):
    for d in list(extra_dirs) + _VENDORED:
        exe = Path(d) / f"{name}.exe"
        if exe.exists():
            return str(exe)
    return shutil.which(name)


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
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
