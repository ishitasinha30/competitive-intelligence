"""Stage 4: Competitor Classification — Fully Automated"""
from config.settings import STAGE_NAMES
from utils.file_utils import save_json, load_all_context
from utils.claude_client import call_claude_json


CLASSIFICATION_DIMENSIONS = [
    "problem_overlap",
    "workflow_overlap",
    "buyer_overlap",
    "user_overlap",
    "capability_overlap",
    "ecosystem_overlap",
    "automation_overlap",
    "ai_overlap",
]


def run() -> dict:
    stage_num = 4
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Classifying competitors across dimensions...")
    context = load_all_context()

    classification = call_claude_json(
        f"""Classify all discovered competitors/alternatives across these overlap dimensions.
Score each dimension 0-10 (0 = no overlap, 10 = identical).

Dimensions:
{chr(10).join(f'- {d}' for d in CLASSIFICATION_DIMENSIONS)}

For each competitor, return:
- name (string)
- category (original discovery category)
- scores (object with each dimension as key, 0-10 score as value)
- overall_overlap_score (average of all dimensions, 0-10)
- overlap_summary (1-2 sentences explaining primary overlap vectors)
- primary_threat_type: one of [
    "direct_substitute", "workflow_expansion", "platform_consolidation",
    "ai_displacement", "diy_replacement", "process_redesign", "ecosystem_lock_in"
  ]
- secondary_threat_types (array)

Return a JSON object:
{{
  "classification_dimensions": [...dimension names...],
  "competitors": [...array of classified competitor objects...]
}}""",
        context,
    )

    save_json("competitor_classification.json", classification)
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return classification
