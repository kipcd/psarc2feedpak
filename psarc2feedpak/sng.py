"""Binary layout of a decrypted Rocksmith 2014 .sng file.

Field names follow the community reverse-engineering (rscustom's toolkit,
0x0L/rocksmith). Everything is little-endian. Parse a blob with ``Song.parse``.
"""

from construct import (
    Float32l, Float64l, If, Int8sl, Int16sl, Int16ul, Int32sl, Int32ul,
    PaddedString, Padding, PrefixedArray, Struct, len_, this,
)


def _list(subcon):
    return PrefixedArray(Int32ul, subcon)


Bend = Struct("time" / Float32l, "step" / Float32l, Padding(3), "unk" / Int8sl)

Beat = Struct(
    "time" / Float32l,
    "measure" / Int16ul,
    "beat" / Int16ul,
    "phraseIteration" / Int32ul,
    "mask" / Int32ul,
)

Phrase = Struct(
    "solo" / Int8sl,
    "disparity" / Int8sl,
    "ignore" / Int8sl,
    Padding(1),
    "maxDifficulty" / Int32ul,
    "iterationLinks" / Int32ul,
    "name" / PaddedString(32, "utf8"),
)

ChordTemplate = Struct(
    "mask" / Int32ul,
    "frets" / Int8sl[6],
    "fingers" / Int8sl[6],
    "notes" / Int32sl[6],
    "name" / PaddedString(32, "utf8"),
)

ChordNote = Struct(
    "mask" / Int32ul[6],
    "bends" / Struct("steps" / Bend[32], "count" / Int32ul)[6],
    "slideTo" / Int8sl[6],
    "slideUnpitchTo" / Int8sl[6],
    "vibrato" / Int16sl[6],
)

Vocal = Struct(
    "time" / Float32l,
    "note" / Int32sl,
    "length" / Float32l,
    "lyric" / PaddedString(48, "utf8"),
)

# Vocals carry a symbol/font atlas we don't need, but must skip past it to keep
# the stream aligned when vocals are present.
_Texture = Struct(
    "fontpath" / PaddedString(128, "ascii"),
    "fontpathLength" / Int32ul,
    Padding(4),
    "width" / Int32ul,
    "height" / Int32ul,
)
_Rect = Struct("y0" / Float32l, "x0" / Float32l, "y1" / Float32l, "x1" / Float32l)
_SymbolDef = Struct(
    "name" / PaddedString(12, "utf8"),
    "outer" / _Rect,
    "inner" / _Rect,
)
Symbols = Struct(
    "header" / _list(Int32sl[8]),
    "textures" / _list(_Texture),
    "defs" / _list(_SymbolDef),
)

PhraseIteration = Struct(
    "phraseId" / Int32ul,
    "time" / Float32l,
    "endTime" / Float32l,
    "difficulty" / Int32ul[3],
)

PhraseExtraInfo = Struct(
    "phraseId" / Int32ul,
    "difficulty" / Int32ul,
    "empty" / Int32ul,
    "levelJump" / Int8sl,
    "redundant" / Int16sl,
    Padding(1),
)

LinkedDiff = Struct("levelBreak" / Int32sl, "phrases" / _list(Int32ul))
Action = Struct("time" / Float32l, "name" / PaddedString(256, "ascii"))
Event = Struct("time" / Float32l, "name" / PaddedString(256, "ascii"))
Tone = Struct("time" / Float32l, "id" / Int32ul)
Dna = Struct("time" / Float32l, "id" / Int32ul)

Section = Struct(
    "name" / PaddedString(32, "utf8"),
    "number" / Int32ul,
    "startTime" / Float32l,
    "endTime" / Float32l,
    "startIterId" / Int32ul,
    "endIterId" / Int32ul,
    "stringMask" / Int8sl[36],
)

Anchor = Struct(
    "time" / Float32l,
    "endTime" / Float32l,
    "unk1" / Float32l,
    "unk2" / Float32l,
    "fret" / Int32sl,
    "width" / Int32sl,
    "iterId" / Int32ul,
)

