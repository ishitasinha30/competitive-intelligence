# Competitive Intelligence Agent

A 12-stage, human-governed, AI-assisted competitive intelligence system. Built to analyze **any** alternative that helps customers achieve the same desired outcome — not just similar software.

## Core Philosophy

> Competition is not limited to similar products. It includes platforms, AI agents, workflows, internal tooling, operational redesign, outsourcing, and composite ecosystems.

## Setup

The agent supports two backends — pick whichever fits your environment:

### Option A: Claude Code (no API key needed)
If you have [Claude Code](https://claude.ai/code) installed, the agent uses the `claude` CLI automatically. No key required.

```bash
pip install -r requirements.txt
python main.py --input inputs/example_saas_product.json --auto
```

### Option B: Anthropic API key
Works anywhere without Claude Code installed.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # get one at console.anthropic.com
python main.py --input inputs/example_saas_product.json --auto
```

The backend is detected automatically: API key takes priority; falls back to `claude` CLI if no key is set.

## Usage

### Interactive run (prompts for product context)
```bash
python main.py
```

### Load from input file (skip Stage 1 prompts)
```bash
python main.py --input inputs/example_saas_product.json
python main.py --input inputs/example_fintech.json
python main.py --input inputs/example_vertical_saas.json
```

### Resume from a specific stage
```bash
python main.py --from-stage 5
```

### Run specific stages only
```bash
python main.py --stages 3,4,6
```

### Auto-accept all optional human gates
```bash
python main.py --input inputs/example_saas_product.json --auto
```

## The 12 Stages

| Stage | Name | Mode |
|-------|------|------|
| 1 | Product Context Definition | Human Input Required |
| 2 | JTBD & Workflow Mapping | Human Optional |
| 3 | Competitor Discovery | Fully Automated |
| 4 | Competitor Classification | Fully Automated |
| 5 | Competitor Validation | Human Review |
| 6 | Threat Scoring | Fully Automated |
| 7 | Competitor Profiling | Fully Automated |
| 8 | Workflow Ownership Analysis | Human Review |
| 9 | Replacement Risk Analysis | Human Review |
| 10 | Strategic Insight Generation | Human Approval |
| 11 | Report Generation | Fully Automated |
| 12 | Continuous Monitoring Setup | Fully Automated |

## Execution Modes

- **Fully Automated** — AI executes without pausing
- **Human Optional** — AI completes work, you may edit before continuing
- **Human Review Required** — You must accept, edit, or reject AI output
- **Human Input Required** — Workflow cannot continue without your input

## Outputs

All outputs are saved to `outputs/`:

```
outputs/
├── product_context.json          # Enriched product definition
├── jtbd_map.json                 # Jobs To Be Done map
├── workflow_map.json             # End-to-end workflow map
├── capabilities.json             # Capability map
├── competitors_raw.json          # Raw discovery (all categories)
├── competitor_classification.json
├── validated_competitors.json
├── competitor_scores.json        # Threat tiers + scores
├── competitor_profiles/          # Individual profiles (JSON)
├── workflow_analysis.md          # Workflow ownership report
├── capability_matrix.csv         # Capability comparison
├── replacement_risks.md          # Replacement risk analysis
├── strategic_insights.md         # Strategic recommendations
├── final_report.md               # Full CI report
├── monitoring_plan.json          # Monitoring configuration
└── monitoring_playbook.md        # Weekly monitoring guide
```

## Competitor Discovery Categories

1. Direct Competitors
2. Vertical Competitors
3. Generic Horizontal Platforms
4. Adjacent Workflow Tools
5. Internal Alternatives
6. Composite Competitor Stacks
7. AI Agent Alternatives
8. Outsourced Service Alternatives
9. Manual Process Alternatives

## Threat Scoring Dimensions

- Problem Overlap (1.5x weight)
- Workflow Ownership (1.5x weight)
- Buyer Overlap
- Capability Overlap
- AI Capability
- Market Presence
- Ecosystem Strength
- Switching Risk

## Example Inputs

See `inputs/` for example product contexts across industries:
- `example_saas_product.json` — Dev tools / project management
- `example_fintech.json` — Finance operations
- `example_vertical_saas.json` — Veterinary practice management
