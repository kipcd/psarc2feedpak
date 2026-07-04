"""AES keys and helpers for Rocksmith 2014 archives.

The keys below are the fixed keys Rocksmith 2014 ships with; they're the same
ones every open-source RS tool uses. ARC_* unwraps the PSARC table of contents,
WIN/MAC_KEY decrypt the per-song .sng blobs.
"""

import zlib

from construct import Int32ul
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

try:  # CFB moved namespaces in cryptography 43+
    from cryptography.hazmat.decrepit.ciphers.modes import CFB
    from cryptography.hazmat.primitives.ciphers.modes import CTR
except ImportError:  # pragma: no cover - older cryptography
    from cryptography.hazmat.primitives.ciphers.modes import CFB, CTR

ARC_KEY = bytes.fromhex(
    "C53DB23870A1A2F71CAE64061FDD0E1157309DC85204D4C5BFDF25090DF2572C"
)
ARC_IV = bytes.fromhex("E915AA018FEF71FC508132E4BB4CEB42")

WIN_KEY = bytes.fromhex(
    "CB648DF3D12A16BF71701414E69619EC171CCA5D2A142E3E59DE7ADDA18A3A30"
)
MAC_KEY = bytes.fromhex(
    "9821330E34B91F70D0A48CBD625993126970CEA09192C0E6CDA676CC9838289D"
)


def decrypt_toc(data):
    dec = Cipher(algorithms.AES(ARC_KEY), CFB(ARC_IV)).decryptor()
    return dec.update(data) + dec.finalize()


def decrypt_sng(data, key):
    """Decrypt one .sng blob and inflate its payload."""
    iv = data[8:24]
    dec = Cipher(algorithms.AES(key), CTR(iv)).decryptor()
    plain = dec.update(data[24:]) + dec.finalize()
    size = Int32ul.parse(plain[:4])
    payload = zlib.decompress(plain[4:])
    if len(payload) != size:
        raise ValueError(f"sng size mismatch: {len(payload)} != {size}")
    return payload
