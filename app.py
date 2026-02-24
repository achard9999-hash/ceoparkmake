import streamlit as st
import random
from dataclasses import dataclass, asdict

# =========================================================
# 박효진는 CEO가 될 수 있을까? - Streamlit Prototype v0.1
# =========================================================

st.set_page_config(
    page_title="박효진은 CEO가 될 수 있을까?",
    page_icon="💼",
    layout="centered"
)

# ---------------------------------------------------------
# 0) 도트풍 스타일 (간단 버전)
# ---------------------------------------------------------
PIXEL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

html, body, [class*="css"] {
    font-family: 'Jua', sans-serif;
}

.main {
    background: linear-gradient(180deg, #dff1ff 0%, #f7fbff 100%);
}

.pixel-card {
    border: 3px solid #333;
    border-radius: 12px;
    padding: 12px;
    background: #ffffff;
    box-shadow: 4px 4px 0 #999;
    margin-bottom: 10px;
}

.pixel-title {
    font-size: 28px;
    color: #ff6b35;
    text-shadow: 1px 1px 0 #fff;
    margin-bottom: 6px;
}

.pixel-subtitle {
    font-size: 18px;
    color: #2b2b2b;
}

.stat-label {
    font-weight: 700;
    color: #333;
}

.footer-tip {
    font-size: 14px;
    color: #555;
    background: #fff7d6;
    border: 2px dashed #d6a400;
    border-radius: 10px;
    padding: 8px;
}
</style>
"""
st.markdown(PIXEL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1) 밸런스 정의
# ---------------------------------------------------------
RANKS = [
    "인턴", "계약직", "정규직", "대리", "과장",
    "차장", "부장", "본부장", "이사", "COO", "CEO"
]

PROMOTION_FAIL_LIMIT = {
    "인턴": 1,
    "계약직": 2
}
DEFAULT_FAIL_LIMIT = 3

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
    "CEO": 100
}

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
    "CEO": 999999
}


# ---------------------------------------------------------
# 2) 이벤트 데이터 (초기 샘플)
# ---------------------------------------------------------
EVENTS = [
    {
        "id": "boss_weekend",
        "title": "주말 출근",
        "speaker": "팀장",
        "text": "효진씨~ 위에서 일정 당겨달래. 이번 주말에 다같이 나와서 마무리하자.",
        "choices": [
            {
                "label": "네 팀장님, 제가 먼저 정리해둘게요.",
                "effects": {"promotion_rate": +1, "hp": -10, "mental": -5},
                "result": "상사는 만족했지만, 박효진의 멘탈이 갈렸다..."
            },
            {
                "label": "이번 주는 두붕 병원 예약이 있어서요…",
                "effects": {"promotion_rate": -1, "mental": +3, "rel_boss": -1},
                "result": "두붕은 지켰다. 하지만 팀장 표정이 싸늘하다."
            }
        ]
    },
    {
        "id": "baseball_ticket",
        "title": "직관의 유혹",
        "speaker": "알림",
        "text": "오늘은 라이벌전! 그런데 하필 임원 보고가 18시에 잡혔다.",
        "choices": [
            {
                "label": "보고 먼저 끝내자.",
                "effects": {"promotion_rate": +2, "mental": -8},
                "result": "보고는 완벽했다. 하지만 경기 결과를 못 본 게 너무 아쉽다."
            },
            {
                "label": "오늘은 못 참아. 직관 간다!",
                "effects": {"promotion_rate": -2, "mental": +12, "money": -50},
                "result": "직관은 최고다. 응원하면서 멘탈이 회복됐다!"
            }
        ]
    },
    {
        "id": "boyfriend_marriage",
        "title": "결혼 얘기",
        "speaker": "남자친구",
        "text": "우리 5년 만났잖아. 이제 슬슬 같이 계획 세워볼까?",
        "choices": [
            {
                "label": "좋아. 같이 준비해보자.",
                "effects": {"money": -5000, "mental": +8, "promotion_rate": +1},
                "result": "현실은 무겁지만, 마음이 단단해졌다."
            },
            {
                "label": "조금만 더 기다려줘…",
                "effects": {"mental": -5},
                "result": "미안한 마음이 남는다."
            }
        ]
    },
    {
        "id": "dubung_walk",
        "title": "두붕 산책",
        "speaker": "두붕",
        "text": "(꼬리 흔드는 소리) 퇴근했더니 두붕이 문 앞에서 기다리고 있다.",
        "choices": [
            {
                "label": "그래, 10분만 걷자.",
                "effects": {"mental": +10, "hp": +4, "money": -100},
                "result": "두붕이 신났다. 효진도 조금 살아났다."
            },
            {
                "label": "내일 하자… 너무 피곤해.",
                "effects": {"hp": +6, "mental": -6},
                "result": "몸은 쉬었지만 마음이 무겁다."
            }
        ]
    },
    {
        "id": "sql_disaster",
        "title": "SQL 사고",
        "speaker": "시스템",
        "text": "WHERE 절 확인 안 하고 실행했다. 대시보드 수치가 이상하다.",
        "choices": [
            {
                "label": "바로 인정하고 수정한다.",
                "effects": {"mental": -3, "promotion_rate": +1},
                "result": "빠른 수습으로 신뢰를 지켰다."
            },
            {
                "label": "일단 조용히 덮어본다.",
                "effects": {"mental": -8, "promotion_rate": -2},
                "result": "결국 들켰다. 더 크게 혼났다."
            }
        ]
    },
]

RETIRE_REASONS = [
    "번아웃으로 퇴사",
    "승진 연속 실패로 권고사직",
    "야근 누적으로 건강 악화",
    "임원 보고 실수로 퇴사",
    "두붕 산책을 못 시켜 자책하며 퇴사",
    "프로젝트 우선순위 변경에 멘탈 붕괴",
    "직관 못 가서 인생회의 후 퇴사"
]

# ---------------------------------------------------------
# 3) 상태 모델
# ---------------------------------------------------------
@dataclass
class GameState:
    name: str = "박효진"
    company_name: str = "에미드넷"
    company_count: int = 1
    rank_index: int = 0  # 인턴
    hp: int = 100
    hp_max: int = 100
    exp: int = 0
    money: int = 500
    promotion_rate: int = 10
    mental: int = 100
    mental_max: int = 100
    promotion_fail_count: int = 0
    retire_count: int = 0
    title: str = "통계 석사"
    game_log: list = None
    pending_event: dict = None
    achievements: dict = None

    def __post_init__(self):
        if self.game_log is None:
            self.game_log = []
        if self.achievements is None:
            self.achievements = {
                "퇴사사유_수집": 0,
                "직관러": 0,
                "두붕맘": 0,
                "악마팀장": 0
            }

    @property
    def rank(self):
        return RANKS[self.rank_index]

    @property
    def required_exp(self):
        return EXP_REQUIREMENT_BY_RANK[self.rank]

    @property
    def fail_limit(self):
        return PROMOTION_FAIL_LIMIT.get(self.rank, DEFAULT_FAIL_LIMIT)

    @property
    def can_try_promotion(self):
        return self.exp >= self.required_exp and self.rank != "CEO"


def init_state():
    st.session_state.game = GameState()
    push_log("에미드넷에 인턴으로 입사했다. 과연 CEO가 될 수 있을까?")


def get_game() -> GameState:
    if "game" not in st.session_state:
        init_state()
    return st.session_state.game


def push_log(msg: str):
    g = get_game()
    g.game_log.insert(0, msg)
    g.game_log = g.game_log[:12]  # 최근 12개만


# ---------------------------------------------------------
# 4) 게임 로직
# ---------------------------------------------------------
def clamp_stats(g: GameState):
    g.hp = max(0, min(g.hp, g.hp_max))
    g.mental = max(0, min(g.mental, g.mental_max))
    g.promotion_rate = max(0, min(g.promotion_rate, 100))


def apply_effects(g: GameState, effects: dict):
    # 기본 스탯
    if "hp" in effects:
        g.hp += effects["hp"]
    if "mental" in effects:
        g.mental += effects["mental"]
    if "money" in effects:
        g.money += effects["money"]
    if "exp" in effects:
        g.exp += effects["exp"]
    if "promotion_rate" in effects:
        g.promotion_rate += effects["promotion_rate"]

    # 간단 업적 카운트
    if effects.get("mental", 0) >= 10:
        g.achievements["두붕맘"] += 1  # 단순 샘플 카운트

    clamp_stats(g)


def do_work():
    g = get_game()
    reward = WORK_REWARD_BY_RANK[g.rank]

    # 업무 수행
    g.money += reward["money"]
    g.exp += reward["exp"]
    g.hp -= reward["hp_cost"]
    g.mental -= reward["mental_cost"]

    # 소소한 랜덤 보너스/리스크
    roll = random.random()
    if roll < 0.12:
        g.money += 50
        push_log("업무 효율이 좋아서 추가 성과금 +50!")
    elif roll > 0.93:
        g.mental -= 5
        push_log("갑작스런 수정 요청… 멘탈 -5")

    clamp_stats(g)
    push_log(f"[업무] {g.rank} 업무 처리! 돈 +{reward['money']}, 경력 +{reward['exp']}")

    # 이벤트 발생 확률
    if random.random() < 0.35 and g.pending_event is None:
        g.pending_event = random.choice(EVENTS)
        push_log(f"이벤트 발생: {g.pending_event['title']}")

    # 퇴사 판정
    check_auto_retire()


def try_promotion():
    g = get_game()
    if not g.can_try_promotion:
        push_log("아직 경력이 부족해서 승진 심사를 볼 수 없다.")
        return

    # 직급 기본 난이도 + 유저 승진확률 조합
    base_rate = BASE_PROMOTION_RATE_BY_RANK[g.rank]
    final_rate = min(95, max(5, base_rate + g.promotion_rate))

    success = random.random() < (final_rate / 100)

    if success:
        old_rank = g.rank
        g.rank_index += 1
        g.exp = 0
        g.promotion_fail_count = 0
        g.promotion_rate = max(0, g.promotion_rate - 3)  # 승진 후 약간 리셋 감각
        g.money += 500  # 승진 보너스
        g.hp -= 5
        clamp_stats(g)
        push_log(f"🎉 승진 성공! {old_rank} → {g.rank}")
        if g.rank == "CEO":
            push_log("👑 박효진이 마침내 에미드넷 CEO가 되었다!")
    else:
        g.promotion_fail_count += 1
        g.exp = 0
        g.mental -= 12
        g.hp -= 8
        clamp_stats(g)
        push_log(f"❌ 승진 실패... ({g.promotion_fail_count}/{g.fail_limit})")

        if g.promotion_fail_count >= g.fail_limit:
            retire("승진 연속 실패로 권고사직")


def rest_action():
    g = get_game()
    g.hp += 20
    g.mental += 10
    g.money -= 100
    clamp_stats(g)
    push_log("카페에서 잠깐 쉬었다. 체력 +20, 멘탈 +10, 돈 -100")


def side_job_action():
    g = get_game()
    # 알바: 광고 대신 간단 보상
    if random.random() < 0.05:
        retire("투잡 뛰다 걸려서 권고사직")
        return
    reward_money = random.randint(250, 600)
    reward_exp = random.randint(5, 15)
    g.money += reward_money
    g.exp += reward_exp
    g.hp -= 5
    g.mental -= 2
    clamp_stats(g)
    push_log(f"외부 알바 완료! 돈 +{reward_money}, 경력 +{reward_exp}")


def check_auto_retire():
    g = get_game()
    if g.hp <= 0:
        retire("야근 누적으로 건강 악화")
    elif g.mental <= 0:
        retire("번아웃으로 퇴사")


def retire(reason: str = None):
    g = get_game()
    if reason is None:
        reason = random.choice(RETIRE_REASONS)

    g.retire_count += 1
    g.achievements["퇴사사유_수집"] += 1
    push_log(f"💥 퇴사 발생: {reason}")

    # 영구 보너스 느낌 (퇴사할수록 다음 런 약간 강해짐)
    next_company_count = g.company_count + 1
    bonus_promotion = min(15, g.retire_count)   # 최대 +15
    bonus_money = g.retire_count * 100

    # 재시작 (에미드넷 n번째 입사 컨셉)
    st.session_state.game = GameState(
        company_name="에미드넷",
        company_count=next_company_count,
        money=500 + bonus_money,
        promotion_rate=10 + bonus_promotion,
        title=g.title,
        retire_count=g.retire_count,
        achievements=g.achievements.copy()
    )
    push_log(f"{next_company_count}번째 입사. 퇴사 경험이 쌓여 승진감각이 조금 늘었다.")


# ---------------------------------------------------------
# 5) UI 렌더링
# ---------------------------------------------------------
def render_bgm_hint():
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown("### 🎵 배경음악 (설계 훅)")
    st.caption("현재는 프로토타입이라 실제 재생 대신 상태별 BGM 이름만 표시")
    g = get_game()

    if g.rank == "CEO":
        bgm = "bgm_ceo_victory.mp3"
    elif g.pending_event is not None:
        bgm = "bgm_event_tension.mp3"
    elif g.hp < 30 or g.mental < 30:
        bgm = "bgm_burnout_low.mp3"
    else:
        bgm = "bgm_office_day.mp3"

    st.info(f"현재 BGM: {bgm}")
    st.markdown('</div>', unsafe_allow_html=True)


def render_header():
    g = get_game()
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown('<div class="pixel-title">박효진은 CEO가 될 수 있을까?</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='pixel-subtitle'>{g.company_count}번째 에미드넷 · 현재 직급: <b>{g.rank}</b> · 타이틀: {g.title}</div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)


def render_stats():
    g = get_game()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
        st.markdown(f"**💰 돈**: {g.money}")
        st.markdown(f"**📈 경력**: {g.exp} / {g.required_exp if g.rank != 'CEO' else 'MAX'}")
        st.progress(min(1.0, g.exp / g.required_exp) if g.rank != "CEO" else 1.0)
        st.markdown(f"**🎯 승진확률 보너스**: +{g.promotion_rate}%")
        st.markdown(f"**❌ 승진 실패**: {g.promotion_fail_count}/{g.fail_limit if g.rank != 'CEO' else '-'}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
        st.markdown(f"**❤️ 체력**: {g.hp} / {g.hp_max}")
        st.progress(g.hp / g.hp_max)
        st.markdown(f"**🧠 멘탈**: {g.mental} / {g.mental_max}")
        st.progress(g.mental / g.mental_max)
        st.markdown(f"**🐶 두붕 상태**: 기다리는 중...")
        st.markdown('</div>', unsafe_allow_html=True)


def render_actions():
    g = get_game()

    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown("### 🎮 행동")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 업무하기", use_container_width=True):
            do_work()
            st.rerun()

        if st.button("☕ 쉬기", use_container_width=True):
            rest_action()
            st.rerun()

    with col2:
        if st.button("🧾 알바하기", use_container_width=True):
            side_job_action()
            st.rerun()

        if st.button("📊 승진 심사", use_container_width=True, disabled=not g.can_try_promotion):
            try_promotion()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_event_modal():
    g = get_game()
    if g.pending_event is None:
        return

    ev = g.pending_event
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown(f"## {ev['title']}")
    st.markdown(f"**{ev['speaker']}**")
    st.write(ev["text"])

    for i, choice in enumerate(ev["choices"]):
        if st.button(choice["label"], key=f"ev_choice_{ev['id']}_{i}", use_container_width=True):
            apply_effects(g, choice["effects"])
            push_log(f"[{ev['title']}] {choice['result']}")
            # 특정 업적 샘플 카운트
            if "직관" in ev["title"] and i == 1:
                g.achievements["직관러"] += 1
            g.pending_event = None
            check_auto_retire()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_achievements():
    g = get_game()
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown("### 🏷️ 진행 현황")
    st.write(f"- 누적 퇴사 횟수: **{g.retire_count}회**")
    st.write(f"- 퇴사사유 수집: **{g.achievements['퇴사사유_수집']}개**")
    st.write(f"- 직관러 포인트: **{g.achievements['직관러']}**")
    st.write(f"- 두붕맘 포인트: **{g.achievements['두붕맘']}**")
    st.markdown('</div>', unsafe_allow_html=True)


def render_logs():
    g = get_game()
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown("### 📜 최근 로그")
    if not g.game_log:
        st.write("아직 로그가 없습니다.")
    else:
        for msg in g.game_log:
            st.write(f"- {msg}")
    st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    st.markdown(
        '<div class="footer-tip">TIP: 초반엔 자주 퇴사해도 괜찮다. 퇴사 경험이 쌓일수록 다음 입사에서 조금 유리해진다.</div>',
        unsafe_allow_html=True
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 새 게임", use_container_width=True):
            init_state()
            st.rerun()
    with col2:
        st.button("💾 저장/불러오기 (추후 구현)", use_container_width=True, disabled=True)


# ---------------------------------------------------------
# 6) 메인 렌더
# ---------------------------------------------------------
def main():
    render_header()
    render_stats()
    render_bgm_hint()
    render_event_modal()   # 이벤트가 있으면 위에 노출
    render_actions()
    render_achievements()
    render_logs()
    render_footer()


if __name__ == "__main__":
    main()
