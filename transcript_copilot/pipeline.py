"""Orchestrates the full transcript -> PRD draft flow, and reports the result the same way as
every other check in this codebase: `passed` plus a list of concrete `issues`, never a bare
pass/fail with no explanation of what's wrong.
"""
import sys
from dataclasses import dataclass

from .extractor import extract_items
from .parser import parse_transcript_file
from .prd_builder import build_prd_draft, render_markdown
from .traceability_check import check_traceability


@dataclass
class PipelineResult:
    passed: bool
    markdown: str
    issues: list  # list of str, human-readable -- empty when passed=True


def run_pipeline(transcript_path):
    try:
        transcript_lines = parse_transcript_file(transcript_path)
    except OSError as exc:
        return PipelineResult(
            passed=False, markdown="",
            issues=[f"Could not read {transcript_path!r}: {exc}"],
        )
    if not transcript_lines:
        return PipelineResult(
            passed=False, markdown="",
            issues=[f"No parseable transcript lines found in {transcript_path!r} -- check the "
                    f"'[HH:MM] Speaker: text' format."],
        )

    extracted_items = extract_items(transcript_lines)
    prd_draft = build_prd_draft(extracted_items)
    violations = check_traceability(prd_draft, transcript_lines)

    issues = [f"UNTRACEABLE: {v.bullet_text} -- {v.reason}" for v in violations]
    markdown = render_markdown(prd_draft)
    return PipelineResult(passed=not issues, markdown=markdown, issues=issues)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 -m transcript_copilot.pipeline <transcript_path>", file=sys.stderr)
        sys.exit(1)

    result = run_pipeline(sys.argv[1])
    print(result.markdown)
    print()
    if result.passed:
        print("✅ Traceability check passed — every bullet above cites a real transcript line.")
    else:
        print("❌ Traceability check FAILED:")
        for issue in result.issues:
            print(f"  - {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
