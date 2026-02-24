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
# 이벤트 관련
# -------------------------
def maybe_trigger_dialogue_event(g: GameState, dialogue_events: List[Dict[str, Any]], chance: float = 0.35) -> bool:
    if g.pending_event is not None:
        return False
    if not dialogue_events:
        return False
    if random.random() > chance:
        return False

    g.pending_event = random.choice(dialogue_events)
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

    g.pending_event = random.choice(adventure_events)
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
