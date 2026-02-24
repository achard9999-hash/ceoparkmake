# ceoparkmake/ui/styles.py

import streamlit as st
from .pixel_css import PIXEL_CSS


def apply_global_styles():
    st.set_page_config(
        page_title="박효진은 CEO가 될 수 있을까?",
        page_icon="💼",
        layout="wide"
    )
    st.markdown(PIXEL_CSS, unsafe_allow_html=True)
