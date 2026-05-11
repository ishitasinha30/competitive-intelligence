"""Stage 10: Strategic Insight Generation — Human Approval Required"""
from config.settings import STAGE_MODES, STAGE_NAMES
from utils.human_gate import gate
from utils.file_utils import save_markdown, load_all_context
from utils.claude_client import call_claude


def run() -> str:
    stage_num = 10
    mode = STAGE_MODES[stage_num]
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Generating strategic insights...")
    context = load_all_context()

    insights_md = call_claude(
        """Generate strategic insights from the full competitive intelligence analysis.
These insights inform product, GTM, and company strategy — they must be sharp, specific, and actionable.

Structure:
# Strategic Insights

## Product Insights
[5-7 insights about product direction, gaps, opportunities, and risks]
Format each as:
### [Insight Title]
**Signal**: [What in the competitive data drives this]
**Implication**: [What it means for the product]
**Recommended Action**: [Specific thing to do]
**Priority**: High / Medium / Low
**Owner**: Product / Engineering / Design

## GTM Insights
[4-5 insights about positioning, messaging, sales motion, and competitive differentiation]
Format same as above with Owner: Marketing / Sales / Product Marketing

## Strategic Insights
[3-5 big-picture insights about market position, threats to the business model, and long-term plays]
Format same as above with Owner: CEO / CPO / CRO

## Competitive Moats to Build
[3-5 specific defensible advantages to invest in, based on competitor weaknesses and workflow gaps]

## What NOT to Build
[2-3 things competitors are investing in that we should deliberately avoid — with rationale]

## 90-Day Competitive Action Plan
[Prioritized list of 5-10 concrete actions to take in the next 90 days]""",
        context,
    )

    insights_md = gate(mode, stage_num, name, insights_md)
    save_markdown("strategic_insights.md", insights_md)
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return insights_md
