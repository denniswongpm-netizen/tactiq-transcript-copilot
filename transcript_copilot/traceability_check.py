"""Verifies every bullet in a generated PRD draft actually traces back to a real line in the
source transcript -- the mechanical honesty gate for this whole pipeline.

This is deliberately NOT trusting PRDBullet.source_line at face value. A bullet could point at a
TranscriptLine object that was itself correct at generation time but has since drifted (a
different extraction path re-numbered lines, a bullet's text was hand-edited after generation,
etc.) -- so this check re-derives the citation from the bullet's own rendered text (`[L<n>]`) and
looks that line number up fresh in the REAL parsed transcript, then confirms the bullet's claim is
actually a substring of that line's real text. A citation that points at a line number that
doesn't exist, or a bullet whose wording isn't actually present on the cited line, is flagged as
UNTRACEABLE -- the same posture as a resume-content checker refusing to accept a number that
doesn't trace back to an approved source fact.
"""
import re
from dataclasses import dataclass

CITATION_PATTERN = re.compile(r"\[L(\d+)\]\s*$")


@dataclass(frozen=True)
class TraceabilityViolation:
    bullet_text: str
    reason: str


def check_traceability(prd_draft, transcript_lines):
    """Returns a list of TraceabilityViolation -- empty means every bullet in the draft is
    genuinely grounded in the real transcript. Never raises; a malformed bullet is reported as a
    violation, not a crash, since this check must be able to run against ANY generated draft,
    including a deliberately broken one being tested."""
    lines_by_index = {line.index: line for line in transcript_lines}
    violations = []

    for bullet in prd_draft.all_bullets():
        match = CITATION_PATTERN.search(bullet.text)
        if not match:
            violations.append(TraceabilityViolation(
                bullet_text=bullet.text,
                reason="No [L<n>] citation found on this bullet at all.",
            ))
            continue

        cited_index = int(match.group(1))
        real_line = lines_by_index.get(cited_index)
        if real_line is None:
            violations.append(TraceabilityViolation(
                bullet_text=bullet.text,
                reason=f"Cites line {cited_index}, which does not exist in the real transcript.",
            ))
            continue

        claim_text = CITATION_PATTERN.sub("", bullet.text).strip()
        # Action-item bullets are rendered as "Speaker: claim" -- strip that prefix before
        # comparing, since the speaker name itself isn't part of the transcript line's own text.
        if ": " in claim_text and claim_text.split(": ", 1)[0] == real_line.speaker:
            claim_text = claim_text.split(": ", 1)[1]

        if claim_text.lower() not in real_line.text.lower():
            violations.append(TraceabilityViolation(
                bullet_text=bullet.text,
                reason=(
                    f"Cites line {cited_index}, but that line's real text "
                    f"({real_line.text!r}) does not actually contain this claim."
                ),
            ))

    return violations
