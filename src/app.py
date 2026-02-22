"""
Description: Main entry point for Dictionary Forge.
"""

import pandas as pd
import streamlit as st

from components.edition_modal import render_edition_modal
from components.export_modal import render_export_modal
from components.governance_manager import render_governance_manager
from components.project_form import render_project_form

# Modular UI Sections
from components.sidebar import render_sidebar
from components.variable_form import render_variable_form

# Import constants and unified logic package
from constants import MASTER_CONFIG_PATH
from logic import flatten_json, load_master_schema

# ==============================================================================
# 1. INITIALIZATION & LAYOUT STATE
# ==============================================================================
st.set_page_config(page_title="Dictionary Forge", page_icon="🏗️", layout="wide")

if "split_ratio" not in st.session_state:
    st.session_state["split_ratio"] = 45

if "project_info" not in st.session_state:
    st.session_state["project_info"] = {
        "project_name": "New Project",
        "version": "1.0.0",
        "description": "",
        "stakeholders": [],
    }
if "variables" not in st.session_state:
    st.session_state["variables"] = []
if "active_v_inputs" not in st.session_state:
    st.session_state["active_v_inputs"] = {}
if "form_id" not in st.session_state:
    st.session_state["form_id"] = 0

# ==============================================================================
# 2. THE VIEWPORT ENGINE (STRICT CSS)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Kill global app scroll */
    [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }

    .block-container {
        padding: 0 !important;
        height: 100vh !important;
        max-width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
    }

    /* THE BLUE SEPARATION LINE */
    .resizer-line {
        height: 3px;
        background-color: #007BFF; /* Primary Blue */
        width: 100%;
        box-shadow: 0 0 10px rgba(0, 123, 255, 0.5);
        z-index: 100;
        margin-top: 2px;
        margin-bottom: 2px;
    }

    .panel-header-label {
        font-weight: bold;
        color: #00ff00;
        font-size: 0.7rem;
        text-transform: uppercase;
        padding: 5px 20px;
        background-color: #1E1E1E;
    }

    div.stButton > button[key="btn_add_ledger"] {
        background-color: #007BFF !important;
        color: white !important;
        border: none !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. SIDEBAR CONTROLS
# ==============================================================================
render_sidebar()

with st.sidebar:
    st.divider()
    st.subheader("🖥️ Viewport Control")
    st.session_state["split_ratio"] = st.number_input(
        "Split % (Form vs Ledger)",
        min_value=20,
        max_value=80,
        value=st.session_state["split_ratio"],
        step=5,
    )

if st.session_state.get("show_gov_manager"):
    render_governance_manager()

try:
    schema = load_master_schema(MASTER_CONFIG_PATH)
    variable_fields = schema.get("variable_schema", [])
except Exception as e:
    st.error(f"Init Error: {e}")
    st.stop()

# ==============================================================================
# 4. TOP PANEL: DRAFTING ZONE
# ==============================================================================
st.markdown(
    '<div class="panel-header-label">🏗️ Variable Drafting Workspace</div>',
    unsafe_allow_html=True,
)

top_vh = st.session_state["split_ratio"]
with st.container(height=int(top_vh * 8.5), border=True):
    render_project_form()
    st.divider()
    render_variable_form(variable_fields)

# ==============================================================================
# 5. THE PERMANENT SEPARATION LINE (BLUE)
# ==============================================================================
st.markdown('<div class="resizer-line"></div>', unsafe_allow_html=True)

# ==============================================================================
# 6. BOTTOM PANEL: LEDGER
# ==============================================================================
st.markdown(
    '<div class="panel-header-label">🔍 Live Data Dictionary Ledger</div>',
    unsafe_allow_html=True,
)

bottom_vh = 82 - top_vh

with st.container(height=int(bottom_vh * 10), border=True):
    col_filter, col_edit, col_add, col_export = st.columns([1.8, 0.4, 0.7, 0.4])

    with col_filter:
        q = st.text_input("Filter Dictionary...", key="p_filter", label_visibility="collapsed").lower()

    with col_edit:
        if st.button("✏️ Edit", key="btn_e", use_container_width=True):
            render_edition_modal()

    with col_add:
        if st.button("➕ Add", key="btn_add_ledger", use_container_width=True):
            if st.session_state.get("active_v_inputs"):
                from components.variable_form.handlers import process_form_submission

                process_form_submission(
                    st.session_state["active_v_inputs"],
                    st.session_state.get("current_at"),
                    st.session_state.get("current_dt"),
                )
                st.rerun()

    with col_export:
        if st.button("🚀 Export", key="btn_x", type="primary", use_container_width=True):
            render_export_modal()

    # Framed Table
    if st.session_state["variables"]:
        filtered = [
            v
            for v in st.session_state["variables"]
            if q in f"{v.get('name', '')} {v.get('description', '')} {v.get('alias', '')}".lower()
        ]
        if filtered:
            df_preview = pd.DataFrame([flatten_json(v) for v in filtered])
            with st.container(border=True):
                st.dataframe(
                    df_preview,
                    use_container_width=True,
                    hide_index=True,
                    height=int(bottom_vh * 7),
                )
            st.markdown('<div style="height:50px;"></div>', unsafe_allow_html=True)
        else:
            st.warning("No matches found.")
    else:
        st.info("The ledger is empty.")
