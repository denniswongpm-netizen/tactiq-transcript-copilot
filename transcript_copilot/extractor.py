"""Rule-based extraction of decisions, action items, feature requests, and explicitly-open
questions from parsed transcript lines.

Deliberately rule-based, not an LLM call -- this keeps the demo runnable offline with no API key,
and makes the extraction logic itself auditable (you can read every pattern below and know exactly
why something was or wasn't picked up). A production version would likely swap this module for an
LLM-based extractor for better recall on phrasing this doesn't anticipate -- see README.md -- but
every extracted item's `source_line` must still point at a real TranscriptLine either way; that
contract doesn't change with the extraction method.

Every ExtractedItem carries the ORIGINAL TranscriptLine it was extracted from, never just its text
-- so a caller can always cite exactly where a claim came from, and traceability_check.py can
verify it wasn't invented.
"""
import re
from dataclasses import dataclass
from enum import Enum


class ItemKind(str, Enum):
    DECISION = "decision"
    ACTION_ITEM = "action_item"
    FEATURE_REQUEST = "feature_request"
    OPEN_QUESTION = "open_question"


@dataclass(frozen=True)
class ExtractedItem:
    kind: ItemKind
    text: str            # the verbatim sentence/clause the pattern matched on
    speaker: str
    source_line: "object"  # the parser.TranscriptLine this came from -- the citation.


# Order matters: OPEN_QUESTION is checked BEFORE DECISION, so a line like "let's not decide that
# today" is never miscounted as a decision just because it contains "let's" -- an explicit
# non-decision marker takes precedence over a looser decision-shaped phrase in the same sentence.
OPEN_QUESTION_PATTERNS = [
    r"flagging it as open",
    r"let'?s not decide",
    r"need(?:s)? .* input before",
]

DECISION_PATTERNS = [
    r"let'?s go with",
    r"that'?s the decision",
    r"we'?ve decided",
    r"add that to scope",
]

ACTION_ITEM_PATTERNS = [
    r"\bi'?ll\b",
    r"\bi will\b",
]

FEATURE_REQUEST_PATTERNS = [
    r"it would be great if",
    r"\bcan we add\b",
    r"customers? (?:are|is) asking for",
    r"users? (?:are|is) asking for",
    r"feature request",
]


def _matches_any(patterns, text_lower):
    return any(re.search(p, text_lower) for p in patterns)


def extract_items(transcript_lines):
    """Returns a list of ExtractedItem. A single line can match more than one category (e.g. a
    feature request that also contains an action-item commitment in the same breath) -- each
    match is recorded separately rather than picking just one, since collapsing them would lose
    real information a PM would want kept distinct."""
    items = []
    for line in transcript_lines:
        text_lower = line.text.lower()
        if _matches_any(OPEN_QUESTION_PATTERNS, text_lower):
            items.append(ExtractedItem(ItemKind.OPEN_QUESTION, line.text, line.speaker, line))
            continue  # an explicit "not deciding this" line is never also counted as a decision
        if _matches_any(DECISION_PATTERNS, text_lower):
            items.append(ExtractedItem(ItemKind.DECISION, line.text, line.speaker, line))
        if _matches_any(ACTION_ITEM_PATTERNS, text_lower):
            items.append(ExtractedItem(ItemKind.ACTION_ITEM, line.text, line.speaker, line))
        if _matches_any(FEATURE_REQUEST_PATTERNS, text_lower):
            items.append(ExtractedItem(ItemKind.FEATURE_REQUEST, line.text, line.speaker, line))
    return items
