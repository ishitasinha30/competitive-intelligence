"""Stage 2: JTBD & Workflow Mapping — Human Optional"""
from config.settings import STAGE_MODES, STAGE_NAMES
from utils.human_gate import gate
from utils.file_utils import save_json, load_all_context
from utils.claude_client import call_claude_json


def run() -> dict:
    stage_num = 2
    mode = STAGE_MODES[stage_num]
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Generating JTBD & workflow maps...")
    context = load_all_context()

    jtbd_map = call_claude_json(
        """Based on the product context, generate a comprehensive Jobs To Be Done (JTBD) map.
Return a JSON object with:
- core_job (string: the primary functional job)
- functional_jobs (array of objects: {job, when, so_that, current_solution})
- emotional_jobs (array of strings)
- social_jobs (array of strings)
- job_stages (array: {stage, description, pain_points[], desired_outcomes[]})
- underserved_jobs (array of strings — jobs poorly served by current solutions)""",
        context,
    )

    workflow_map = call_claude_json(
        """Based on the product context, map the end-to-end workflow this product supports.
Use the Universal Workflow Model: Input → Processing → Decision → Action → Outcome → Reporting

Return a JSON object with:
- workflow_name (string)
- trigger (string: what initiates the workflow)
- steps (array of: {phase, step_name, description, actor, tool_used, pain_points[], time_estimate})
- decision_points (array of: {point, options[], criteria})
- outcomes (array of: {outcome, success_metric, frequency})
- reporting_needs (array of strings)
- automation_opportunities (array of strings)""",
        context,
    )

    capabilities = call_claude_json(
        """Based on the product context and workflow, map the product's core capabilities.
Return a JSON object with:
- capability_areas (array of: {area, capabilities[], workflows_owned[], differentiators[]})
- workflow_ownership_score (0-100: % of workflow the product owns end-to-end)
- integration_surface (array of: {tool, relationship, criticality})
- ai_capabilities (array of strings — current or potential AI features)
- gaps (array of strings — capabilities missing from current product)""",
        context,
    )

    jtbd_map = gate(mode, stage_num, name, jtbd_map)
    save_json("jtbd_map.json", jtbd_map)
    save_json("workflow_map.json", workflow_map)
    save_json("capabilities.json", capabilities)

    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return {"jtbd_map": jtbd_map, "workflow_map": workflow_map, "capabilities": capabilities}
