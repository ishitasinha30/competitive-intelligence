"""Stage 5: Competitor Validation — Human Review Required"""
from config.settings import STAGE_MODES, STAGE_NAMES
from utils.human_gate import gate
from utils.file_utils import save_json, load_all_context, load_json
from utils.claude_client import call_claude_json


def run() -> dict:
    stage_num = 5
    mode = STAGE_MODES[stage_num]
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Preparing competitor list for validation...")
    context = load_all_context()

    # Build a summary view for human review
    classification = load_json("competitor_classification.json") or {}
    competitors = classification.get("competitors", [])

    print(f"\n  Found {len(competitors)} alternatives to validate.")
    print("  Top competitors by overlap score:\n")
    sorted_comps = sorted(competitors, key=lambda x: x.get("overall_overlap_score", 0), reverse=True)
    for c in sorted_comps[:10]:
        score = c.get("overall_overlap_score", 0)
        threat = c.get("primary_threat_type", "unknown")
        print(f"    {c['name']:<30} Score: {score:.1f}/10  Type: {threat}")

    print(f"\n  (Full list: {len(competitors)} competitors)")

    validated = gate(mode, stage_num, name, competitors)

    # If human accepted without changes, still ask Claude to flag any they'd remove
    if validated == competitors:
        filtered = call_claude_json(
            """Review this competitor list and remove any entries that are:
- Not actually relevant to the product context
- Duplicates (keep the more detailed entry)
- Too niche to warrant tracking

Return the filtered list as a JSON array with the same structure.
Add a "validation_note" field to any competitor you flag as borderline.""",
            {"competitors": competitors, "product_context": context.get("product_context", {})},
        )
    else:
        filtered = validated

    save_json("validated_competitors.json", filtered)
    print(f"\n  Validated {len(filtered)} competitors")
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return filtered
