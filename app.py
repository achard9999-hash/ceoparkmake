# ceoparkmake/app.py

import streamlit as st

from ui.styles import apply_global_styles
from ui.components import (
    render_header,
    render_status_panel,
    render_character_panel,
    render_event_panel,
    render_logs,
)

from game.state import (
    init_game_state,
    push_log,
    clamp_stats,
)
from game.logic import (
    do_work,
    do_rest,
    do_part_time,
    maybe_trigger_dialogue_event,
    maybe_trigger_adventure_event,
    resolve_pending_event_choice,
    try_promotion,
    check_for_forced_retirement,
    retire_and_rehire,
    check_endings,
)
from game.content_loader import (
    load_dialogue_events,
    load_adventure_events,
    load_upgrades,
    load_endings,
)


# =========================================================
# 0) 초기 설정 / 리소스 로드
# =========================================================
apply_global_styles()

# JSON 데이터(캐시)
@st.cache_data
def _load_all_content():
    return {
        "dialogue_events": load_dialogue_events(),
        "adventure_events": load_adventure_events(),
        "upgrades": load_upgrades(),
        "endings": load_endings(),
    }

content = _load_all_content()


# =========================================================
# 1) 세션 상태 초기화
# =========================================================
def ensure_session():
    if "game" not in st.session_state:
        st.session_state.game = init_game_state()

    # 구매한 업그레이드 id 저장
    if "purchased_upgrades" not in st.session_state:
        st.session_state.purchased_upgrades = set()

    # 발동된 엔딩(중복 팝업 방지)
    if "triggered_ending_id" not in st.session_state:
        st.session_state.triggered_ending_id = None


ensure_session()
g = st.session_state.game


# =========================================================
# 2) 업그레이드 적용 함수
# =========================================================
def _apply_upgrade_effects(game, effects: dict):
    """
    upgrades.json 효과 적용
    - 즉시효과: hp, mental, hp_max, mental_max, promotion_rate
    - 영구보너스: work_money_bonus, work_exp_bonus (세션 상태에 누적 저장)
    """
    if not effects:
        return

    # 즉시/스탯 효과
    if "hp_max" in effects:
        game.hp_max += int(effects["hp_max"])
    if "mental_max" in effects:
        game.mental_max += int(effects["mental_max"])
    if "hp" in effects:
        game.hp += int(effects["hp"])
    if "mental" in effects:
        game.mental += int(effects["mental"])
    if "promotion_rate" in effects:
        game.promotion_rate += int(effects["promotion_rate"])

    # 영구 업무 보너스는 세션에 누적
    if "upgrade_bonuses" not in st.session_state:
        st.session_state.upgrade_bonuses = {"work_money_bonus": 0, "work_exp_bonus": 0}

    if "work_money_bonus" in effects:
        st.session_state.upgrade_bonuses["work_money_bonus"] += int(effects["work_money_bonus"])
    if "work_exp_bonus" in effects:
        st.session_state.upgrade_bonuses["work_exp_bonus"] += int(effects["work_exp_bonus"])

    clamp_stats(game)


def _get_upgrade_bonuses():
    if "upgrade_bonuses" not in st.session_state:
        st.session_state.upgrade_bonuses = {"work_money_bonus": 0, "work_exp_bonus": 0}
    return st.session_state.upgrade_bonuses


# =========================================================
# 3) 게임 액션 래퍼 (공통 후처리 포함)
# =========================================================
def _post_action_checks():
    """액션 후 공통 판정: 강제퇴사 -> 엔딩"""
    global g

    # 체력/멘탈 바닥 퇴사
    forced_reason = check_for_forced_retirement(g)
    if forced_reason:
        st.session_state.game = retire_and_rehire(g, forced_reason)
        g = st.session_state.game

    # 엔딩 판정 (최초 1회만)
    if st.session_state.triggered_ending_id is None:
        ending = check_endings(g, content["endings"])
        if ending:
            st.session_state.triggered_ending_id = ending.get("id")
            st.session_state.triggered_ending = ending


