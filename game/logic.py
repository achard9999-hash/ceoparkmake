# ceoparkmake/game/logic.py

import random
from typing import Dict, Any, List, Tuple, Optional

from .balance import (
    RANKS,
    WORK_REWARD_BY_RANK,
    BASE_PROMOTION_RATE_BY_RANK,
)
from .state import GameState, clamp_stats, push_log, apply_effects, reset_for_rehire


# -------------------------
# 기본 액션
# -------------------------
def do_work(g: GameState) -> None:
    reward = WORK_REWARD_BY_RANK[g.rank]

    g.money += reward["money"]
    g.exp += reward["exp"]
    g.hp -= reward["hp_cost"]
    g.mental -= reward["mental_cost"]

    # 소소한 랜덤 보정
    if random.random() < 0.15:
        bonus = random.randint(10, 40)
        g.money += bonus
        push_log(g, f"📎 업무 효율 보너스! +{bonus}원")

    push_log(g, f"💼 업무 처리: 돈 +{reward['money']} / 경력 +{reward['exp']}")
    clamp_stats(g)


def do_rest(g: GameState) -> None:
    hp_gain = random.randint(10, 18)
    mental_gain = random.randint(8, 14)

    g.hp += hp_gain
    g.mental += mental_gain

    # 두붕 산책 감성 로그
    if random.random() < 0.4:
        push_log(g, f"🐶 {g.dog_name}과 산책했다. 마음이 조금 편해졌다.")
    else:
        push_log(g, "☕ 잠깐 쉬었다. 호흡을 가다듬었다.")

    clamp_stats(g)


def do_part_time(g: GameState) -> Optional[str]:
    """
    알바(광고 보기 느낌)
    - 소액 돈 / 소량 exp 보상
    - 낮은 확률로 퇴사 이벤트
    """
    money_gain = random.randint(300, 600)
    exp_gain = random.randint(5, 20)

    g.money += money_gain
    g.exp += exp_gain
    g.hp -= 3
    g.mental -= 2

    push_log(g, f"🎬 알바 완료: 돈 +{money_gain} / 경력 +{exp_gain}")

    # 5% 퇴사 리스크
    if random.random() < 0.05:
        reason = "투잡 뛰다 걸렸다!!"
        push_log(g, f"⚠️ {reason}")
        return reason

    clamp_stats(g)
    return None


# -------------------------
# 이벤트 관련 (중복 방지 + 조건 지원)
# -------------------------
def _ensure_event_runtime_fields(g: GameState) -> None:
    """GameState dataclass를 안 바꾸고 런타임 필드만 동적으로 붙인다."""
    if not hasattr(g, "recent_event_ids"):
        g.recent_event_ids = []  # type: ignore[attr-defined]


def _is_valid_event(event: Dict[str, Any]) -> bool:
    """최소 스키마 검증 (깨진 이벤트는 스킵)"""
    if not isinstance(event, dict):
        return False

    if not isinstance(event.get("id"), str) or not event.get("id"):
        return False
    if not isinstance(event.get("title"), str):
        return False
    if not isinstance(event.get("text"), str):
        return False

    choices = event.get("choices")
    if not isinstance(choices, list) or len(choices) == 0:
        return False

    for ch in choices:
        if not isinstance(ch, dict):
            return False
        if not isinstance(ch.get("label"), str):
            return False
        # effects/result는 없어도 fallback 처리 가능하지만, effects는 dict 권장
        effects = ch.get("effects", {})
        if effects is not None and not isinstance(effects, dict):
            return False

    return True


def _event_matches_conditions(g: GameState, event: Dict[str, Any]) -> bool:
    """
    events_* JSON의 선택적 conditions 지원
    예:
      "conditions": {
        "rank_is": "대리",
        "retire_count_gte": 3,
        "money_gte": 1000
      }
    """
    cond = event.get("conditions", {})
    if not cond:
        return True
    if not isinstance(cond, dict):
        return True  # 잘못 들어와도 게임 안 깨지게 통과(원하면 False로 바꿔도 됨)

    # rank 조건
    rank_is = cond.get("rank_is")
    if rank_is is not None and g.rank != str(rank_is):
        return False

    rank_in = cond.get("rank_in")
    if rank_in is not None:
        if not isinstance(rank_in, list):
            return False
        if g.rank not in [str(x) for x in rank_in]:
            return False

    rank_not = cond.get("rank_not")
    if rank_not is not None and g.rank == str(rank_not):
        return False

    # 숫자 조건
    def _gte(field_name: str, current_val: int) -> bool:
        if cond.get(field_name) is None:
            return True
        try:
            return current_val >= int(cond[field_name])
        except Exception:
            return False

    def _lte(field_name: str, current_val: int) -> bool:
        if cond.get(field_name) is None:
            return True
        try:
            return current_val <= int(cond[field_name])
        except Exception:
            return False

    if not _gte("retire_count_gte", g.retire_count):
        return False
    if not _gte("company_count_gte", g.company_count):
        return False
    if not _gte("money_gte", g.money):
        return False
    if not _lte("money_lte", g.money):
        return False
    if not _gte("exp_gte", g.exp):
        return False
    if not _gte("promotion_rate_gte", g.promotion_rate):
        return False

    return True


