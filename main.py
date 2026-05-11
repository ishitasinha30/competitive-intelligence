#!/usr/bin/env python3
"""
Competitive Intelligence Agent
A 12-stage, human-governed, AI-assisted competitive intelligence system.

Usage:
    python main.py                          # Full run, interactive
    python main.py --from-stage 3           # Resume from a specific stage
    python main.py --stages 1,2,3           # Run specific stages only
    python main.py --input inputs/my.json   # Load context from file, skip Stage 1 prompts
    python main.py --auto                   # Skip all optional human gates (stages 2,6)
"""
import argparse
import sys
import os
from pathlib import Path
from typing import List

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import STAGE_NAMES, STAGE_MODES, OUTPUTS_DIR


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         COMPETITIVE INTELLIGENCE AGENT                      ║
║         Human-Governed · AI-Assisted · 12 Stages            ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_stage_map(stages_to_run: List[int]):
    mode_labels = {1: "AUTO", 2: "REVIEW", 3: "INPUT", 4: "OPTIONAL"}
    print("  Stages to run:\n")
    for s in stages_to_run:
        mode = STAGE_MODES[s]
        label = mode_labels[mode]
        marker = "►" if s in stages_to_run else " "
        print(f"  {marker} Stage {s:2d}: {STAGE_NAMES[s]:<40} [{label}]")
    print()


def run_stage(stage_num: int, auto: bool = False) -> bool:
    from config.settings import MODE_HUMAN_OPTIONAL, STAGE_MODES

    if auto and STAGE_MODES[stage_num] == MODE_HUMAN_OPTIONAL:
        # Patch gate to auto-accept in auto mode
        import utils.human_gate as hg
        original_gate = hg.gate

        def auto_gate(mode, *args, **kwargs):
            if mode == MODE_HUMAN_OPTIONAL:
                return kwargs.get("ai_output", args[2] if len(args) > 2 else None)
            return original_gate(mode, *args, **kwargs)

        hg.gate = auto_gate

    try:
        if stage_num == 1:
            from stages.stage1_context import run
        elif stage_num == 2:
            from stages.stage2_jtbd import run
        elif stage_num == 3:
            from stages.stage3_discovery import run
        elif stage_num == 4:
            from stages.stage4_classification import run
        elif stage_num == 5:
            from stages.stage5_validation import run
        elif stage_num == 6:
            from stages.stage6_scoring import run
        elif stage_num == 7:
            from stages.stage7_profiling import run
        elif stage_num == 8:
            from stages.stage8_workflow_analysis import run
        elif stage_num == 9:
            from stages.stage9_replacement_risk import run
        elif stage_num == 10:
            from stages.stage10_insights import run
        elif stage_num == 11:
            from stages.stage11_report import run
        elif stage_num == 12:
            from stages.stage12_monitoring import run
        else:
            print(f"  Unknown stage: {stage_num}")
            return False

        run()
        return True

    except KeyboardInterrupt:
        print(f"\n\n  Interrupted at Stage {stage_num}. Progress saved to outputs/")
        return False
    except Exception as e:
        print(f"\n  ERROR in Stage {stage_num}: {e}")
        raise


def print_backend_info():
    """Show which backend will be used for Claude calls."""
    from utils.claude_client import BACKEND
    if BACKEND == "cli":
        print("  Backend: claude CLI  (no API key needed)\n")
    else:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        masked = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "****"
        print(f"  Backend: Anthropic SDK  (key: {masked})\n")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Competitive Intelligence Agent")
    parser.add_argument("--from-stage", type=int, default=1, help="Resume from stage N")
    parser.add_argument("--stages", type=str, help="Comma-separated list of stages to run (e.g. 1,2,3)")
    parser.add_argument("--input", type=str, help="Path to pre-filled product_context.json")
    parser.add_argument("--auto", action="store_true", help="Auto-accept all optional human gates")
    args = parser.parse_args()

    print_backend_info()

    # Copy input file if provided
    if args.input:
        import shutil
        src = Path(args.input)
        if src.exists():
            dst = Path(__file__).parent / "inputs" / "product_context.json"
            dst.parent.mkdir(exist_ok=True)
            shutil.copy(src, dst)
            print(f"  Loaded input: {src.name}\n")

    # Determine stages to run
    if args.stages:
        stages_to_run = [int(s.strip()) for s in args.stages.split(",")]
    else:
        stages_to_run = list(range(args.from_stage, 13))

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print_stage_map(stages_to_run)

    input("  Press Enter to begin, Ctrl+C to abort...")
    print()

    for stage_num in stages_to_run:
        success = run_stage(stage_num, auto=args.auto)
        if not success:
            print(f"\n  Stopped at Stage {stage_num}. Run with --from-stage {stage_num} to resume.\n")
            sys.exit(1)

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ALL STAGES COMPLETE                                         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print("  Outputs saved to: outputs/")
    print()
    print("  Key files:")
    print("    outputs/final_report.md         — Full competitive intelligence report")
    print("    outputs/strategic_insights.md   — Strategic recommendations")
    print("    outputs/replacement_risks.md    — Replacement risk analysis")
    print("    outputs/workflow_analysis.md    — Workflow ownership analysis")
    print("    outputs/monitoring_playbook.md  — Ongoing monitoring guide")
    print("    outputs/competitor_profiles/    — Individual competitor profiles")
    print("    outputs/capability_matrix.csv   — Capability comparison matrix")
    print()


if __name__ == "__main__":
    main()
