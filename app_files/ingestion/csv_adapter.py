"""CSV adapter: the existing chardet-backed CSV read, behind the Adapter API."""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from app_files.ingestion.base import Adapter

# Encodings to try when chardet is unavailable or returns something unusable.
# cp1252 precedes latin-1 so bytes in 0x80-0x9F (curly quotes, em dash) decode
# to the characters Windows actually wrote; latin-1 is the never-fails catch-all.
_FALLBACK_ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")

# Unicode blocks for the scripts a codepage guess can claim, so the guess can be
# checked against the text it actually produces.
_SCRIPT_RANGES = {
    "cyrillic": ((0x0400, 0x04FF), (0x0500, 0x052F)),
    "greek": ((0x0370, 0x03FF), (0x1F00, 0x1FFF)),
    "hebrew": ((0x0590, 0x05FF),),
    "arabic": ((0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF)),
    "hangul": ((0xAC00, 0xD7AF), (0x1100, 0x11FF)),
    "kana": ((0x3040, 0x30FF),),
    "han": ((0x4E00, 0x9FFF),),
    "thai": ((0x0E00, 0x0E7F),),
}
# Which script each codepage inevitably produces, used to verify the guess.
_GUESS_SCRIPT = {
    "windows-1251": "cyrillic", "cp1251": "cyrillic", "koi8-r": "cyrillic",
    "koi8-u": "cyrillic", "iso-8859-5": "cyrillic", "maccyrillic": "cyrillic",
    "windows-1253": "greek", "cp1253": "greek", "iso-8859-7": "greek",
    "macgreek": "greek",
    "windows-1255": "hebrew", "cp1255": "hebrew", "iso-8859-8": "hebrew",
    "windows-1256": "arabic", "cp1256": "arabic", "iso-8859-6": "arabic",
    "cp862": "hebrew", "cp864": "arabic",
}
# Multibyte guesses are structurally evidenced (a byte cannot decode as UTF-8
# but can as Shift-JIS), so they are believed outright.
_MULTIBYTE_GUESSES = {
    "shift_jis", "cp932", "sjis", "gb2312", "gb18030", "gbk", "big5",
    "euc-jp", "euc-kr", "euc_jp", "euc_kr", "johab", "cp949", "cp950",
    "utf-16", "utf-16-le", "utf-16-be", "utf-32",
}
# Letters that exist in the Central-European codepages (cp1250/iso-8859-2) but
# not in cp1252. Only a real density of these proves a file is cp1250 rather
# than the far more common cp1252, which chardet cannot tell apart.
_CENTRAL_EUROPE_LETTERS = set("ąćęłńśźżĄĆĘŁŃŚŹŻčďěňřšťůžČĎĚŇŘŠŤŮŽ")
_CENTRAL_EUROPE_SHARE = 0.15
# A script guess is only trusted when it accounts for a real share of the
# letters: Western bytes decoded as Hebrew/Arabic yield mostly Latin letters
# plus a few stray marks from the 0x80-0x9F range.
_SCRIPT_SHARE = 0.30


def _decode_with_fallback(raw: bytes) -> str:
    for encoding in _FALLBACK_ENCODINGS:
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "utf-8"


def _letter_share(text: str, predicate) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for char in letters if predicate(char)) / len(letters)


def detect_encoding(raw: bytes) -> str:
    """Best-effort encoding detection, with a chardet-free fallback chain.

    Statistical detection is unreliable for the single-byte Western codepages,
    and its mistakes are silent corruption rather than an error:

    * a cp1252/Excel export is often reported as ``Windows-1250``, turning
      ``naïve`` into ``naďve``;
    * if the file contains curly quotes, chardet may claim ``cp862`` or
      ``Windows-1256``, decoding commas and quotes into spuriously valid Hebrew
      or Arabic letters.

    So the guess is not taken on trust. UTF-8 is verified by decoding; a
    codepage naming a specific script must actually produce that script; a
    Central-European guess must show Central-European letters. Anything left is
    Western and resolved to cp1252.

    The one case this cannot get right is a genuine legacy Mac export, which is
    byte-for-byte indistinguishable from cp1252 here and is read as cp1252.
    That is the right way round: cp1252 sources are far more common, and a Mac
    export can be forced through by re-saving it as UTF-8.
    """
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            pass

    try:
        import chardet

        guess = (chardet.detect(raw) or {}).get("encoding") or ""
    except ImportError:
        guess = ""

    key = guess.lower().replace("_", "-")
    if key in _MULTIBYTE_GUESSES:
        return guess

    script = _GUESS_SCRIPT.get(key)
    if script:
        try:
            ranges = _SCRIPT_RANGES[script]
            share = _letter_share(
                raw.decode(guess),
                lambda char: any(low <= ord(char) <= high for low, high in ranges),
            )
            if share >= _SCRIPT_SHARE:
                return guess
        except (UnicodeDecodeError, LookupError):
            pass

    try:
        raw.decode("cp1252")
    except UnicodeDecodeError:
        return guess or "latin-1"

    if key in ("windows-1250", "cp1250"):
        try:
            if _letter_share(raw.decode(guess), lambda c: c in _CENTRAL_EUROPE_LETTERS) >= _CENTRAL_EUROPE_SHARE:
                return guess
        except (UnicodeDecodeError, LookupError):
            pass

    return "cp1252"


class CSVAdapter(Adapter):
    name = "csv"
    extensions = (".csv", ".txt", ".tsv")

    def read(
        self, source: str | Path | BinaryIO | bytes, extension: str | None = None
    ) -> pd.DataFrame:
        raw = self._as_bytes(source)
        if not raw.strip():
            return pd.DataFrame()
        encoding = detect_encoding(raw)
        suffix = self._extension_of(source, extension)
        separator = "\t" if suffix == ".tsv" else ","
        try:
            frame = pd.read_csv(
                io.BytesIO(raw),
                dtype=str,
                keep_default_na=False,
                encoding=encoding,
                sep=separator,
            )
        except (UnicodeDecodeError, pd.errors.ParserError):
            frame = pd.read_csv(
                io.BytesIO(raw),
                dtype=str,
                keep_default_na=False,
                encoding=encoding,
                sep=separator,
                engine="python",
                on_bad_lines="skip",
            )
        return self._stringify(frame)