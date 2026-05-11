"""Stage 9: Replacement Risk Analysis — Human Review Required"""
from config.settings import STAGE_MODES, STAGE_NAMES
from utils.human_gate import gate
from utils.file_utils import save_markdown, load_all_context
from utils.claude_client import call_claude


REPLACEMENT_TYPES = [
    "Direct Product",
    "Platform Expansion",
    "AI Agent",
    "Internal Tooling",
    "Outsourcing",
    "Composite Stack",
    "Workflow Redesign",
]


def run() -> str:
    stage_num = 9
    mode = STAGE_MODES[stage_num]
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Analyzing replacement risks...")
    context = load_all_context()

    risk_md = call_claude(
        f"""Generate a Replacement Risk Analysis report in markdown.

Replacement types to analyze:
{chr(10).join(f'- {r}' for r in REPLACEMENT_TYPES)}

Structure:
# Replacement Risk Analysis

## Executive Summary
[3-4 sentence summary of replacement risk landscape]

## Risk by Replacement Type

For each replacement type, include:
### [Type Name]
- **Risk Level**: High / Medium / Low
- **Key Threat Actors**: [Specific companies/alternatives]
- **Replacement Scenario**: [How exactly this replacement plays out]
- **Trigger Conditions**: [What would accelerate this replacement]
- **Time Horizon**: [When this risk becomes material]
- **Mitigation**: [What we should do to reduce this risk]

## Replacement Risk Matrix
[Table: Replacement Type | Risk Level | Likelihood (1-5) | Impact (1-5) | Risk Score | Primary Actor]

## Highest Priority Replacement Risks
[Top 3 risks ranked, with specific action items]

## Early Warning Signals
[Observable signals that replacement risk is accelerating — what to monitor]""",
        context,
    )

    risk_md = gate(mode, stage_num, name, risk_md)
    save_markdown("replacement_risks.md", risk_md)
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return risk_md
