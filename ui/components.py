# ceoparkmake/ui/components.py

from pathlib import Path
import streamlit as st

from game.logic import get_total_promotion_rate


ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"
IMG_DIR = ASSET_DIR / "images"


def render_header(g):
    st.markdown('<div class="pixel-card">', unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 2.8], vertical_alignment="top")

    with c1:
        bg_path = IMG_DIR / "bg_office.png"
        if bg_path.exists():
            st.image(str(bg_path), use_container_width=True)

    with c2:
        st.markdown(
            f"""
            <div style="font-size:26px;font-weight:800;">박효진은 CEO가 될 수 있을까?</div>
            <div style="font-size:14px;color:#555;">
                {g.company_count}번째 회사 · {g.company_name} · 현재 직급: <b>{g.rank}</b>
            </div>
            <div style="font-size:13px;color:#666;margin-top:4px;">
                {g.hometown} 출신 · {g.title} · 반려견 {g.dog_name} · 취미 {g.favorite}
            </div>
            """,
            unsafe_allow_html=True
        )

        badges = [
            f"💰 {g.money}원",
            f"📚 {g.exp}/{g.required_exp}",
            f"📈 승진확률 {get_total_promotion_rate(g)}%",
            f"💥 퇴사 {g.retire_count}회",
        ]
        st.markdown(
            "".join([f'<span class="pixel-badge">{b}</span>' for b in badges]),
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


def _bar_html(label: str, value: int, max_value: int, css_class: str):
    pct = 0 if max_value <= 0 else int((value / max_value) * 100)
    pct = max(0, min(100, pct))
    return f"""
    <div class="stat-box">
      <div class="stat-label">{label} {value}/{max_value}</div>
      <div class="stat-track">
        <div class="{css_class}" style="width:{pct}%;"></div>
      </div>
    </div>
    """


def render_status_panel(g):
    st.markdown(
        _bar_html("체력", g.hp, g.hp_max, "stat-fill-hp")
        + _bar_html("멘탈", g.mental, g.mental_max, "stat-fill-mental")
        + _bar_html("경력", g.exp, g.required_exp, "stat-fill-exp"),
        unsafe_allow_html=True
    )


def render_character_panel(g):
    c1, c2 = st.columns([1, 1])

    with c1:
        # 직급 기준으로 간단히 스프라이트 분기
        img_name = "hyojin_intern.png" if g.rank_index <= 4 else "hyojin_manager.png"
        img_path = IMG_DIR / img_name
        if img_path.exists():
            st.image(str(img_path), width=180)
        else:
            st.info("캐릭터 이미지 없음")

    with c2:
        dubung_path = IMG_DIR / "dubung.png"
        if dubung_path.exists():
            st.image(str(dubung_path), width=140)
            st.caption(f"{g.dog_name} (효진의 멘탈 담당)")
        else:
            st.info("두붕 이미지 없음")


def render_event_panel(g):
    if not g.pending_event:
        return

    e = g.pending_event
    title = e.get("title", "이벤트")
    speaker = e.get("speaker", "알림")
    text = e.get("text", "")

    st.markdown(
        f"""
        <div class="event-panel">
          <div class="event-title">{title}</div>
          <div class="event-speaker">[{speaker}]</div>
          <div class="event-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_logs(g):
    st.markdown('<div class="section-title">📜 최근 로그</div>', unsafe_allow_html=True)
    items = g.game_log or []
    html = '<div class="log-box">'
    for msg in items:
        html += f'<div class="log-item">{msg}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
