# ceoparkmake/game/content_loader.py

import json
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _read_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def load_ranks() -> List[Dict[str, Any]]:
    obj = _read_json(DATA_DIR / "ranks.json", {"ranks": []})
    ranks = obj.get("ranks", [])
    return ranks if isinstance(ranks, list) else []


def load_dialogue_events() -> List[Dict[str, Any]]:
    obj = _read_json(DATA_DIR / "events_dialogue.json", {"events": []})
    events = obj.get("events", [])
    return events if isinstance(events, list) else []


def load_adventure_events() -> List[Dict[str, Any]]:
    obj = _read_json(DATA_DIR / "events_adventure.json", {"events": []})
    events = obj.get("events", [])
    return events if isinstance(events, list) else []


def load_upgrades() -> Dict[str, List[Dict[str, Any]]]:
    obj = _read_json(DATA_DIR / "upgrades.json", {"categories": {}})
    cats = obj.get("categories", {})
    return cats if isinstance(cats, dict) else {}


def load_endings() -> List[Dict[str, Any]]:
    obj = _read_json(DATA_DIR / "endings.json", {"endings": []})
    endings = obj.get("endings", [])
    return endings if isinstance(endings, list) else []
