# ceoparkmake/game/events.py

import json
from pathlib import Path
from typing import List, Dict, Any


# 프로젝트 루트 기준 data 경로 추정
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _fallback_dialogue_events() -> List[Dict[str, Any]]:
    """
    JSON 로드 실패 시 최소 동작 보장용 기본 이벤트
    """
    return [
        {
            "id": "boss_weekend",
            "category": "dialogue",
            "title": "주말 출근",
            "speaker": "팀장",
            "text": "효진씨~ 이번 주말에 다같이 나와서 마무리하자.",
            "choices": [
                {
                    "label": "네 팀장님, 제가 먼저 정리해둘게요.",
                    "effects": {"promotion_rate": 1, "hp": -10, "mental": -5},
                    "result": "상사는 만족했지만 멘탈이 갈렸다..."
                },
                {
                    "label": "이번 주는 두붕 병원 예약이 있어서요…",
                    "effects": {"promotion_rate": -1, "mental": 3},
                    "result": "두붕은 지켰다. 하지만 팀장 표정이 싸늘하다."
                }
            ]
        },
        {
            "id": "baseball_ticket",
            "category": "dialogue",
            "title": "직관의 유혹",
            "speaker": "알림",
            "text": "오늘은 라이벌전! 그런데 임원 보고가 18시에 잡혔다.",
            "choices": [
                {
                    "label": "보고 먼저 끝내자.",
                    "effects": {"promotion_rate": 2, "mental": -8},
                    "result": "보고는 완벽했다. 하지만 직관을 못 갔다."
                },
                {
                    "label": "오늘은 못 참아. 직관 간다!",
                    "effects": {"promotion_rate": -2, "mental": 12, "money": -50},
                    "result": "직관은 최고다. 응원하면서 멘탈 회복!"
                }
            ]
        }
    ]


def load_dialogue_events() -> List[Dict[str, Any]]:
    path = DATA_DIR / "events_dialogue.json"

    if not path.exists():
        return _fallback_dialogue_events()

    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        # 스키마: {"events": [...]}
        events = obj.get("events", [])
        if isinstance(events, list) and len(events) > 0:
            return events

        return _fallback_dialogue_events()

    except Exception:
        return _fallback_dialogue_events()


def pick_random_dialogue_event(events: List[Dict[str, Any]]):
    """
    logic.py에서 random.choice로 써도 되지만
    나중에 가중치/조건 필터 넣기 쉽게 함수 분리
    """
    import random

    if not events:
        events = _fallback_dialogue_events()
    return random.choice(events)
