import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transcript_copilot.extractor import extract_items
from transcript_copilot.parser import parse_transcript
from transcript_copilot.prd_builder import PRDBullet, PRDDraft, build_prd_draft
from transcript_copilot.traceability_check import check_traceability

TRANSCRIPT = (
    "[00:01] Priya: Let's go with per-project settings.\n"
    "[00:02] Marcus: I'll pull the numbers by tomorrow.\n"
    "[00:03] Sofia: It would be great if we could add dark mode.\n"
)


class CheckTraceabilityTests(unittest.TestCase):
    def test_a_genuinely_built_prd_draft_passes_clean(self):
        """The real, load-bearing case: a PRD draft built the normal way (extract -> build) from
        a real transcript must never fail its own traceability check -- if it did, this check
        would be useless (either too strict to ever pass real output, or the builder itself would
        be broken)."""
        lines = parse_transcript(TRANSCRIPT)
        draft = build_prd_draft(extract_items(lines))
        violations = check_traceability(draft, lines)
        self.assertEqual(violations, [])

    def test_catches_a_bullet_citing_a_line_that_does_not_exist(self):
        """The core hallucination scenario this whole module exists to catch: a generated bullet
        pointing at a citation number that was never actually in the source transcript."""
        lines = parse_transcript(TRANSCRIPT)
        fabricated = PRDDraft(
            decisions=[PRDBullet(text="We will 10x revenue this quarter. [L99]", source_line=None)],
            requirements=[], action_items=[], open_questions=[],
        )
        violations = check_traceability(fabricated, lines)
        self.assertEqual(len(violations), 1)
        self.assertIn("does not exist", violations[0].reason)

    def test_catches_a_bullet_whose_wording_is_not_actually_on_the_cited_line(self):
        """A subtler hallucination: the citation POINTS at a real line, but the bullet's actual
        claim was never said on that line -- e.g. an LLM extractor embellishing a real utterance
        with something nobody actually said."""
        lines = parse_transcript(TRANSCRIPT)
        fabricated = PRDDraft(
            decisions=[PRDBullet(
                text="Let's go with per-project settings AND guarantee 99.99% uptime. [L1]",
                source_line=lines[0],
            )],
            requirements=[], action_items=[], open_questions=[],
        )
        violations = check_traceability(fabricated, lines)
        self.assertEqual(len(violations), 1)
        self.assertIn("does not actually contain this claim", violations[0].reason)

    def test_bullet_with_no_citation_at_all_is_flagged(self):
        lines = parse_transcript(TRANSCRIPT)
        fabricated = PRDDraft(
            decisions=[PRDBullet(text="Some claim with no citation marker at all.", source_line=None)],
            requirements=[], action_items=[], open_questions=[],
        )
        violations = check_traceability(fabricated, lines)
        self.assertEqual(len(violations), 1)
        self.assertIn("No [L<n>] citation", violations[0].reason)

    def test_action_item_speaker_prefix_is_correctly_stripped_before_comparison(self):
        lines = parse_transcript(TRANSCRIPT)
        draft = build_prd_draft(extract_items(lines))
        self.assertTrue(any(b.text.startswith("Marcus:") for b in draft.action_items))
        # Already covered by the clean-pass test above, but assert explicitly here too since this
        # is the one bullet type with a speaker prefix baked into its rendered text.
        violations = check_traceability(draft, lines)
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
