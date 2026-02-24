# ceoparkmake/ui/pixel_css.py

PIXEL_CSS = """
<style>
/* =========================================================
   0) 공통 / 픽셀 느낌
========================================================= */
html, body, [class*="css"] {
    image-rendering: pixelated;
}

.main .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1100px;
}

/* =========================================================
   1) 카드 공통
   - Streamlit 다크테마 글자색 충돌 방지 위해 !important 사용
========================================================= */
.pixel-card {
    border: 3px solid #2f3b52;
    border-radius: 10px;
    background: #f7f8fb;
    box-shadow: 4px 4px 0 #c7cfdf;
    padding: 10px;
    margin-bottom: 10px;
    color: #1f2937 !important;
}

/* 카드 내부 텍스트 강제색 */
.pixel-card,
.pixel-card * {
    color: #1f2937 !important;
}

/* 단, 버튼 텍스트는 Streamlit 버튼 기본 스타일 존중 */
.stButton button,
.stButton button * {
    color: inherit !important;
}

/* =========================================================
   2) 섹션 타이틀 / 배지
========================================================= */
.section-title {
    font-weight: 800;
    font-size: 16px;
    margin: 6px 0;
    color: #111827 !important;
}

.pixel-badge {
    display: inline-block;
    border: 2px solid #2f3b52;
    border-radius: 6px;
    padding: 2px 6px;
    background: #fff;
    margin-right: 6px;
    margin-bottom: 4px;
    font-size: 12px;
    color: #1f2937 !important;
}

/* =========================================================
   3) 상태창
========================================================= */
.stat-box {
    border: 2px solid #2f3b52;
    border-radius: 8px;
    padding: 8px;
    background: #ffffff;
    margin-bottom: 8px;
    color: #1f2937 !important;
}

.stat-box * {
    color: #1f2937 !important;
}

.stat-label {
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 4px;
    color: #1f2937 !important;
}

.stat-track {
    width: 100%;
    height: 18px;
    background: #d8deea;
    border: 2px solid #2f3b52;
    border-radius: 6px;
    overflow: hidden;
}

.stat-fill-hp {
    height: 100%;
    background: #ff4d5a;
}

.stat-fill-exp {
    height: 100%;
    background: #ffd24d;
}

.stat-fill-mental {
    height: 100%;
    background: #5aa9ff;
}

/* =========================================================
   4) 로그창
========================================================= */
.log-box {
    border: 2px solid #2f3b52;
    border-radius: 8px;
    background: #fff;
    padding: 8px;
    min-height: 220px;
    color: #1f2937 !important;
}

.log-box * {
    color: #1f2937 !important;
}

.log-item {
    border-bottom: 1px dashed #d4d9e5;
    padding: 5px 0;
    font-size: 13px;
    color: #1f2937 !important;
}

.log-item:last-child {
    border-bottom: none;
}

/* 로그 하이라이트(혹시 span 등으로 감쌀 때 대비) */
.log-item strong,
.log-item b {
    color: #111827 !important;
}

/* =========================================================
   5) 이벤트 패널
========================================================= */
.event-panel {
    border: 3px solid #2f3b52;
    border-radius: 10px;
    background: #eef4ff;
    padding: 10px;
    margin: 8px 0 12px 0;
    color: #1f2937 !important;
}

.event-panel * {
    color: #1f2937 !important;
}

.event-title {
    font-weight: 800;
    font-size: 18px;
    margin-bottom: 6px;
    color: #1f2937 !important;
}

.event-speaker {
    color: #445 !important;
    font-size: 13px;
    margin-bottom: 8px;
}

.event-text {
    background: #fffbe8;
    border: 2px solid #d7cfa8;
    border-radius: 8px;
    padding: 10px;
    line-height: 1.5;
    margin-bottom: 8px;
    color: #1f2937 !important;
}

.event-text * {
    color: #1f2937 !important;
}

/* =========================================================
   6) Streamlit 기본 위젯(탭/expander/메트릭 등) 최소 보정
   - 앱 전체를 다 바꾸지는 않고, 가독성만 보정
========================================================= */

/* 탭 텍스트 */
button[data-baseweb="tab"] {
    font-weight: 700 !important;
}

/* 탭 내부 글자색 (선택/비선택 모두) */
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] div,
button[data-baseweb="tab"] span {
    color: inherit !important;
}

/* 일반 markdown 문단이 카드 밖에서 너무 흐릴 경우 대비 (강하게는 안 건드림) */
.stMarkdown p {
    line-height: 1.45;
}

/* =========================================================
   7) 반응형 여백
========================================================= */
@media (max-width: 900px) {
    .main .block-container {
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }

    .section-title {
        font-size: 15px;
    }

    .event-title {
        font-size: 16px;
    }
}
</style>
"""
