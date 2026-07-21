"""
Claude client — supports two backends:

1. Claude CLI  (default when ANTHROPIC_API_KEY is not set)
   Uses `claude -p "..."` via subprocess. Works inside Claude Code
   with no API key required — just needs `claude` on PATH.

2. Anthropic SDK  (used when ANTHROPIC_API_KEY is set)
   Direct API access. Works anywhere with a valid key.

Backend is selected automatically at startup; override with:
   CLAUDE_BACKEND=cli   or   CLAUDE_BACKEND=sdk
"""
import json
import os
import re
import subprocess
import sys
from typing import Optional, Union

# ── Backend detection ────────────────────────────────────────────────────────

def _detect_backend() -> str:
    forced = os.environ.get("CLAUDE_BACKEND", "").lower()
    if forced in ("cli", "sdk"):
        return forced
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "sdk"
    # Check if claude CLI is available
    result = subprocess.run(["which", "claude"], capture_output=True)
    if result.returncode == 0:
        return "cli"
    return "sdk"  # will fail loudly if no key either — better than silent


BACKEND = _detect_backend()

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior product manager and competitive intelligence analyst with deep expertise across SaaS, AI products, infrastructure, and vertical software markets.

Your role is to help build rigorous competitive intelligence — not just mapping similar products, but identifying ANY alternative that helps customers achieve the same desired outcome. This includes:
- Direct competitors (similar software)
- Generic horizontal platforms (spreadsheets, Notion, etc.)
- AI agents that could replace specific workflows
- Internal tooling companies might build
- Manual processes or outsourced services
- Composite tool stacks

You think in terms of Jobs To Be Done (JTBD), workflow ownership, and replacement risk — not feature checklists.

Always return valid JSON when asked. Be specific, evidence-based, and strategically sharp."""


# ── CLI backend ───────────────────────────────────────────────────────────────

def _call_via_cli(full_prompt: str) -> str:
    """Call Claude via `claude -p` subprocess (no API key needed)."""
    result = subprocess.run(
        ["claude", "-p", full_prompt],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"claude CLI error (exit {result.returncode}): {err[:500]}")
    return result.stdout.strip()


# ── SDK backend ───────────────────────────────────────────────────────────────

_sdk_client = None


def _get_sdk_client():
    global _sdk_client
    if _sdk_client is None:
        try:
            import anthropic
        except ImportError:
            print("ERROR: anthropic package not installed. Run: pip install anthropic")
            sys.exit(1)
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY not set and claude CLI not found.")
            print("Either: export ANTHROPIC_API_KEY=sk-ant-...")
            print("Or:     install Claude Code so `claude` is on your PATH")
            sys.exit(1)
        _sdk_client = anthropic.Anthropic(api_key=api_key)
    return _sdk_client


def _call_via_sdk(prompt: str, context: Optional[dict], system_override: Optional[str]) -> str:
    client = _get_sdk_client()

    messages = []
    if context:
        context_text = json.dumps(context, indent=2)
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Here is the current competitive intelligence context:\n\n```json\n{context_text}\n```",
                    "cache_control": {"type": "ephemeral"},
                },
                {"type": "text", "text": prompt},
            ],
        })
    else:
        messages.append({"role": "user", "content": prompt})

    from config.settings import MODEL, MAX_TOKENS
    # Stream instead of a plain create() call. Stages that batch every
    # discovered competitor into one call (classification, scoring) scale
    # with however many Stage 3 finds (no upper bound), and a non-streaming
    # request errors out once the API estimates it could take >10 minutes —
    # which large max_tokens values can trigger well before actually being
    # needed. Streaming removes that ceiling so MAX_TOKENS can be set high
    # enough to not truncate large real runs.
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        # These calls are structured extraction/synthesis, not multi-step
        # reasoning — extended thinking was silently eating a third of the
        # output budget (thinking tokens count against max_tokens) and
        # truncating large JSON responses mid-string.
        thinking={"type": "disabled"},
        system=[
            {
                "type": "text",
                "text": system_override or SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=messages,
    ) as stream:
        response = stream.get_final_message()
    for block in response.content:
        if block.type == "text":
            return block.text
    raise RuntimeError(f"No text block in Claude response: {response.content!r}")


# ── Public interface ──────────────────────────────────────────────────────────

def call_claude(
    prompt: str,
    context: Optional[dict] = None,
    system_override: Optional[str] = None,
) -> str:
    if BACKEND == "cli":
        parts = [system_override or SYSTEM_PROMPT]
        if context:
            parts.append(
                f"Here is the current competitive intelligence context:\n\n"
                f"```json\n{json.dumps(context, indent=2)}\n```"
            )
        parts.append(prompt)
        return _call_via_cli("\n\n".join(parts))
    else:
        return _call_via_sdk(prompt, context, system_override)


_FENCE_RE = re.compile(r"^```[a-zA-Z0-9]*\n?(.*?)\n?```\s*$", re.DOTALL)


def strip_code_fence(text: str) -> str:
    """Strip a single leading/trailing markdown code fence, if the whole
    response is wrapped in one. Leaves the text untouched otherwise —
    safe even if the content itself contains ``` sequences."""
    text = text.strip()
    match = _FENCE_RE.match(text)
    return match.group(1).strip() if match else text


def call_claude_json(prompt: str, context: Optional[dict] = None) -> Union[dict, list]:
    full_prompt = prompt + "\n\nReturn ONLY valid JSON. No markdown fences, no explanation."
    raw = call_claude(full_prompt, context)
    try:
        return json.loads(strip_code_fence(raw))
    except json.JSONDecodeError as e:
        # LLM output occasionally comes back malformed — one retry with the
        # parse error attached is usually enough to get valid JSON back.
        retry_raw = call_claude(
            full_prompt + f"\n\nYour previous response failed to parse as JSON ({e}). "
            f"Return the corrected JSON only.",
            context,
        )
        try:
            return json.loads(strip_code_fence(retry_raw))
        except json.JSONDecodeError as e2:
            raise RuntimeError(
                f"Model did not return valid JSON after a retry: {e2}\nRaw response:\n{retry_raw[:1000]}"
            ) from e2
