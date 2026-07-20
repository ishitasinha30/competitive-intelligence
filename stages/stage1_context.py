"""Stage 1: Product Context Definition — Human Input Required"""
import json
from pathlib import Path
from config.settings import STAGE_MODES, STAGE_NAMES, MODE_HUMAN_REVIEW
from utils.human_gate import gate
from utils.file_utils import save_json
from utils.claude_client import call_claude_json


def run() -> dict:
    stage_num = 1
    mode = STAGE_MODES[stage_num]
    name = STAGE_NAMES[stage_num]

    # Allow loading from inputs/ if a pre-filled file exists
    inputs_path = Path(__file__).parent.parent / "inputs" / "product_context.json"
    if inputs_path.exists():
        print(f"\n[Stage {stage_num}] Loading context from inputs/product_context.json")
        with open(inputs_path) as f:
            raw = json.load(f)
        context = gate(
            MODE_HUMAN_REVIEW,
            stage_num,
            name,
            raw,
            review_intro=(
                "Product context was loaded from inputs/product_context.json. "
                "Review it before enrichment, or edit / replace as needed."
            ),
            review_accept_prompt="Accept this context? [y]es / [e]dit / [r]eject: ",
        )
    else:
        context = gate(mode, stage_num, name, None)

    # Enrich with Claude: normalize and fill gaps
    print(f"\n[Stage {stage_num}] Enriching context...")
    enriched = call_claude_json(
        f"""Given this product context provided by a human, enrich and normalize it into a clean structured format.
Fill in any obvious gaps with reasonable inferences, but flag them with a "inferred": true field.
Return a JSON object with these fields:
- product_name (string)
- product_description (string, 2-3 sentences)
- business_objective (string)
- icp (object: company_size, industry, role, pain_points[])
- buyer_persona (object: title, goals[], frustrations[])
- user_persona (object: title, daily_jobs[], key_workflows[])
- industry (string)
- known_competitors (array of strings)
- website_url (string or null)
- existing_workflow (string or null)
- key_jtbd_hypothesis (string — what is the core job the product helps with?)
- inferred_fields (array of field names that were inferred, not provided)

Input context:
{json.dumps(context, indent=2)}"""
    )

    save_json("product_context.json", enriched)
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return enriched
