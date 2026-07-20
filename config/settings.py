import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
INPUTS_DIR = BASE_DIR / "inputs"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Claude model to use
MODEL = "claude-sonnet-5"

# Response token budget. Some stages (e.g. discovery, profiling) ask for
# large structured JSON and were getting truncated mid-response at 8192.
# Stay below ~20k here — the SDK requires streaming for requests estimated
# to take longer than 10 minutes, which max_tokens above that can trigger.
MAX_TOKENS = 16000

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
