"""Assembles a structured PRD-lite draft from extracted transcript items.

The one rule this module never breaks: every bullet it writes carries the real TranscriptLine it
came from (via PRDBullet.source_line), and the bullet's own rendered text always includes that
line's citation marker. There is no code path here that invents a bullet with no real source --
if a section has no matching extracted items, the section says so honestly rather than being
padded with a plausible-sounding guess.
"""
from dataclasses import dataclass

from .extractor import ItemKind


@dataclass(frozen=True)
class PRDBullet:
    text: str            # rendered bullet text, INCLUDING the trailing "[L<n>]" citation
    source_line: object  # the parser.TranscriptLine this bullet is grounded in


@dataclass(frozen=True)
class PRDDraft:
    decisions: list
    requirements: list
    action_items: list
    open_questions: list

    def all_bullets(self):
        return self.decisions + self.requirements + self.action_items + self.open_questions


def _bullet(item):
    return PRDBullet(
        text=f"{item.text} [L{item.source_line.index}]",
        source_line=item.source_line,
    )


def build_prd_draft(extracted_items):
    decisions = [_bullet(i) for i in extracted_items if i.kind == ItemKind.DECISION]
    requirements = [_bullet(i) for i in extracted_items if i.kind == ItemKind.FEATURE_REQUEST]
    open_questions = [_bullet(i) for i in extracted_items if i.kind == ItemKind.OPEN_QUESTION]
    action_items = [
        PRDBullet(
            text=f"{item.speaker}: {item.text} [L{item.source_line.index}]",
            source_line=item.source_line,
        )
        for item in extracted_items if item.kind == ItemKind.ACTION_ITEM
    ]
    return PRDDraft(
        decisions=decisions,
        requirements=requirements,
        action_items=action_items,
        open_questions=open_questions,
    )


def render_markdown(prd_draft, title="Draft PRD — generated from meeting transcript"):
    """Renders the draft as markdown. Every heading that has no real extracted content says so
    explicitly ("No decisions extracted from this transcript") rather than being silently
    omitted or filled with a fabricated placeholder — an empty section is real information (this
    topic wasn't actually discussed), not a gap to paper over."""
    lines = [f"# {title}", ""]

    def section(heading, bullets, empty_note):
        lines.append(f"## {heading}")
        if not bullets:
            lines.append(f"_{empty_note}_")
        else:
            for b in bullets:
                lines.append(f"- {b.text}")
        lines.append("")

    section("Decisions", prd_draft.decisions, "No decisions extracted from this transcript.")
    section("Requirements", prd_draft.requirements,
             "No feature requests extracted from this transcript.")
    section("Action Items", prd_draft.action_items,
             "No action items extracted from this transcript.")
    section("Open Questions", prd_draft.open_questions,
             "No explicitly-open questions extracted from this transcript.")

    lines.append("_Every bullet above cites the transcript line it was extracted from "
                 "(e.g. `[L12]`) — see traceability_check.py for how that citation is verified, "
                 "not just asserted._")
    return "\n".join(lines)
