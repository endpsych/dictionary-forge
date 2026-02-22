"""
Description: Sidebar management for Variable Blueprints.
Handles global template selection, destructive overwrites, and full-payload saving.
"""

import copy

import streamlit as st

from logic import apply_template_to_state, load_all_templates, save_user_template


def render_template_manager_sidebar():
    """
    Renders the Blueprint Management suite in the Streamlit Sidebar.
    Orchestrates template application and creation.
    """
    fid = st.session_state.get("form_id", 0)

    st.sidebar.divider()
    st.sidebar.subheader("✨ Blueprint Management")
    st.sidebar.caption("Project-wide standards & custom patterns.")

    # ==========================================================================
    # 1. APPLY TEMPLATE (The Selection Hub)
    # ==========================================================================
    all_templates = load_all_templates()

    if all_templates:
        template_labels = ["--- Select a Template ---"] + [all_templates[t].get("label", t) for t in all_templates]

        selected_label = st.sidebar.selectbox(
            "Load Blueprint",
            options=template_labels,
            key=f"sidebar_template_select_{fid}",
            help="Apply a standardized metadata stack to the current form.",
        )

        if selected_label != "--- Select a Template ---":
            # Map label back to key
            t_key = next(k for k, v in all_templates.items() if v.get("label") == selected_label)

            # The Destructive Overwrite Safety
            with st.sidebar.popover("⚠️ Confirm Overwrite", use_container_width=True):
                st.warning(
                    "This will reset all technical settings and constraints in the form. Variable names are preserved."
                )
                if st.button(
                    "Apply to Active Form",
                    type="primary",
                    use_container_width=True,
                    key=f"apply_t_{fid}",
                ):
                    apply_template_to_state(all_templates[t_key], fid)
                    st.toast(f"Applied: {selected_label}")
                    st.rerun()

    # ==========================================================================
    # 2. SAVE AS BLUEPRINT (The Workshop)
    # ==========================================================================
    st.sidebar.write("")  # Spacer
    with st.sidebar.expander("💾 Create New Blueprint"):
        st.info("Captures all currently filled metadata sections as a reusable template.")

        new_bp_name = st.text_input(
            "Blueprint Name",
            placeholder="e.g., Secure User ID",
            key=f"new_bp_name_{fid}",
        )

        active_data = st.session_state.get("active_v_inputs")

        if not active_data:
            st.error("No active form data detected.")
        else:
            with st.popover("👁️ Preview Blueprint", use_container_width=True):
                # Scrub unique identifiers to generate generic template preview
                preview_data = copy.deepcopy(active_data)
                preview_data.pop("name", None)
                preview_data.pop("alias", None)
                preview_data.pop("description", None)

                st.markdown("**Blueprint Payload Preview:**")
                st.json(preview_data)

                if st.button(
                    "💾 Confirm & Save Blueprint",
                    type="primary",
                    use_container_width=True,
                    key=f"save_bp_{fid}",
                ):
                    if not new_bp_name:
                        st.error("Please provide a name.")
                    else:
                        save_user_template(new_bp_name, active_data)
                        st.success(f"Blueprint '{new_bp_name}' saved!")
                        st.rerun()
