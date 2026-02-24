# ceoparkmake/game/balance.py

# =========================================================
# 밸런스 규칙 (직급 / 업무 보상 / 승진 확률 / 필요 경험치)
# =========================================================

RANKS = [
    "인턴", "계약직", "정규직", "대리", "과장",
    "차장", "부장", "본부장", "이사", "COO", "CEO"
]

# 직급별 승진 실패 허용 횟수
PROMOTION_FAIL_LIMIT = {
    "인턴": 1,
    "계약직": 2,
}
DEFAULT_FAIL_LIMIT = 3

# 직급별 기본 승진 확률(베이스)
BASE_PROMOTION_RATE_BY_RANK = {
    "인턴": 75,
    "계약직": 65,
    "정규직": 55,
    "대리": 48,
    "과장": 42,
    "차장": 35,
    "부장": 28,
    "본부장": 22,
    "이사": 18,
    "COO": 12,
    "CEO": 100,
}

# 직급별 업무 보상 / 소모
WORK_REWARD_BY_RANK = {
    "인턴": {"money": 40, "exp": 10, "hp_cost": 8, "mental_cost": 5},
    "계약직": {"money": 70, "exp": 14, "hp_cost": 9, "mental_cost": 5},
    "정규직": {"money": 110, "exp": 18, "hp_cost": 10, "mental_cost": 6},
    "대리": {"money": 180, "exp": 22, "hp_cost": 11, "mental_cost": 7},
    "과장": {"money": 280, "exp": 26, "hp_cost": 12, "mental_cost": 8},
    "차장": {"money": 420, "exp": 30, "hp_cost": 13, "mental_cost": 9},
    "부장": {"money": 650, "exp": 34, "hp_cost": 14, "mental_cost": 10},
    "본부장": {"money": 900, "exp": 38, "hp_cost": 15, "mental_cost": 11},
    "이사": {"money": 1300, "exp": 42, "hp_cost": 16, "mental_cost": 12},
    "COO": {"money": 1800, "exp": 46, "hp_cost": 17, "mental_cost": 13},
    "CEO": {"money": 2500, "exp": 0, "hp_cost": 10, "mental_cost": 8},
}

# 직급별 승진 필요 경험치
EXP_REQUIREMENT_BY_RANK = {
    "인턴": 100,
    "계약직": 140,
    "정규직": 180,
    "대리": 240,
    "과장": 300,
    "차장": 360,
    "부장": 440,
    "본부장": 520,
    "이사": 620,
    "COO": 800,
    "CEO": 999999,  # 종착점
}
