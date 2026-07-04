# psarc2feedpak

Convert Rocksmith 2014 custom songs (`.psarc` CDLC) into
[feedpak](https://github.com/got-feedback/feedpak-spec) packages for
[got-feedBack](https://github.com/got-feedback).

It unpacks the archive, decodes the binary `.sng` arrangements, and rewrites the
notes, chords, anchors, handshapes, beats, sections and lyrics as a `.feedpak`.
Audio (`.wem`) is transcoded to OGG and the album art (`.dds`) to PNG.

## Install

```
pip install construct cryptography
```

Audio conversion needs two external tools on your `PATH` (or drop
`vgmstream-cli` in `tools/vgmstream/`):

- [vgmstream](https://vgmstream.org/) — decodes Wwise `.wem`
- [ffmpeg](https://ffmpeg.org/) — OGG encode + DDS→PNG

## Usage

Command line:

```
python -m psarc2feedpak song_p.psarc
python -m psarc2feedpak song_p.psarc -o out.feedpak
python -m psarc2feedpak song_p.psarc --keep-dir   # also leave the unzipped folder
```

Output defaults to `<artist> - <title>.feedpak` next to the input.

GUI:

```
python -m psarc2feedpak.gui
```

Pick one or more `.psarc` files, choose an output folder, and convert. Prebuilt
Windows builds (with ffmpeg and vgmstream bundled, no Python needed) are on the
[Releases](https://github.com/carelesshangman/psarc2feedpak/releases) page.

## Notes

- The difficulty ladder is flattened to the full (hardest) chart.
- Vocal arrangements become `lyrics.json` + `vocal_pitch.json`.
- Only extraction is implemented — it never writes `.psarc`.

## Legal

The AES keys required to read a `.psarc` are the fixed keys Rocksmith 2014 ships
with, the same ones every open-source RS tool has used for a decade. This is a
tool for converting songs you already own for personal use.

This project is independent and is **not affiliated with, endorsed by, or
associated with any of the businesses, products, or projects it interoperates
with** — including Ubisoft / Rocksmith, got-feedBack, ffmpeg, or vgmstream. All
trademarks belong to their respective owners. The prebuilt releases bundle
ffmpeg (GPL) and vgmstream (see their licenses in the download).

## Credits

PSARC/SNG parsing follows the community reverse-engineering work in
[0x0L/rocksmith](https://github.com/0x0L/rocksmith) and the
[Rocksmith Custom Song Toolkit](https://github.com/rscustom/rocksmith-custom-song-toolkit).

## License

MIT
