import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
INPUTS_DIR = BASE_DIR / "inputs"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Claude model to use
MODEL = "claude-sonnet-5"

# Response token budget. Stages that batch every discovered competitor into
# one call (classification, scoring) scale with however many competitors
# Stage 3 discovers (no upper bound), and were truncating mid-response with
# 40+ of them even after fixing the extended-thinking issue below. The SDK
# client now streams (see _call_via_sdk), which removes the "requires
# streaming for requests over ~10min" ceiling that previously capped this
# at 20000 — 32000 was confirmed accepted by the API (the earlier failure
# at that value was purely the client's non-streaming guard, not a
# server-side rejection). Not live-verified end-to-end past 20000 due to
# the API account running out of credits mid-testing; re-confirm with a
# large (30+) competitor run once credits are available.
MAX_TOKENS = 32000

# Execution modes
MODE_FULLY_AUTOMATED = 1
MODE_HUMAN_REVIEW = 2
MODE_HUMAN_INPUT = 3
MODE_HUMAN_OPTIONAL = 4

# Stage execution modes per spec
STAGE_MODES = {
    1: MODE_HUMAN_INPUT,
    2: MODE_HUMAN_OPTIONAL,
    3: MODE_FULLY_AUTOMATED,
    4: MODE_FULLY_AUTOMATED,
    5: MODE_HUMAN_REVIEW,
    6: MODE_FULLY_AUTOMATED,
    7: MODE_FULLY_AUTOMATED,
    8: MODE_HUMAN_REVIEW,
    9: MODE_HUMAN_REVIEW,
    10: MODE_HUMAN_REVIEW,
    11: MODE_FULLY_AUTOMATED,
    12: MODE_FULLY_AUTOMATED,
}

STAGE_NAMES = {
    1: "Product Context Definition",
    2: "JTBD & Workflow Mapping",
    3: "Competitor Discovery",
    4: "Competitor Classification",
    5: "Competitor Validation",
    6: "Threat Scoring",
    7: "Competitor Profiling",
    8: "Workflow Ownership Analysis",
    9: "Replacement Risk Analysis",
    10: "Strategic Insight Generation",
    11: "Report Generation",
    12: "Continuous Monitoring",
}
