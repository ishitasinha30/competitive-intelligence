"""Stage 3: Competitor Discovery — Fully Automated"""
from config.settings import STAGE_MODES, STAGE_NAMES
from utils.file_utils import save_json, load_all_context
from utils.claude_client import call_claude_json


DISCOVERY_CATEGORIES = [
    "direct_competitors",
    "vertical_competitors",
    "generic_horizontal_platforms",
    "adjacent_workflow_tools",
    "internal_alternatives",
    "composite_competitor_stacks",
    "ai_agent_alternatives",
    "outsourced_service_alternatives",
    "manual_process_alternatives",
]


def run() -> dict:
    stage_num = 3
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Discovering competitors across all categories...")
    context = load_all_context()

    competitors_raw = call_claude_json(
        f"""You are conducting comprehensive competitor discovery for this product.

Remember: competitors are NOT just "companies selling similar software."
A competitor is ANY alternative that helps customers achieve the same desired outcome.

Discover competitors across ALL these categories:
{chr(10).join(f'- {c}' for c in DISCOVERY_CATEGORIES)}

For each competitor/alternative found, include:
- name (string)
- category (one of the categories above)
- description (1-2 sentences)
- website (string or null)
- how_it_competes (string: specifically how it delivers the same outcome)
- target_customer (string)
- pricing_model (string or "unknown")
- ai_enabled (boolean)
- founded_year (int or null)
- funding_stage (string or null)

Return a JSON object where each key is a category name and value is an array of competitor objects.
Include at minimum 3-5 entries per category where applicable. Be thorough — include less obvious alternatives.""",
        context,
    )

    save_json("competitors_raw.json", competitors_raw)
    total = sum(len(v) for v in competitors_raw.values() if isinstance(v, list))
    print(f"  Found {total} alternatives across {len(competitors_raw)} categories")
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return competitors_raw