def _pick_event_with_rules(
    g: GameState,
    events: List[Dict[str, Any]],
    recent_limit: int = 4,
) -> Optional[Dict[str, Any]]:
    """
    규칙:
    1) 깨진 스키마 이벤트 제외
    2) conditions 불만족 이벤트 제외
    3) 최근 이벤트(recent_event_ids) 제외 우선
    4) 후보 없으면 최근 제외 규칙만 풀고 재시도
    """
    _ensure_event_runtime_fields(g)

    valid_events = [e for e in events if _is_valid_event(e)]
    if not valid_events:
        return None

    # 조건 필터
    eligible = [e for e in valid_events if _event_matches_conditions(g, e)]
    if not eligible:
        return None

    recent_ids = list(getattr(g, "recent_event_ids", []))

    # 최근 이벤트 제외
    fresh = [e for e in eligible if e.get("id") not in recent_ids]

    pool = fresh if fresh else eligible
    chosen = random.choice(pool)

    # 최근 기록 업데이트
    eid = chosen.get("id")
    if isinstance(eid, str) and eid:
        recent_ids.append(eid)
        recent_ids = recent_ids[-recent_limit:]
        g.recent_event_ids = recent_ids  # type: ignore[attr-defined]

    return chosen


def maybe_trigger_dialogue_event(g: GameState, dialogue_events: List[Dict[str, Any]], chance: float = 0.35) -> bool:
    if g.pending_event is not None:
        return False
    if not dialogue_events:
        return False
    if random.random() > chance:
        return False

    picked = _pick_event_with_rules(g, dialogue_events, recent_limit=4)
    if not picked:
        return False

    g.pending_event = picked
    push_log(g, f"💬 이벤트 발생: {g.pending_event.get('title', '대화 이벤트')}")
    return True


def maybe_trigger_adventure_event(g: GameState, adventure_events: List[Dict[str, Any]], chance: float = 0.20) -> bool:
    if g.pending_event is not None:
        return False
    if not adventure_events:
        return False
    if g.rank == "인턴":  # 원작 감성 반영: 인턴은 모험 제한
        return False
    if random.random() > chance:
        return False

    picked = _pick_event_with_rules(g, adventure_events, recent_limit=4)
    if not picked:
        return False

    g.pending_event = picked
    push_log(g, f"🎲 모험 발생: {g.pending_event.get('title', '모험 이벤트')}")
    return True


def resolve_pending_event_choice(g: GameState, choice_idx: int) -> Optional[str]:
    """
    선택지 적용
    반환값:
      - 퇴사 사유(str) / None
    """
    if g.pending_event is None:
        return None

    event = g.pending_event
    choices = event.get("choices", [])
    if not (0 <= choice_idx < len(choices)):
        return None

    chosen = choices[choice_idx]
    effects = chosen.get("effects", {})
    result_msg = chosen.get("result", "결과가 적용되었다.")

    apply_effects(g, effects)
    push_log(g, f"📝 {result_msg}")

    # 퇴사 플래그 처리
    retire_reason = chosen.get("retire_reason")
    g.pending_event = None
    return retire_reason


# -------------------------
# 승진 / 퇴사 / 판정
# -------------------------
def get_total_promotion_rate(g: GameState) -> int:
    base = BASE_PROMOTION_RATE_BY_RANK.get(g.rank, 10)
    total = base + g.promotion_rate
    return max(1, min(100, total))


def try_promotion(g: GameState) -> Tuple[bool, Optional[str]]:
    """
    returns:
      (성공여부, 퇴사사유)
    """
    if g.rank == "CEO":
        push_log(g, "👑 이미 CEO다.")
        return True, None

    if not g.can_try_promotion:
        push_log(g, f"📚 경력이 부족하다. ({g.exp}/{g.required_exp})")
        return False, None

    rate = get_total_promotion_rate(g)
    roll = random.randint(1, 100)

    push_log(g, f"📈 승진 심사 중... (확률 {rate}%, 주사위 {roll})")

    if roll <= rate:
        old_rank = g.rank
        g.rank_index = min(g.rank_index + 1, len(RANKS) - 1)
        g.exp = 0
        g.promotion_fail_count = 0
        g.promotion_rate = max(0, g.promotion_rate - 3)  # 승진 보너스 일부 소모
        g.hp -= 6
        g.mental += 5
        clamp_stats(g)

        push_log(g, f"🎉 승진 성공! {old_rank} → {g.rank}")
        return True, None

    # 실패
    g.promotion_fail_count += 1
    g.exp = 0
    g.mental -= 10
    g.hp -= 8
    clamp_stats(g)

    push_log(g, f"❌ 승진 실패... ({g.promotion_fail_count}/{g.fail_limit})")

    if g.promotion_fail_count >= g.fail_limit:
        return False, "승진 누적 실패로 권고사직"

    return False, None


def check_for_forced_retirement(g: GameState) -> Optional[str]:
    if g.hp <= 0:
        return "과로로 번아웃"
    if g.mental <= 0:
        return "멘탈 붕괴"
    return None


def retire_and_rehire(g: GameState, reason: str) -> GameState:
    return reset_for_rehire(g, reason)


# -------------------------
# 엔딩 판정
# -------------------------
def check_endings(g: GameState, endings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    endings.json 조건과 매칭
    현재는 간단 조건만 지원:
      - rank_is
      - retire_count_gte
      - company_count_gte
      - money_gte
    """
    for e in endings:
        cond = e.get("conditions", {})
        ok = True

        rank_is = cond.get("rank_is")
        if rank_is and g.rank != rank_is:
            ok = False

        if cond.get("retire_count_gte") is not None:
            if g.retire_count < int(cond["retire_count_gte"]):
                ok = False

        if cond.get("company_count_gte") is not None:
            if g.company_count < int(cond["company_count_gte"]):
                ok = False

        if cond.get("money_gte") is not None:
            if g.money < int(cond["money_gte"]):
                ok = False

        if ok:
            return e

    return None