AnchorExtension = Struct("time" / Float32l, "fret" / Int8sl, Padding(7))

Fingerprint = Struct(
    "chordId" / Int32ul,
    "startTime" / Float32l,
    "endTime" / Float32l,
    "unk1" / Float32l,
    "unk2" / Float32l,
)

Note = Struct(
    "mask" / Int32ul,
    "flags" / Int32ul,
    "hash" / Int32ul,
    "time" / Float32l,
    "string" / Int8sl,
    "fret" / Int8sl,
    "anchorFret" / Int8sl,
    "anchorWidth" / Int8sl,
    "chordId" / Int32ul,
    "chordNoteId" / Int32ul,
    "phraseId" / Int32ul,
    "iterId" / Int32ul,
    "fingerprintId" / Int16ul[2],
    "nextNote" / Int16ul,
    "prevNote" / Int16ul,
    "parentPrevNote" / Int16ul,
    "slideTo" / Int8sl,
    "slideUnpitchTo" / Int8sl,
    "leftHand" / Int8sl,
    "tap" / Int8sl,
    "pickDirection" / Int8sl,
    "slap" / Int8sl,
    "pluck" / Int8sl,
    "vibrato" / Int16sl,
    "sustain" / Float32l,
    "bendTime" / Float32l,
    "bends" / _list(Bend),
)

Level = Struct(
    "difficulty" / Int32ul,
    "anchors" / _list(Anchor),
    "anchorExtensions" / _list(AnchorExtension),
    "fingerprints" / _list(Fingerprint)[2],
    "notes" / _list(Note),
    "avgNotesPerIter" / _list(Float32l),
    "notesInIterNoIgnored" / _list(Int32ul),
    "notesInIter" / _list(Int32ul),
)

Metadata = Struct(
    "maxScore" / Float64l,
    "maxNotes" / Float64l,
    "maxNotesNoIgnored" / Float64l,
    "pointsPerNote" / Float64l,
    "firstBeatLength" / Float32l,
    "startTime" / Float32l,
    "capo" / Int8sl,
    "lastConversion" / PaddedString(32, "ascii"),
    "part" / Int16sl,
    "songLength" / Float32l,
    "tuning" / _list(Int16sl),
    "firstNoteTime" / Float32l,
    "firstNoteTime2" / Float32l,
    "maxDifficulty" / Int32sl,
)

Song = Struct(
    "beats" / _list(Beat),
    "phrases" / _list(Phrase),
    "chordTemplates" / _list(ChordTemplate),
    "chordNotes" / _list(ChordNote),
    "vocals" / _list(Vocal),
    "symbols" / If(len_(this.vocals) > 0, Symbols),
    "phraseIterations" / _list(PhraseIteration),
    "phraseExtraInfos" / _list(PhraseExtraInfo),
    "linkedDiffs" / _list(LinkedDiff),
    "actions" / _list(Action),
    "events" / _list(Event),
    "tones" / _list(Tone),
    "dna" / _list(Dna),
    "sections" / _list(Section),
    "levels" / _list(Level),
    "metadata" / Metadata,
)

# --- note mask bits ---------------------------------------------------------
CHORD = 0x02
OPEN = 0x04
FRETHANDMUTE = 0x08
TREMOLO = 0x10
HARMONIC = 0x20
PALMMUTE = 0x40
SLAP = 0x80
PLUCK = 0x100
HAMMERON = 0x200
PULLOFF = 0x400
SLIDE = 0x800
BEND = 0x1000
SUSTAIN = 0x2000
TAP = 0x4000
PINCHHARMONIC = 0x8000
VIBRATO = 0x10000
MUTE = 0x20000
IGNORE = 0x40000
HIGHDENSITY = 0x200000
SLIDEUNPITCHED = 0x400000
CHORDNOTES = 0x1000000
ACCENT = 0x4000000
LINKNEXT = 0x8000000
ARPEGGIO = 0x20000000

TEMPLATE_ARPEGGIO = 0x01
