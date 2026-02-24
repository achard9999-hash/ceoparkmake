# ceoparkmake/ui/pixel_css.py

PIXEL_CSS = """
<style>
/* 전체 폰트/배경 */
html, body, [class*="css"] {
    image-rendering: pixelated;
}

.main .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1100px;
}

/* 헤더 카드 */
.pixel-card {
    border: 3px solid #2f3b52;
    border-radius: 10px;
    background: #f7f8fb;
    box-shadow: 4px 4px 0 #c7cfdf;
    padding: 10px;
    margin-bottom: 10px;
}

/* 상태 바 박스 */
.stat-box {
    border: 2px solid #2f3b52;
    border-radius: 8px;
    padding: 8px;
    background: #ffffff;
    margin-bottom: 8px;
}

.stat-label {
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 4px;
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

/* 로그 */
.log-box {
    border: 2px solid #2f3b52;
    border-radius: 8px;
    background: #fff;
    padding: 8px;
    min-height: 220px;
}

.log-item {
    border-bottom: 1px dashed #d4d9e5;
    padding: 5px 0;
    font-size: 13px;
}
.log-item:last-child {
    border-bottom: none;
}

/* 이벤트 패널 */
.event-panel {
    border: 3px solid #2f3b52;
    border-radius: 10px;
    background: #eef4ff;
    padding: 10px;
    margin: 8px 0 12px 0;
}

.event-title {
    font-weight: 800;
    font-size: 18px;
    margin-bottom: 6px;
}

.event-speaker {
    color: #445;
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
}

/* 작은 배지 */
.pixel-badge {
    display: inline-block;
    border: 2px solid #2f3b52;
    border-radius: 6px;
    padding: 2px 6px;
    background: #fff;
    margin-right: 6px;
    margin-bottom: 4px;
    font-size: 12px;
}

/* 구분 텍스트 */
.section-title {
    font-weight: 800;
    font-size: 16px;
    margin: 6px 0;
}
</style>
"""
