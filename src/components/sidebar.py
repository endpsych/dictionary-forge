"""
Description: Modular sidebar component for Dictionary Forge.
"""

import streamlit as st

from components.cloning_modal import render_cloning_modal
from components.quality_modal import render_quality_modal
from components.template_modal import render_template_modal
from sections.batch_forge import render_batch_forge


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🛠️ Global Controls")

        if st.button("⚖️ Manage Regulations", use_container_width=True):
            st.session_state["show_gov_manager"] = True
            st.session_state["reg_manager_view"] = "LIST"

        if st.button("🛡️ Data Quality Audit", use_container_width=True):
            render_quality_modal()

        if st.button("💾 Variable Templates", use_container_width=True):
            render_template_modal()

        if st.button("📑 Variable Cloning", use_container_width=True):
            render_cloning_modal()

        if st.button("🚀 Batch Forge", use_container_width=True):
            render_batch_forge()

        with st.popover("🧹 Dictionary Cleanup", use_container_width=True):
            st.warning("This action is permanent.")
            confirm_clear = st.checkbox("Confirm Deletion", key="sidebar_clear_confirm")
            if st.button(
                "Clear All Variables",
                type="primary",
                use_container_width=True,
                disabled=not confirm_clear,
            ):
                st.session_state["variables"] = []
                st.session_state["editing_index"] = None
                st.rerun()