def action_work():
    """업무 + 업그레이드 보너스 반영 + 이벤트 확률 발생"""
    global g

    # 기본 업무 수행
    do_work(g)

    # 업그레이드 보너스 추가 반영
    bonuses = _get_upgrade_bonuses()
    bonus_money = int(bonuses.get("work_money_bonus", 0))
    bonus_exp = int(bonuses.get("work_exp_bonus", 0))

    if bonus_money > 0:
        g.money += bonus_money
        push_log(g, f"⚙️ 업무능력 보너스: 돈 +{bonus_money}")

    if bonus_exp > 0:
        g.exp += bonus_exp
        push_log(g, f"⚙️ 업무능력 보너스: 경력 +{bonus_exp}")

    clamp_stats(g)

    # 업무 후 이벤트 판정 (대화 우선, 모험 후순위)
    if not maybe_trigger_dialogue_event(g, content["dialogue_events"], chance=0.35):
        maybe_trigger_adventure_event(g, content["adventure_events"], chance=0.20)

    _post_action_checks()


def action_rest():
    do_rest(g)

    # 휴식 후 가끔 대화 이벤트
    maybe_trigger_dialogue_event(g, content["dialogue_events"], chance=0.18)
    _post_action_checks()


def action_part_time():
    global g
    reason = do_part_time(g)
    if reason:
        st.session_state.game = retire_and_rehire(g, reason)
        g = st.session_state.game
    else:
        maybe_trigger_dialogue_event(g, content["dialogue_events"], chance=0.15)

    _post_action_checks()


def action_try_promotion():
    global g
    success, retire_reason = try_promotion(g)

    if retire_reason:
        st.session_state.game = retire_and_rehire(g, retire_reason)
        g = st.session_state.game
    else:
        # 승진 성공 시 승진 이벤트 감성 로그/대화 가끔
        if success:
            push_log(g, "✨ 회사 공기가 조금 달라진 것 같다.")
        maybe_trigger_dialogue_event(g, content["dialogue_events"], chance=0.25)

    _post_action_checks()


def action_choice(choice_idx: int):
    global g
    retire_reason = resolve_pending_event_choice(g, choice_idx)
    if retire_reason:
        st.session_state.game = retire_and_rehire(g, retire_reason)
        g = st.session_state.game

    _post_action_checks()


# =========================================================
# 4) 사이드바: 게임 제어 / 디버그성 편의
# =========================================================
with st.sidebar:
    st.markdown("### 🎮 게임 제어")

    if st.button("🔄 새 게임 시작", use_container_width=True):
        st.session_state.game = init_game_state()
        st.session_state.purchased_upgrades = set()
        st.session_state.upgrade_bonuses = {"work_money_bonus": 0, "work_exp_bonus": 0}
        st.session_state.triggered_ending_id = None
        if "triggered_ending" in st.session_state:
            del st.session_state["triggered_ending"]
        st.rerun()

    st.markdown("---")
    st.caption("Private Birthday Gift Prototype")
    st.caption("ceoparkmake / Streamlit MVP")


# =========================================================
# 5) 메인 레이아웃
# =========================================================
render_header(g)

left, right = st.columns([1.2, 1.0], vertical_alignment="top")

