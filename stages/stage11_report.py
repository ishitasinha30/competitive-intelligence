"""Stage 11: Report Generation — Fully Automated"""
import json
from pathlib import Path
from datetime import date
from config.settings import STAGE_MODES, STAGE_NAMES, OUTPUTS_DIR
from utils.file_utils import save_markdown, load_all_context, load_json
from utils.claude_client import call_claude


def run() -> str:
    stage_num = 11
    name = STAGE_NAMES[stage_num]

    print(f"\n[Stage {stage_num}] Generating final report...")
    context = load_all_context()

    product = context.get("product_context", {})
    product_name = product.get("product_name", "Product")
    today = date.today().strftime("%B %d, %Y")

    scores = load_json("competitor_scores.json") or {}
    tier_summary = scores.get("tier_summary", {})
    scored = scores.get("scored_competitors", [])

    # Read supplementary reports
    def read_output(filename: str) -> str:
        path = Path(OUTPUTS_DIR) / filename
        return path.read_text() if path.exists() else ""

    workflow_analysis = read_output("workflow_analysis.md")
    replacement_risks = read_output("replacement_risks.md")
    strategic_insights = read_output("strategic_insights.md")

    # Build threat summary table
    tier1 = tier_summary.get("tier_1", [])
    tier2 = tier_summary.get("tier_2", [])

    threat_rows = ""
    for c in scored:
        name = c.get("name", "Unknown")
        if name in tier1 + tier2:
            threat_rows += f"| {name} | {c.get('tier', '')} | {c.get('composite_score', 0):.1f} | {c.get('time_to_threat', '')} | {c.get('tier_rationale', '')} |\n"

    report_intro = call_claude(
        f"""Write the executive summary section of a competitive intelligence report for {product_name}.

Context from this analysis:
- Tier 1 competitors (critical): {tier1}
- Tier 2 competitors (moderate): {tier2}
- Total alternatives discovered: {sum(len(v) for v in load_json('competitors_raw.json', ).values() if isinstance(v, list)) if load_json('competitors_raw.json') else 'N/A'}

Write:
1. A 3-4 paragraph executive summary covering: market landscape, primary threats, key vulnerabilities, strategic opportunity
2. A "Key Findings" section with 5-7 bullet points
3. A "How to Read This Report" section (2-3 sentences)

Be direct, specific, and strategically sharp. No filler language.""",
        context,
    )

    report = f"""# Competitive Intelligence Report: {product_name}
**Generated:** {today}
**Classification:** Internal — Product & Strategy

---

{report_intro}

---

## Threat Summary

| Competitor | Tier | Score | Time to Threat | Rationale |
|------------|------|-------|----------------|-----------|
{threat_rows}

---

{workflow_analysis}

---

{replacement_risks}

---

{strategic_insights}

---

## Appendix

### Methodology
This report was generated using a 12-stage competitive intelligence workflow. Competitors are defined as any alternative that helps customers achieve the same desired outcome — including direct products, platform expansions, AI agents, internal tooling, manual processes, and composite tool stacks.

### Confidence & Limitations
- Competitor profiles are based on publicly available information and AI synthesis
- Pricing data may be outdated; verify before using in sales contexts
- Strategic insights require human validation before acting on them
- This report should be refreshed quarterly or when major market events occur

### Full Data
Raw data files are available in the `outputs/` directory:
- `product_context.json` — Product definition
- `jtbd_map.json` — Jobs To Be Done map
- `workflow_map.json` — End-to-end workflow
- `competitor_scores.json` — Full scoring data
- `competitor_profiles/` — Individual competitor profiles
- `capability_matrix.csv` — Full capability comparison
"""

    save_markdown("final_report.md", report)
    print(f"\n[Stage {stage_num}] ✓ Complete\n")
    return report
