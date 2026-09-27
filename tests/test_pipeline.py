import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transcript_copilot.pipeline import run_pipeline

SAMPLE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_transcripts", "product_planning_meeting.txt",
)


class RunPipelineTests(unittest.TestCase):
    def test_real_sample_transcript_passes_end_to_end(self):
        result = run_pipeline(SAMPLE)
        self.assertTrue(result.passed, msg=result.issues)
        self.assertEqual(result.issues, [])

    def test_markdown_contains_all_four_sections(self):
        result = run_pipeline(SAMPLE)
        for heading in ("## Decisions", "## Requirements", "## Action Items", "## Open Questions"):
            self.assertIn(heading, result.markdown)

    def test_markdown_bullets_carry_citations(self):
        result = run_pipeline(SAMPLE)
        self.assertIn("[L", result.markdown)

    def test_missing_file_reports_a_clean_failure_not_a_crash(self):
        result = run_pipeline("/nonexistent/path/does-not-exist.txt")
        self.assertFalse(result.passed)
        self.assertTrue(len(result.issues) >= 1)


if __name__ == "__main__":
    unittest.main()
