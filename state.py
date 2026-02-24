# ceoparkmake/game/state.py

from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from .balance import (
    RANKS,
    EXP_REQUIREMENT_BY_RANK,
    PROMOTION_FAIL_LIMIT,
    DEFAULT_FAIL_LIMIT,
)


@dataclass
class GameState:
    # 기본 정보
    name: str = "박효진"
    company_name: str = "에미드넷"
    company_count: int = 1
    rank_index: int = 0  # 인턴 시작

    # 스탯
    hp: int = 100
    hp_max: int = 100
    mental: int = 100
    mental_max: int = 100
    exp: int = 0
    money: int = 500

    # 진행
    promotion_rate: int = 10  # 추가 보너스 개념
    promotion_fail_count: int = 0
    retire_count: int = 0

    # 캐릭터 설정
    title: str = "통계 석사"
    hometown: str = "동투"
    dog_name: str = "두붕"
    favorite: str = "야구 직관"

    # 런타임
    game_log: Optional[List[str]] = None
    pending_event: Optional[Dict[str, Any]] = None
    achievements: Optional[Dict[str, int]] = None

    def __post_init__(self):
        if self.game_log is None:
            self.game_log = []

        if self.achievements is None:
            self.achievements = {
                "퇴사사유_수집": 0,
                "직관러": 0,
                "두붕맘": 0,
                "데이터장인": 0,
                "악마팀장": 0,
            }

    @property
    def rank(self) -> str:
        return RANKS[self.rank_index]

    @property
    def required_exp(self) -> int:
        return EXP_REQUIREMENT_BY_RANK[self.rank]

    @property
    def fail_limit(self) -> int:
        return PROMOTION_FAIL_LIMIT.get(self.rank, DEFAULT_FAIL_LIMIT)

    @property
    def can_try_promotion(self) -> bool:
        return (self.rank != "CEO") and (self.exp >= self.required_exp)


def clamp_stats(g: GameState) -> None:
    g.hp = max(0, min(g.hp, g.hp_max))
    g.mental = max(0, min(g.mental, g.mental_max))
    g.promotion_rate = max(0, min(g.promotion_rate, 100))
    g.money = max(0, g.money)
    g.exp = max(0, g.exp)


def init_game_state() -> GameState:
    """새 게임 시작용 상태 생성"""
    g = GameState()
    push_log(g, "에미드넷에 인턴으로 입사했다. 과연 CEO가 될 수 있을까?")
    push_log(g, "H대 통계학 석사 출신 박효진. 두붕과 함께 오늘도 출근.")
    return g


def reset_for_rehire(
    prev: GameState,
    reason: str,
) -> GameState:
    """
    퇴사 후 재입사 상태 생성
    - 퇴사 횟수에 따라 약간의 완화 보너스
    """
    retire_count = prev.retire_count + 1
    next_company_count = prev.company_count + 1

    bonus_promotion = min(15, retire_count)    # 최대 +15
    bonus_money = retire_count * 100

    g = GameState(
        name=prev.name,
        company_name=prev.company_name,
        company_count=next_company_count,
        rank_index=0,
        hp=100,
        hp_max=100,
        mental=100,
        mental_max=100,
        exp=0,
        money=500 + bonus_money,
        promotion_rate=10 + bonus_promotion,
        promotion_fail_count=0,
        retire_count=retire_count,
        title=prev.title,
        hometown=prev.hometown,
        dog_name=prev.dog_name,
        favorite=prev.favorite,
        achievements=prev.achievements.copy(),
    )

    # 퇴사사유 수집
    g.achievements["퇴사사유_수집"] = g.achievements.get("퇴사사유_수집", 0) + 1

    push_log(g, f"💥 퇴사 발생: {reason}")
    push_log(g, f"{g.company_count}번째 에미드넷 입사. 이전 회사의 상처가 교훈이 되었다.")
    return g


def push_log(g: GameState, msg: str, max_logs: int = 12) -> None:
    g.game_log.insert(0, msg)
    g.game_log = g.game_log[:max_logs]


def apply_effects(g: GameState, effects: Dict[str, int]) -> None:
    """
    이벤트 선택지 효과 적용
    허용 키 예시: hp, mental, money, exp, promotion_rate
    """
    if "hp" in effects:
        g.hp += int(effects["hp"])
    if "mental" in effects:
        g.mental += int(effects["mental"])
    if "money" in effects:
        g.money += int(effects["money"])
    if "exp" in effects:
        g.exp += int(effects["exp"])
    if "promotion_rate" in effects:
        g.promotion_rate += int(effects["promotion_rate"])

    # 간단 업적 카운트 규칙
    if effects.get("mental", 0) >= 8:
        g.achievements["두붕맘"] = g.achievements.get("두붕맘", 0) + 1
    if effects.get("exp", 0) >= 10:
        g.achievements["데이터장인"] = g.achievements.get("데이터장인", 0) + 1

    clamp_stats(g)
