"""transcript_copilot -- turns a raw meeting transcript into a traceable, structured PRD draft.

Every requirement, decision, and action item in the generated draft carries a citation back to
the exact transcript line it came from. A separate check (traceability_check.py) verifies those
citations are real before the draft is considered done -- nothing in the output is allowed to
exist without a verifiable source in the input.
"""
