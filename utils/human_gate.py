import json
from typing import Any, Union, Optional
from config.settings import (
    MODE_FULLY_AUTOMATED,
    MODE_HUMAN_REVIEW,
    MODE_HUMAN_INPUT,
    MODE_HUMAN_OPTIONAL,
)


def _print_divider(char: str = "─", width: int = 60):
    print(char * width)


def gate(
    mode: int,
    stage_num: int,
    stage_name: str,
    ai_output: Any,
    prompt: str = "",
    review_intro: Optional[str] = None,
    review_accept_prompt: Optional[str] = None,
) -> Any:
    """
    Handles human checkpoint logic based on execution mode.
    Returns (possibly edited) output to continue with.
    """
    if mode == MODE_FULLY_AUTOMATED:
        return ai_output

    _print_divider("═")
    print(f"  STAGE {stage_num}: {stage_name}")
    _print_divider("═")

    if mode == MODE_HUMAN_INPUT:
        return _handle_human_input(stage_name, prompt)

    if mode == MODE_HUMAN_REVIEW:
        return _handle_human_review(
            ai_output,
            intro=review_intro,
            accept_prompt=review_accept_prompt,
        )

    if mode == MODE_HUMAN_OPTIONAL:
        return _handle_human_optional(ai_output)

    return ai_output


def _handle_human_input(stage_name: str, prompt: str) -> dict:
    print(f"\n[INPUT REQUIRED] {stage_name} needs your input to proceed.\n")
    if prompt:
        print(prompt)
    print()

    fields = {
        "product_name": "Product Name",
        "product_description": "Product Description (what it does, who it's for)",
        "business_objective": "Primary Business Objective",
        "icp": "Ideal Customer Profile (ICP)",
        "buyer_persona": "Buyer Persona",
        "user_persona": "User Persona",
        "industry": "Industry / Market",
        "known_competitors": "Known Competitors (comma-separated, optional)",
        "website_url": "Website URL (optional)",
        "existing_workflow": "Existing Workflow Description (optional)",
    }

    context = {}
    for key, label in fields.items():
        val = input(f"  {label}: ").strip()
        if val:
            if key == "known_competitors" and val:
                context[key] = [c.strip() for c in val.split(",") if c.strip()]
            else:
                context[key] = val

    return context


def _handle_human_review(
    ai_output: Any,
    *,
    intro: Optional[str] = None,
    accept_prompt: Optional[str] = None,
) -> Any:
    output_str = json.dumps(ai_output, indent=2) if not isinstance(ai_output, str) else ai_output
    if intro:
        print(f"\n[REVIEW REQUIRED] {intro}\n")
    else:
        print("\n[REVIEW REQUIRED] AI has completed this stage. Please review:\n")
    print(output_str[:3000])
    if len(output_str) > 3000:
        print(f"\n... (truncated, {len(output_str)} chars total)")
    print()

    accept_line = accept_prompt or "Accept AI output? [y]es / [e]dit / [r]eject: "
    while True:
        choice = input(f"  {accept_line}").strip().lower()
        if choice in ("y", "yes", ""):
            print("  ✓ Accepted\n")
            return ai_output
        elif choice in ("e", "edit"):
            print("  Paste your edited JSON (end with a line containing only '---'):")
            lines = []
            while True:
                line = input()
                if line == "---":
                    break
                lines.append(line)
            try:
                return json.loads("\n".join(lines))
            except json.JSONDecodeError:
                return "\n".join(lines)
        elif choice in ("r", "reject"):
            print("  Stage output rejected. Please provide replacement content:")
            lines = []
            while True:
                line = input()
                if line == "---":
                    break
                lines.append(line)
            try:
                return json.loads("\n".join(lines))
            except json.JSONDecodeError:
                return "\n".join(lines)


def _handle_human_optional(ai_output: Any) -> Any:
    output_str = json.dumps(ai_output, indent=2) if not isinstance(ai_output, str) else ai_output
    print("\n[OPTIONAL REVIEW] AI output ready. You may edit or proceed:\n")
    print(output_str[:2000])
    if len(output_str) > 2000:
        print(f"\n... (truncated, {len(output_str)} chars total)")
    print()

    choice = input("  Proceed with AI output? [Y]es / [e]dit: ").strip().lower()
    if choice in ("e", "edit"):
        return _handle_human_review(ai_output, intro=None, accept_prompt=None)
    return ai_output
