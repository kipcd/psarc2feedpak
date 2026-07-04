"""Read a Rocksmith 2014 PSARC archive into {path: bytes}.

Only the bits we need to unpack are implemented (no writing). The header is
followed by an encrypted table of contents: one entry per file plus a list of
per-block compressed lengths. Block length 0 means "full block, stored raw or
that decompressed to BLOCK_SIZE".
"""

import zlib
from io import BytesIO

from construct import BytesInteger, Bytes, Const, GreedyRange, Struct

from .crypto import decrypt_toc, decrypt_sng, WIN_KEY, MAC_KEY

BLOCK_SIZE = 1 << 16

_HEADER = Struct(
    "magic" / Const(b"PSAR"),
    "version" / BytesInteger(4),
    "compression" / Const(b"zlib"),
    "toc_size" / BytesInteger(4),
    "entry_size" / BytesInteger(4),
    "n_entries" / BytesInteger(4),
    "block_size" / BytesInteger(4),
    "flags" / BytesInteger(4),
)

_ENTRY = Struct(
    "md5" / Bytes(16),
    "zindex" / BytesInteger(4),
    "length" / BytesInteger(5),
    "offset" / BytesInteger(5),
)


def _read_entry(f, entry, zlengths):
    f.seek(entry.offset)
    out = BytesIO()
    for z in zlengths[entry.zindex:]:
        if out.tell() >= entry.length:
            break
        chunk = f.read(BLOCK_SIZE if z == 0 else z)
        try:
            chunk = zlib.decompress(chunk)
        except zlib.error:
            pass  # stored uncompressed
        out.write(chunk)
    data = out.getvalue()
    if len(data) != entry.length:
        raise ValueError(f"psarc entry size mismatch: {len(data)} != {entry.length}")
    return data


def read(path):
    """Extract every file. .sng entries come back already decrypted+inflated."""
    with open(path, "rb") as f:
        header = _HEADER.parse_stream(f)
        toc = f.read(header.toc_size - 32)
        if header.flags & 4:
            toc = decrypt_toc(toc)

        parsed = Struct(
            "entries" / _ENTRY[header.n_entries],
            "zlengths" / GreedyRange(BytesInteger(2)),
        ).parse(toc)
        zlengths = list(parsed.zlengths)

        # First entry is the manifest: a newline-separated list of the rest.
        names = _read_entry(f, parsed.entries[0], zlengths).decode().splitlines()
        files = {
            name: _read_entry(f, parsed.entries[i + 1], zlengths)
            for i, name in enumerate(names)
        }

    for name, blob in files.items():
        if "songs/bin/generic/" in name:
            files[name] = decrypt_sng(blob, WIN_KEY)
        elif "songs/bin/macos/" in name:
            files[name] = decrypt_sng(blob, MAC_KEY)
    return files
