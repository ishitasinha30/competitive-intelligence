"""Stage 7: Competitor Profiling — Fully Automated"""
import json
from pathlib import Path
from config.settings import STAGE_NAMES, OUTPUTS_DIR
from utils.file_utils import load_all_context, load_json
from utils.claude_client import call_claude_json


PROFILE_AREAS = [
    "company_overview",
    "positioning",
    "target_customer",
    "core_capabilities",
    "workflow_ownership",
    "ai_strategy",
    "integrations",
    "pricing",
    "strengths",
    "weaknesses",
    "customer_complaints",
    "recent_launches",
    "growth_signals",
]


def run() -> dict:
    stage_num = 7
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Building competitor profiles...")
    context = load_all_context()

    scores = load_json("competitor_scores.json") or {}
    scored = scores.get("scored_competitors", [])

    # Profile Tier 1 and 2 in full detail; Tier 3 gets lighter treatment
    tier_summary = scores.get("tier_summary", {})
    priority = set(tier_summary.get("tier_1", []) + tier_summary.get("tier_2", []))

    profiles_dir = Path(OUTPUTS_DIR) / "competitor_profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    all_profiles = {}

    for comp in scored:
        comp_name = comp.get("name", "Unknown")
        is_priority = comp_name in priority
        detail = "comprehensive" if is_priority else "summary"

        print(f"  Profiling: {comp_name} ({detail})...")

        profile = call_claude_json(
            f"""Generate a {'comprehensive' if is_priority else 'concise summary'} competitor profile for: {comp_name}

Profile areas to cover:
{chr(10).join(f'- {a}' for a in (PROFILE_AREAS if is_priority else PROFILE_AREAS[:8]))}

Return a JSON object with:
- name (string)
- tier (from scoring)
- company_overview (object: founded, size, funding, headquarters, stage)
- positioning (object: tagline, primary_value_prop, messaging_angle)
- target_customer (object: icp, buyer, user_persona)
- core_capabilities (array of strings)
- workflow_ownership (object: workflows_owned[], depth_of_ownership, end_to_end_score)
- ai_strategy (object: current_ai_features[], ai_roadmap_signals[], ai_maturity: low/medium/high)
- integrations (array of: {{name, type, criticality}})
- pricing (object: model, tiers[], free_tier, estimated_arpu)
- strengths (array of strings)
- weaknesses (array of strings)
- customer_complaints (array of strings — from reviews/public sources)
- recent_launches (array of: {{feature, date_approx, impact}})
- growth_signals (array of strings)
- competitive_summary (2-3 sentence strategic summary)

Context for scoring: tier={comp.get('tier')}, composite_score={comp.get('composite_score')}""",
            {"product_context": context.get("product_context", {}), "competitor_score": comp},
        )

        all_profiles[comp_name] = profile

        # Save individual profile
        safe_name = comp_name.lower().replace(" ", "_").replace("/", "_")
        profile_path = profiles_dir / f"{safe_name}.json"
        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)

    print(f"\n  Built {len(all_profiles)} profiles")
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return all_profiles
