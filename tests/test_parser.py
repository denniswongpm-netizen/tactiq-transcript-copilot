import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transcript_copilot.parser import parse_transcript, parse_transcript_file

SAMPLE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_transcripts", "product_planning_meeting.txt",
)


class ParseTranscriptTests(unittest.TestCase):
    def test_parses_well_formed_lines(self):
        raw = "[00:01] Alice: Hello there\n[00:02] Bob: Hi Alice"
        lines = parse_transcript(raw)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].timestamp, "00:01")
        self.assertEqual(lines[0].speaker, "Alice")
        self.assertEqual(lines[0].text, "Hello there")
        self.assertEqual(lines[1].speaker, "Bob")

    def test_skips_unparseable_lines(self):
        raw = "[Fictional example transcript]\n\n[00:01] Alice: Real line"
        lines = parse_transcript(raw)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text, "Real line")

    def test_index_is_the_real_1_based_file_line_number_not_a_position_counter(self):
        raw = "[not a real line]\n[00:01] Alice: First real utterance"
        lines = parse_transcript(raw)
        self.assertEqual(lines[0].index, 2)  # line 2 in the file, not position 0

    def test_speaker_with_surrounding_whitespace_is_trimmed(self):
        raw = "[00:01]   Alice  :   spaced out text  "
        lines = parse_transcript(raw)
        self.assertEqual(lines[0].speaker, "Alice")
        self.assertEqual(lines[0].text, "spaced out text")

    def test_empty_transcript_returns_empty_list(self):
        self.assertEqual(parse_transcript(""), [])

    def test_parses_the_real_sample_file(self):
        lines = parse_transcript_file(SAMPLE)
        self.assertGreater(len(lines), 10)
        self.assertTrue(all(line.speaker in ("Priya", "Marcus", "Sofia") for line in lines))


if __name__ == "__main__":
    unittest.main()