# -------------------------
# 좌측: 캐릭터 / 상태 / 액션 / 이벤트
# -------------------------
with left:
    c1, c2 = st.columns([1, 1], vertical_alignment="top")

    with c1:
        st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 캐릭터</div>', unsafe_allow_html=True)
        render_character_panel(g)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 상태</div>', unsafe_allow_html=True)
        render_status_panel(g)
        st.markdown("</div>", unsafe_allow_html=True)

    # 엔딩 팝업 느낌 패널
    if st.session_state.get("triggered_ending_id") and st.session_state.get("triggered_ending"):
        e = st.session_state["triggered_ending"]
        st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="section-title">🏁 엔딩 달성</div>
            <div class="event-panel">
              <div class="event-title">{e.get('name', '엔딩')}</div>
              <div class="event-text">{e.get('description', '')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # 이벤트 패널
    if g.pending_event:
        st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
        render_event_panel(g)

        choices = g.pending_event.get("choices", [])
        for i, ch in enumerate(choices):
            label = ch.get("label", f"선택지 {i+1}")
            if st.button(label, key=f"event_choice_{g.pending_event.get('id','evt')}_{i}", use_container_width=True):
                action_choice(i)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # 액션 패널 (이벤트 없을 때만 주요 액션)
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🕹️ 행동</div>', unsafe_allow_html=True)

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("💼 업무", use_container_width=True, disabled=g.pending_event is not None):
            action_work()
            st.rerun()
    with a2:
        if st.button("☕ 휴식", use_container_width=True, disabled=g.pending_event is not None):
            action_rest()
            st.rerun()
    with a3:
        if st.button("🎬 알바", use_container_width=True, disabled=g.pending_event is not None):
            action_part_time()
            st.rerun()
    with a4:
        promo_disabled = (g.pending_event is not None) or (g.rank == "CEO")
        if st.button("📈 승진", use_container_width=True, disabled=promo_disabled):
            action_try_promotion()
            st.rerun()

    # 승진 보조 안내
    if g.rank != "CEO":
        if g.can_try_promotion:
            st.success(f"승진 시도 가능! (경력 {g.exp}/{g.required_exp})")
        else:
            st.info(f"승진 조건: 경력 {g.exp}/{g.required_exp}")
    else:
        st.success("👑 CEO 달성! 숨겨진 엔딩/자진퇴사 루트를 다음 버전에서 추가 가능")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# 우측: 로그 / 업그레이드 / 데이터
# -------------------------
with right:
    # 로그
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    render_logs(g)
    st.markdown("</div>", unsafe_allow_html=True)

    # 업그레이드 (MVP)
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧠 스펙업</div>', unsafe_allow_html=True)

    upgrade_cats = content["upgrades"] or {}
    purchased = st.session_state.purchased_upgrades

    if not upgrade_cats:
        st.info("upgrades.json 비어있음")
    else:
        tabs = st.tabs(list(upgrade_cats.keys()))
        for tab, cat_name in zip(tabs, upgrade_cats.keys()):
            with tab:
                items = upgrade_cats.get(cat_name, [])
                if not items:
                    st.caption("항목 없음")
                    continue

                for item in items:
                    uid = item.get("id", "")
                    name = item.get("name", "업그레이드")
                    cost = int(item.get("cost", 0))
                    effects = item.get("effects", {})

                    col_a, col_b = st.columns([2.8, 1.2], vertical_alignment="center")

                    with col_a:
                        effect_texts = []
                        for k, v in effects.items():
                            if k == "work_money_bonus":
                                effect_texts.append(f"업무 돈 +{v}")
                            elif k == "work_exp_bonus":
                                effect_texts.append(f"업무 경력 +{v}")
                            elif k == "promotion_rate":
                                effect_texts.append(f"승진확률 +{v}%")
                            elif k == "hp_max":
                                effect_texts.append(f"최대체력 +{v}")
                            elif k == "mental_max":
                                effect_texts.append(f"최대멘탈 +{v}")
                            elif k == "hp":
                                effect_texts.append(f"체력 +{v}")
                            elif k == "mental":
                                effect_texts.append(f"멘탈 +{v}")
                            else:
                                effect_texts.append(f"{k}:{v}")

                        st.markdown(f"**{name}**")
                        st.caption(f"비용 {cost}원 · " + ", ".join(effect_texts))

                    with col_b:
                        is_bought = uid in purchased
                        disabled = is_bought or (g.money < cost)
                        btn_label = "구매완료" if is_bought else "구입하기"

                        if st.button(btn_label, key=f"upgrade_{uid}", use_container_width=True, disabled=disabled):
                            g.money -= cost
                            _apply_upgrade_effects(g, effects)
                            purchased.add(uid)
                            push_log(g, f"🛍️ 업그레이드 구매: {name}")
                            _post_action_checks()
                            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 진행 정보 / 디버그 요약
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📌 진행 요약</div>', unsafe_allow_html=True)

    bonuses = _get_upgrade_bonuses()
    st.markdown(
        f"""
        - **현재 직급:** {g.rank}  
        - **회사 수:** {g.company_count}번째  
        - **퇴사 횟수:** {g.retire_count}회  
        - **추가 승진 보너스:** +{g.promotion_rate}%  
        - **업무 보너스(돈):** +{bonuses.get("work_money_bonus", 0)}  
        - **업무 보너스(경력):** +{bonuses.get("work_exp_bonus", 0)}  
        """,
        unsafe_allow_html=False
    )

    # 간단 업적 표시
    if getattr(g, "achievements", None):
        st.markdown("**업적 카운트(초안)**")
        for k, v in g.achievements.items():
            st.caption(f"- {k}: {v}")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 6) 하단 도움말
# =========================================================
st.markdown('<div class="pixel-card">', unsafe_allow_html=True)
st.markdown(
    """
    **플레이 방법 (MVP)**  
    1) `업무`로 돈/경력을 모으기  
    2) `휴식`으로 체력/멘탈 관리하기  
    3) 랜덤 `대화/모험 이벤트` 선택하기  
    4) 경력이 차면 `승진` 시도  
    5) 체력/멘탈이 0이 되거나 승진 실패 누적 시 퇴사 → 재입사 루프  
    """,
    unsafe_allow_html=False
)
st.markdown("</div>", unsafe_allow_html=True)
