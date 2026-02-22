"""
Description: Streamlit dialog for managing and editing existing dictionary variables.
"""

import copy

import pandas as pd
import streamlit as st

from components.variable_form.handlers import delete_variable
from logic import is_field_visible


@st.dialog("✏️ Dictionary Editor", width="large")
def render_edition_modal():
    """
    Renders a unified editor modal with tabs for Individual and Batch editing.
    """
    variables = st.session_state.get("variables", [])

    if not variables:
        st.info("No variables currently defined in the dictionary.")
        if st.button("Close Manager", use_container_width=True):
            st.rerun()
        return

    tab_indiv, tab_batch = st.tabs(["📝 Individual Edition", "⚙️ Batch Edition"])

    # ==========================================
    # TAB 1: INDIVIDUAL EDITION
    # ==========================================
    with tab_indiv:
        st.markdown(
            "Select an action for the variables currently in your dictionary. Clicking 'Edit' will populate the Variable Form tab."
        )
        st.divider()

        # List container with height to enable internal scrolling for large dictionaries
        with st.container(height=500):
            for idx, var in enumerate(variables):
                col_info, col_edit, col_del = st.columns([3, 1, 1])

                # Label construction: Shows Name and Alias if available
                name = var.get("name", "Unnamed")
                alias = var.get("alias", "")
                label = f"**{name}**" + (f"  \n*{alias}*" if alias else "")

                col_info.markdown(label)

                # Edit Button: Sets state for Variable Form hydration
                if col_edit.button("📝 Edit", key=f"edit_v_{idx}", use_container_width=True):
                    st.session_state["editing_index"] = idx
                    st.session_state["form_id"] += 1
                    st.session_state["cat_rows_hydrated"] = False
                    st.rerun()

                # Delete Button: Integrated with safety popover
                with col_del.popover("🗑️", use_container_width=True):
                    st.warning(f"Permanently delete '{name}'?")
                    if st.button(
                        "Yes, Delete",
                        key=f"del_v_{idx}",
                        type="primary",
                        use_container_width=True,
                    ):
                        delete_variable(idx)

    # ==========================================
    # TAB 2: BATCH EDITION
    # ==========================================
    with tab_batch:
        # Initialize batch editor state
        if "batch_patch" not in st.session_state:
            st.session_state["batch_patch"] = {"root": {}, "nested": {}}
        if "batch_selected_indices" not in st.session_state:
            st.session_state["batch_selected_indices"] = []

        b_tab1, b_tab2, b_tab3 = st.tabs(["1️⃣ Select Variables", "2️⃣ Define Patch", "3️⃣ Review & Apply"])

        # --- PHASE 1: SELECTION MATRIX ---
        with b_tab1:
            st.markdown("### Filter & Select Variables")

            vars_data = []
            for i, v in enumerate(variables):
                vars_data.append(
                    {
                        "var_idx": i,
                        "Select": i in st.session_state["batch_selected_indices"],
                        "Name": v.get("name", ""),
                        "Analytical Type": v.get("analytical_type", ""),
                        "Data Type": v.get("data_type", ""),
                        "Sensitivity": v.get("governance", {}).get("sensitivity", ""),
                    }
                )

            df = pd.DataFrame(vars_data)

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_n = st.text_input("Search by Name", key="batch_search_n").lower()
            with col_f2:
                at_opts = ["All"] + sorted(list(df["Analytical Type"].unique()))
                search_at = st.selectbox("Filter by Analytical Type", options=at_opts)

            if search_n:
                df = df[df["Name"].str.lower().str.contains(search_n)]
            if search_at != "All":
                df = df[df["Analytical Type"] == search_at]

            st.caption(f"Showing {len(df)} matching variables.")

            edited_df = st.data_editor(
                df,
                column_config={
                    "var_idx": None,
                    "Select": st.column_config.CheckboxColumn("Select", default=False),
                },
                disabled=["Name", "Analytical Type", "Data Type", "Sensitivity"],
                hide_index=True,
                use_container_width=True,
                key="batch_data_editor",
            )

            selected_indices = edited_df[edited_df["Select"]]["var_idx"].tolist()
            st.session_state["batch_selected_indices"] = selected_indices

        # --- PHASE 2: OPT-IN PATCH UI ---
        with b_tab2:
            st.markdown("### Define Metadata Updates")
            st.caption("Only fields explicitly toggled ON will be applied.")

            patch_root = {}
            patch_nested = {"governance": {}, "cleaning": {}}

            with st.expander("Technical Baseline", expanded=True):
                c1, c2 = st.columns([1, 3])
                update_at = c1.toggle("Update Analytical Type", key="tgl_at")
                if update_at:
                    patch_root["analytical_type"] = c2.selectbox(
                        "New Analytical Type",
                        options=[
                            "continuous",
                            "discrete",
                            "nominal",
                            "ordinal",
                            "binary",
                            "text",
                            "time_index",
                            "spatial",
                        ],
                        label_visibility="collapsed",
                    )

                c3, c4 = st.columns([1, 3])
                update_dt = c3.toggle("Update Data Type", key="tgl_dt")
                if update_dt:
                    patch_root["data_type"] = c4.selectbox(
                        "New Data Type",
                        options=[
                            "float64",
                            "int64",
                            "string",
                            "bool",
                            "category",
                            "datetime64",
                            "object",
                        ],
                        label_visibility="collapsed",
                    )

            with st.expander("Governance & Privacy", expanded=False):
                c1, c2 = st.columns([1, 3])
                update_sens = c1.toggle("Update Sensitivity", key="tgl_sens")
                if update_sens:
                    patch_nested["governance"]["sensitivity"] = c2.selectbox(
                        "New Sensitivity",
                        options=[
                            "Public",
                            "Internal",
                            "Confidential",
                            "Highly Confidential",
                            "PII",
                            "Restricted",
                        ],
                        label_visibility="collapsed",
                    )

                c3, c4 = st.columns([1, 3])
                update_pii = c3.toggle("Update PII Flag", key="tgl_pii")
                if update_pii:
                    patch_nested["governance"]["pii_flag"] = c4.toggle("Contains PII", value=True)

            with st.expander("Cleaning Strategies", expanded=False):
                c1, c2 = st.columns([1, 3])
                update_miss = c1.toggle("Update Missing Strategy", key="tgl_miss")
                if update_miss:
                    patch_nested["cleaning"]["missing_strategy"] = c2.selectbox(
                        "New Missing Strategy",
                        options=["keep", "drop", "mean", "median", "mode"],
                        label_visibility="collapsed",
                    )

            st.session_state["batch_patch"] = {
                "root": patch_root,
                "nested": patch_nested,
            }

        # --- PHASE 3: COHERENCE CASCADE & COMMIT ---
        with b_tab3:
            st.markdown("### Preview & Commit Changes")

            selected_count = len(st.session_state["batch_selected_indices"])
            patch = st.session_state["batch_patch"]

            if selected_count == 0:
                st.warning("No variables selected. Go to Phase 1.")
            else:
                active_updates = len(patch["root"]) + sum(len(v) for v in patch["nested"].values())
                if active_updates == 0:
                    st.warning("No updates defined. Go to Phase 2.")
                else:
                    st.info(
                        f"Targeting **{selected_count}** variables with **{active_updates}** explicitly defined metadata changes."
                    )

                    st.markdown("#### Coherence Pruning Summary")
                    updated_variables = []
                    total_pruned_keys = 0

                    for idx in st.session_state["batch_selected_indices"]:
                        var = copy.deepcopy(variables[idx])

                        for k, v in patch["root"].items():
                            var[k] = v
                        for section, fields in patch["nested"].items():
                            if fields:
                                if section not in var:
                                    var[section] = {}
                                for k, v in fields.items():
                                    var[section][k] = v

                        new_at = var.get("analytical_type", "continuous")
                        new_dt = var.get("data_type", "float64")

                        pruned_for_this_var = []
                        for section in [
                            "constraints",
                            "cleaning",
                            "governance",
                            "database_mapping",
                        ]:
                            if section in var:
                                keys_to_remove = [
                                    k for k in var[section].keys() if not is_field_visible(k, new_at, new_dt)
                                ]
                                for k in keys_to_remove:
                                    del var[section][k]
                                    pruned_for_this_var.append(k)

                        total_pruned_keys += len(pruned_for_this_var)
                        updated_variables.append((idx, var, pruned_for_this_var))

                    if total_pruned_keys > 0:
                        st.warning(
                            f"⚠️ **Coherence Action:** {total_pruned_keys} incompatible metadata keys will be automatically pruned."
                        )
                        with st.expander("View Pruning Details"):
                            for idx, var, pruned in updated_variables:
                                if pruned:
                                    st.write(f"- **{var.get('name')}**: Pruned `{', '.join(pruned)}`")
                    else:
                        st.success("✅ No coherence conflicts detected.")

                    if st.button(
                        "🚀 Confirm & Apply Batch Update",
                        type="primary",
                        use_container_width=True,
                    ):
                        for idx, new_var, _ in updated_variables:
                            st.session_state["variables"][idx] = new_var

                        st.session_state["batch_selected_indices"] = []
                        st.session_state["batch_patch"] = {"root": {}, "nested": {}}
                        st.success("Batch update applied successfully!")
                        st.rerun()
