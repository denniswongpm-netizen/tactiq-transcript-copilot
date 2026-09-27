"""Parses a plain-text meeting transcript into structured, addressable lines.

Expected format, one utterance per line: "[HH:MM] Speaker: text" -- the same shape a tool like
Tactiq exports. Lines that don't match (blank lines, a leading bracketed note) are skipped, never
guessed at.
"""
import re
from dataclasses import dataclass

LINE_PATTERN = re.compile(r"^\[(?P<timestamp>\d{2}:\d{2})\]\s*(?P<speaker>[^:]+):\s*(?P<text>.+)$")


@dataclass(frozen=True)
class TranscriptLine:
    index: int          # 1-based line number in the ORIGINAL file -- the citation key everything
                         # downstream points back to.
    timestamp: str
    speaker: str
    text: str


def parse_transcript(raw_text):
    """Returns a list of TranscriptLine, in original file order. `index` is the real line number
    in the source file (1-based), not a re-numbered position -- this is what lets a citation
    ("this claim came from line 12") be checked against the actual file later, not just against
    an in-memory list that could silently drift out of sync with it."""
    lines = []
    for line_number, raw_line in enumerate(raw_text.splitlines(), start=1):
        match = LINE_PATTERN.match(raw_line.strip())
        if not match:
            continue
        lines.append(TranscriptLine(
            index=line_number,
            timestamp=match.group("timestamp"),
            speaker=match.group("speaker").strip(),
            text=match.group("text").strip(),
        ))
    return lines


def parse_transcript_file(path):
    with open(path, encoding="utf-8") as f:
        return parse_transcript(f.read())
