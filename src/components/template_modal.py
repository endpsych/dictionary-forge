"""
Description: Streamlit dialog for the Variable Template Hub.
"""

import copy

import streamlit as st

from logic.templates import (
    delete_template,
    get_template_list,
    load_template_data,
    save_template_data,
)


@st.dialog("💾 Variable Template Hub", width="large")
def render_template_modal():

    # 1. Global CSS Injection for the Half-Height Overwrite Frame
    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div.slim-frame) {
            padding: 0px 10px !important;
            min-height: 34px !important;
            height: 34px !important;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: rgba(255, 255, 255, 0.05);
        }
        div.slim-frame [data-testid="stVerticalBlock"] { gap: 0px !important; }
        div.slim-frame .stCheckbox { margin-bottom: -15px !important; margin-top: -5px !important; }
        .footer-label { margin-top: 6px; font-weight: bold; font-size: 0.9rem; }
        </style>
    """,
        unsafe_allow_html=True,
    )

    tab_load, tab_save = st.tabs(["📂 Load from Library", "💾 Save Current Configuration"])

    with tab_load:
        templates = get_template_list()
        if not templates:
            st.info("No templates found in the library.")
        else:
            col_nav, col_preview, col_json = st.columns([0.8, 1.2, 1.2], gap="small")

            with col_nav:
                st.markdown("### 📋 Library")
                with st.container(height=400, border=True):
                    search_query = st.text_input(
                        "Search",
                        placeholder="🔍 Search...",
                        label_visibility="collapsed",
                    )
                    filtered = [t for t in templates if search_query.lower() in t.lower()]

                    if filtered:
                        selected_t = st.radio(
                            "Select:",
                            options=filtered,
                            label_visibility="collapsed",
                            key="t_hub_radio",
                        )
                    else:
                        st.caption("No results.")
                        selected_t = templates[0]

            with col_preview:
                t_data = load_template_data(selected_t)
                st.markdown(f"### 🔍 Preview: {selected_t}")
                with st.container(height=400, border=True):
                    st.markdown("**Description**")
                    st.caption(t_data.get("description", "No description provided."))
                    st.divider()
                    st.markdown("**Technical Baseline**")
                    st.write(f"- AT: `{t_data.get('analytical_type', 'N/A')}`")
                    st.write(f"- DT: `{t_data.get('data_type', 'N/A')}`")
                    st.write(f"- Role: `{t_data.get('role', 'N/A')}`")
                    st.divider()
                    st.markdown("**Governance**")
                    gov = t_data.get("governance", {})
                    st.write(f"- PII: `{gov.get('pii_flag', 'N/A')}`")
                    st.write(f"- Sensitivity: `{gov.get('sensitivity', 'N/A')}`")

            with col_json:
                st.markdown("### 📄 JSON Schema")
                with st.container(height=400, border=True):
                    st.json(t_data)

            st.write("")

            # 3. BOTTOM ZONE: Ultra-Slim Action Bar
            act_col1, act_col_slim, act_col_btn = st.columns([0.5, 2.5, 1.0])

            with act_col1:
                with st.popover("🗑️ Delete", use_container_width=True):
                    st.error(f"Delete '{selected_t}'?")
                    if st.button("Confirm", type="primary", use_container_width=True):
                        delete_template(selected_t)
                        st.rerun()

            with act_col_slim:
                with st.container(border=True):
                    st.markdown('<div class="slim-frame"></div>', unsafe_allow_html=True)
                    t_col1, t_col2, t_col3, t_col4 = st.columns([0.8, 1, 1, 1.2])

                    t_col1.markdown('<p class="footer-label">Overwrite:</p>', unsafe_allow_html=True)
                    ov_name = t_col2.checkbox("Name", value=False)
                    ov_alias = t_col3.checkbox("Alias", value=False)
                    ov_desc = t_col4.checkbox("Description", value=False)

            with act_col_btn:
                if st.button("🚀 Load Template", type="primary", use_container_width=True):
                    st.session_state["editing_index"] = None
                    st.session_state["cat_rows_hydrated"] = False

                    hydrate_payload = copy.deepcopy(t_data)
                    skipped_fields = []

                    # Overwrite Guards
                    if not ov_name:
                        hydrate_payload.pop("name", None)
                        skipped_fields.append("Name")
                    if not ov_alias:
                        hydrate_payload.pop("alias", None)
                        skipped_fields.append("Alias")
                    if not ov_desc:
                        hydrate_payload.pop("description", None)
                        skipped_fields.append("Description")

                    # ==========================================================
                    # THE DATA MISMATCH SANITIZER
                    # Forces legacy template names to match Streamlit's strict logic
                    # ==========================================================
                    at_map = {
                        "categorical": "nominal",
                        "boolean": "binary",
                        "numeric": "continuous",
                        "datetime": "time_index",
                    }
                    dt_map = {
                        "boolean": "bool",
                        "float": "float64",
                        "integer": "int64",
                        "string": "string",
                        "category": "category",
                    }
                    role_map = {
                        "dimension": "feature",
                        "measure": "target",
                        "identifier": "id",
                    }

                    # 1. Sanitize Analytical Type
                    raw_at = str(hydrate_payload.get("analytical_type", "")).lower()
                    hydrate_payload["analytical_type"] = at_map.get(raw_at, raw_at)

                    # 2. Sanitize Data Type
                    raw_dt = str(hydrate_payload.get("data_type", "")).lower()
                    hydrate_payload["data_type"] = dt_map.get(raw_dt, raw_dt)

                    # 3. Sanitize Role
                    raw_role = str(hydrate_payload.get("role", "")).lower()
                    hydrate_payload["role"] = role_map.get(raw_role, raw_role)

                    # 4. Standardize legacy constraint keys
                    if "constraints" in hydrate_payload:
                        if "is_nullable" in hydrate_payload["constraints"]:
                            hydrate_payload["constraints"]["nullable"] = hydrate_payload["constraints"].pop(
                                "is_nullable"
                            )

                    # Hand off to __init__.py Orchestrator
                    st.session_state["hydration_report"] = (
                        "Complete template applied."
                        if not skipped_fields
                        else f"Metadata applied ({', '.join(skipped_fields)} preserved)."
                    )
                    st.session_state["loaded_template"] = hydrate_payload
                    st.rerun()

    # --- TAB 2: SAVE ---
    with tab_save:
        current_data = st.session_state.get("active_v_inputs", {})
        if not current_data.get("name"):
            st.warning("Define a Variable Name before saving.")
        else:
            with st.form("save_template_form"):
                new_name = st.text_input("Template Name", placeholder="e.g., Secure_ID")
                template_desc = st.text_area("Description", value=current_data.get("description", ""))
                if st.form_submit_button("Save to Library", use_container_width=True):
                    if new_name:
                        safe_name = (
                            "".join([c for c in new_name if c.isalnum() or c in (" ", "_")]).strip().replace(" ", "_")
                        )
                        save_data = copy.deepcopy(current_data)
                        save_data["description"] = template_desc
                        save_template_data(safe_name, save_data)
                        st.success(f"Template '{safe_name}' saved!")
                        st.rerun()

    st.divider()
    if st.button("Close Hub", use_container_width=True):
        st.rerun()
