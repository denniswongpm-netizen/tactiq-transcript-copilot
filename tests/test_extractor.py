import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transcript_copilot.extractor import ItemKind, extract_items
from transcript_copilot.parser import parse_transcript


class ExtractItemsTests(unittest.TestCase):
    def test_extracts_a_decision(self):
        lines = parse_transcript("[00:01] Priya: Let's go with per-project settings.")
        items = extract_items(lines)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].kind, ItemKind.DECISION)

    def test_extracts_an_action_item_with_the_correct_speaker(self):
        lines = parse_transcript("[00:01] Marcus: I'll pull the numbers by tomorrow.")
        items = extract_items(lines)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].kind, ItemKind.ACTION_ITEM)
        self.assertEqual(items[0].speaker, "Marcus")

    def test_extracts_a_feature_request(self):
        lines = parse_transcript("[00:01] Sofia: It would be great if we could add dark mode.")
        items = extract_items(lines)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].kind, ItemKind.FEATURE_REQUEST)

    def test_open_question_is_never_also_counted_as_a_decision(self):
        """The real trap this guards against: 'let's not decide' contains the word 'let's', the
        same word the DECISION pattern 'let's go with' also uses -- a naive check could
        mis-fire."""
        lines = parse_transcript(
            "[00:01] Priya: Good question, let's not decide that today -- flagging it as open."
        )
        items = extract_items(lines)
        kinds = [i.kind for i in items]
        self.assertIn(ItemKind.OPEN_QUESTION, kinds)
        self.assertNotIn(ItemKind.DECISION, kinds)

    def test_a_line_can_match_multiple_categories(self):
        lines = parse_transcript(
            "[00:01] Sofia: Can we add a preview? I'll have a mock by Thursday."
        )
        items = extract_items(lines)
        kinds = {i.kind for i in items}
        self.assertIn(ItemKind.FEATURE_REQUEST, kinds)
        self.assertIn(ItemKind.ACTION_ITEM, kinds)

    def test_ordinary_chatter_extracts_nothing(self):
        lines = parse_transcript("[00:01] Priya: Okay, let's get started with today's agenda.")
        items = extract_items(lines)
        self.assertEqual(items, [])

    def test_every_extracted_item_carries_its_real_source_line(self):
        lines = parse_transcript("[00:05] Marcus: I'll check on that.")
        items = extract_items(lines)
        self.assertEqual(items[0].source_line, lines[0])
        self.assertEqual(items[0].source_line.index, 1)


if __name__ == "__main__":
    unittest.main()
