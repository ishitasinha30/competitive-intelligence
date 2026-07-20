"""Stage 6: Threat Scoring — Mostly Automated"""
from config.settings import STAGE_NAMES
from utils.file_utils import save_json, load_all_context, load_json
from utils.claude_client import call_claude_json


SCORING_DIMENSIONS = {
    "problem_overlap": "How much of the core problem does this solve? (0-10)",
    "workflow_ownership": "How much of the end-to-end workflow does this own? (0-10)",
    "buyer_overlap": "How much does the buyer profile overlap? (0-10)",
    "capability_overlap": "How many key capabilities does this match? (0-10)",
    "ai_capability": "How capable is their AI/automation? (0-10)",
    "market_presence": "How strong is their market presence/brand? (0-10)",
    "ecosystem_strength": "How strong is their integration ecosystem? (0-10)",
    "switching_risk": "How hard would it be for a customer to switch to this? (0-10)",
}

TIERS = {
    "tier_1": "Score 8-10: Active competitive threat, monitor weekly",
    "tier_2": "Score 6-7: Moderate threat, monitor monthly",
    "tier_3": "Score 4-5: Low threat, monitor quarterly",
    "monitor_only": "Score 0-3: Minimal threat, annual review",
}


def run() -> dict:
    stage_num = 6
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Scoring competitive threats...")
    context = load_all_context()
    validated = load_json("validated_competitors.json") or []

    scores = call_claude_json(
        f"""Score each competitor on these threat dimensions (0-10 each):
{chr(10).join(f'- {k}: {v}' for k, v in SCORING_DIMENSIONS.items())}

Tier assignment:
{chr(10).join(f'- {k}: {v}' for k, v in TIERS.items())}

For each competitor return:
- name (string)
- scores (object with each dimension)
- composite_score (weighted average: workflow_ownership x1.5, problem_overlap x1.5, others x1)
- tier (tier_1 / tier_2 / tier_3 / monitor_only)
- tier_rationale (1 sentence)
- time_to_threat (string: "immediate" / "6-12 months" / "1-2 years" / "speculative")
- threat_narrative (2-3 sentences: how specifically this competitor threatens you)
- watch_signals (array of strings: what signals would elevate this competitor's tier)

Return a JSON object:
{{
  "scoring_dimensions": [...],
  "tier_definitions": {{...}},
  "scored_competitors": [...],
  "tier_summary": {{
    "tier_1": [...names...],
    "tier_2": [...names...],
    "tier_3": [...names...],
    "monitor_only": [...names...]
  }}
}}""",
        {"validated_competitors": validated, **context},
    )

    save_json("competitor_scores.json", scores)

    tier_summary = scores.get("tier_summary", {})
    print(f"  Tier 1 (critical): {len(tier_summary.get('tier_1', []))}")
    print(f"  Tier 2 (moderate): {len(tier_summary.get('tier_2', []))}")
    print(f"  Tier 3 (low):      {len(tier_summary.get('tier_3', []))}")
    print(f"  Monitor only:      {len(tier_summary.get('monitor_only', []))}")
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return scores
