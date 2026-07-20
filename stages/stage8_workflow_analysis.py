"""Stage 8: Workflow Ownership Analysis — Human Review Required"""
from config.settings import STAGE_MODES, STAGE_NAMES
from utils.human_gate import gate
from utils.file_utils import save_markdown, load_all_context, load_json
from utils.claude_client import call_claude, strip_code_fence


def run() -> str:
    stage_num = 8
    mode = STAGE_MODES[stage_num]
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Analyzing workflow ownership...")
    context = load_all_context()

    analysis_md = call_claude(
        """Generate a detailed Workflow Ownership Analysis report in markdown.

Structure:
# Workflow Ownership Analysis

## Overview
[2-3 sentence summary of workflow ownership landscape]

## Our Product's Workflow Coverage
[Table: Workflow Step | We Own | Coverage Level (Full/Partial/None) | Notes]

## Competitor Workflow Coverage Matrix
[Table: Workflow Step | [each Tier1+2 competitor] | Notes]
Use ✅ (full), ⚠️ (partial), ❌ (none) symbols.

## Workflow Gaps & Vulnerabilities
[For each gap: what step, who owns it, risk level, recommendation]

## Workflow Expansion Opportunities
[Areas where competitors have expanded their workflow ownership — and whether we should too]

## Key Takeaways
[Bullet points: 3-5 strategic insights from workflow analysis]""",
        context,
    )

    analysis_md = gate(mode, stage_num, name, analysis_md)
    save_markdown("workflow_analysis.md", analysis_md)

    # Generate capability matrix CSV
    cap_matrix = call_claude(
        """Generate a capability comparison matrix in CSV format.
Columns: Capability,Our_Product,[each Tier1+2 competitor name]
Values: Full / Partial / None / Roadmap
Include 20-30 capabilities.
Return ONLY the CSV content, no explanation.""",
        context,
    )
    cap_matrix = strip_code_fence(cap_matrix)

    from pathlib import Path
    from config.settings import OUTPUTS_DIR
    csv_path = Path(OUTPUTS_DIR) / "capability_matrix.csv"
    with open(csv_path, "w") as f:
        f.write(cap_matrix)
    print(f"  Saved → outputs/capability_matrix.csv")

    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return analysis_md
