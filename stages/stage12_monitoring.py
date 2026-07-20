"""Stage 12: Continuous Monitoring Setup — Fully Automated"""
from config.settings import STAGE_NAMES
from utils.file_utils import save_json, save_markdown, load_all_context, load_json
from utils.claude_client import call_claude_json, call_claude


MONITORING_SIGNALS = [
    "Product Launches",
    "Pricing Changes",
    "AI Announcements",
    "New Integrations",
    "Funding Rounds",
    "Key Hiring (roles signal strategy)",
    "Messaging Changes",
    "Customer Reviews",
    "Partnership Announcements",
    "Open Source Activity",
]


def run() -> dict:
    stage_num = 12
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Setting up continuous monitoring plan...")
    context = load_all_context()

    scores = load_json("competitor_scores.json") or {}
    tier_summary = scores.get("tier_summary", {})
    tier1 = tier_summary.get("tier_1", [])
    tier2 = tier_summary.get("tier_2", [])
    tier3 = tier_summary.get("tier_3", [])

    monitoring_plan = call_claude_json(
        f"""Create a continuous monitoring plan for these competitors.

Monitoring signals to track:
{chr(10).join(f'- {s}' for s in MONITORING_SIGNALS)}

Monitoring cadence by tier:
- Tier 1: Weekly
- Tier 2: Monthly
- Tier 3: Quarterly
- Monitor Only: Semi-annually

For each competitor to monitor, return:
- name (string)
- tier (string)
- monitoring_cadence (string)
- watch_signals (array of strings — specific things to look for)
- tracking_sources (array of: {{source, url_pattern, signal_type}})
- alert_conditions (array of strings — what would trigger immediate review)
- confidence_baseline (object: {{positioning, pricing, capabilities, ai_strategy}} — current confidence 0-10)
- last_updated (string: today's date)

Also include:
- "monitoring_dashboard" (object with suggested metrics to track weekly)
- "quarterly_review_checklist" (array of review questions)
- "escalation_criteria" (array of conditions that should trigger full re-analysis)

Return as JSON object with "competitors" array and the above additional fields.""",
        {
            "tier1": tier1,
            "tier2": tier2,
            "tier3": tier3,
            "product_context": context.get("product_context", {}),
        },
    )

    save_json("monitoring_plan.json", monitoring_plan)

    # Generate markdown monitoring brief
    monitoring_md = call_claude(
        """Generate a Monitoring Brief in markdown that a team member can run each week.

Include:
# Competitive Monitoring Playbook

## Weekly Check (Tier 1 Competitors)
[Checklist format — what to check, where, and what to do with findings]

## Monthly Check (Tier 2 Competitors)
[Checklist format]

## Sources & Tools
[List of sources to check: G2, Capterra, LinkedIn, company blogs, GitHub, job boards, etc.]

## How to Log Findings
[Simple template for logging a new competitive signal]

## Escalation Protocol
[When and how to escalate a finding to the team]""",
        {
            "monitoring_plan": monitoring_plan,
            "product_context": context.get("product_context", {}),
        },
    )

    save_markdown("monitoring_playbook.md", monitoring_md)

    competitors_monitored = len(monitoring_plan.get("competitors", []))
    print(f"  Monitoring plan set up for {competitors_monitored} competitors")
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return monitoring_plan
