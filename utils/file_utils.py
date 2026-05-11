import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from config.settings import OUTPUTS_DIR


def save_json(filename: str, data: Union[dict, list]):
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved → outputs/{filename}")
    return path


def save_markdown(filename: str, content: str):
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_DIR / filename
    with open(path, "w") as f:
        f.write(content)
    print(f"  Saved → outputs/{filename}")
    return path


def load_json(filename: str) -> Optional[Union[dict, list]]:
    path = OUTPUTS_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def load_all_context() -> dict:
    """Load all available output files into a single context dict."""
    context = {}
    files = {
        "product_context": "product_context.json",
        "jtbd_map": "jtbd_map.json",
        "workflow_map": "workflow_map.json",
        "capabilities": "capabilities.json",
        "competitors_raw": "competitors_raw.json",
        "competitor_classification": "competitor_classification.json",
        "validated_competitors": "validated_competitors.json",
        "competitor_scores": "competitor_scores.json",
    }
    for key, filename in files.items():
        data = load_json(filename)
        if data:
            context[key] = data
    return context
