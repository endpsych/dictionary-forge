"""
Description: Advanced Variable Cloning Modal with 3-pane layout.
"""

import copy

import streamlit as st


@st.dialog("📑 Variable Cloning", width="large")
def render_cloning_modal():
    if not st.session_state.get("variables"):
        st.info("No variables in dictionary to clone.")
        return

    # 1. TOP ZONE: 3-Pane Inspection
    col_nav, col_compare, col_action = st.columns([0.8, 1.2, 1.0], gap="medium")

    # --- PANE 1: THE LIBRARY ---
    with col_nav:
        st.markdown("### 📋 Library")
        with st.container(height=550, border=True):
            search_query = st.text_input(
                "Search",
                placeholder="🔍 Search...",
                label_visibility="collapsed",
                key="cl_search",
            )
            filtered = [v for v in st.session_state["variables"] if search_query.lower() in v["name"].lower()]

            if filtered:
                selected_source_name = st.radio(
                    "Select Source",
                    options=[v["name"] for v in filtered],
                    label_visibility="collapsed",
                    key="cl_radio",
                )
                source_var = next(v for v in st.session_state["variables"] if v["name"] == selected_source_name)
            else:
                st.caption("No matches.")
                source_var = None

    # --- PANE 2: VISUAL COMPARISON ---
    with col_compare:
        st.markdown("### ⚖️ Comparison")
        if source_var:
            current_form = st.session_state.get("active_v_inputs", {})

            def compare_row(label, source_val, current_val):
                c1, c2 = st.columns(2)
                diff = source_val != current_val
                color = "#ff4b4b" if diff else "#09ab3b"
                c1.caption(f"**{label} (Source)**")
                c1.code(str(source_val) if source_val else "None")
                c2.caption(f"**{label} (Form)**")
                c2.markdown(
                    f"<div style='color:{color}; font-family:monospace; font-size:12px;'>{current_val if current_val else 'None'}</div>",
                    unsafe_allow_html=True,
                )
                st.divider()

            with st.container(height=550, border=True):
                compare_row("Name", source_var.get("name"), current_form.get("name"))
                compare_row("Role", source_var.get("role"), current_form.get("role"))
                compare_row(
                    "Data Type",
                    source_var.get("data_type"),
                    current_form.get("data_type"),
                )

                s_gov = source_var.get("governance", {})
                f_gov = current_form.get("governance", {})
                compare_row("Sensitivity", s_gov.get("sensitivity"), f_gov.get("sensitivity"))
                compare_row("PII", s_gov.get("pii_flag"), f_gov.get("pii_flag"))

    # --- PANE 3: DIRECT COMMIT & BATCH ENGINE ---
    with col_action:
        st.markdown("### ⚙️ Configuration")
        with st.container(height=550, border=True):
            mode = st.radio(
                "Cloning Mode",
                ["Direct Commit", "Bulk Generation"],
                horizontal=True,
                key="cl_mode",
            )
            st.divider()

            if mode == "Direct Commit":
                st.markdown("**New Identity Definition**")
                new_name = st.text_input(
                    "New Variable Name",
                    value=f"{source_var['name']}_copy",
                    key="cl_new_name",
                )
                new_alias = st.text_input(
                    "New Alias",
                    value=f"{source_var.get('alias', '')} (Copy)",
                    key="cl_new_alias",
                )
                new_desc = st.text_area(
                    "New Description",
                    value=source_var.get("description", ""),
                    key="cl_new_desc",
                )

                st.write("")
                st.markdown("**Inheritance settings**")
                clone_tech = st.checkbox("Inherit Technical (Type/Role)", value=True, key="cl_inherit_tech")
                clone_gov = st.checkbox(
                    "Inherit Governance (PII/Sensitivity)",
                    value=True,
                    key="cl_inherit_gov",
                )

                if st.button("🚀 Create & Commit", type="primary", use_container_width=True):
                    # Validation
                    existing_names = [v["name"] for v in st.session_state["variables"]]
                    if not new_name.strip():
                        st.error("Name is required.")
                    elif new_name in existing_names:
                        st.error(f"'{new_name}' already exists in dictionary.")
                    else:
                        # Build new entry
                        new_entry = {
                            "name": new_name.strip(),
                            "alias": new_alias.strip(),
                            "description": new_desc.strip(),
                        }
                        if clone_tech:
                            new_entry.update(
                                {
                                    "analytical_type": source_var.get("analytical_type"),
                                    "data_type": source_var.get("data_type"),
                                    "role": source_var.get("role"),
                                }
                            )
                        if clone_gov:
                            new_entry["governance"] = copy.deepcopy(source_var.get("governance", {}))

                        st.session_state["variables"].append(new_entry)
                        st.success(f"Variable '{new_name}' committed to dictionary!")
                        st.rerun()

            else:
                # Bulk Generation Logic
                st.markdown("**Bulk Suffix/Prefix Engine**")
                prefix = st.text_input("Prefix", value="v2_", key="cl_pre")
                suffix = st.text_input("Suffix", value="", key="cl_suf")
                count = st.number_input("Count", min_value=1, max_value=20, value=1, key="cl_count")

                if st.button("👯 Generate Clones", type="primary", use_container_width=True):
                    for i in range(count):
                        new_entry = copy.deepcopy(source_var)
                        final_name = f"{prefix}{source_var['name']}{suffix}"
                        if count > 1:
                            final_name += f"_{i + 1}"
                        new_entry["name"] = final_name
                        st.session_state["variables"].append(new_entry)
                    st.success(f"Added {count} variants to dictionary.")
                    st.rerun()

    st.divider()
    if st.button("Close", use_container_width=True):
        st.rerun()
