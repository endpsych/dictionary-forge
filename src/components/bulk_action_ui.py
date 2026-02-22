"""
Description: Mass governance and batch edition UI for Dictionary Forge.
"""

import copy

import pandas as pd
import streamlit as st

from logic import is_field_visible


@st.dialog("⚙️ Batch Editor", width="large")
def render_bulk_action_ui():
    """Renders the 3-phase Batch Editor for safe, mass variable updates."""

    if not st.session_state.get("variables"):
        st.warning("No variables in the dictionary to edit.")
        return

    # Initialize batch editor state
    if "batch_patch" not in st.session_state:
        st.session_state["batch_patch"] = {"root": {}, "nested": {}}
    if "batch_selected_indices" not in st.session_state:
        st.session_state["batch_selected_indices"] = []

    tab1, tab2, tab3 = st.tabs(["1️⃣ Select Variables", "2️⃣ Define Patch", "3️⃣ Review & Apply"])

    # --- PHASE 1: SELECTION MATRIX ---
    with tab1:
        st.markdown("### Filter & Select Variables")

        # Build DataFrame for Selection
        vars_data = []
        for i, v in enumerate(st.session_state["variables"]):
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

        # Filter controls
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_n = st.text_input("Search by Name", key="batch_search_n").lower()
        with col_f2:
            at_opts = ["All"] + sorted(list(df["Analytical Type"].unique()))
            search_at = st.selectbox("Filter by Analytical Type", options=at_opts)

        # Apply filters
        if search_n:
            df = df[df["Name"].str.lower().str.contains(search_n)]
        if search_at != "All":
            df = df[df["Analytical Type"] == search_at]

        st.caption(f"Showing {len(df)} matching variables.")

        # Data Editor for Selection
        edited_df = st.data_editor(
            df,
            column_config={
                "var_idx": None,  # Hide internal index safely
                "Select": st.column_config.CheckboxColumn("Select", default=False),
            },
            disabled=["Name", "Analytical Type", "Data Type", "Sensitivity"],
            hide_index=True,
            use_container_width=True,
            key="batch_data_editor",
        )

        # Update selection state
        selected_indices = edited_df[edited_df["Select"]]["var_idx"].tolist()
        st.session_state["batch_selected_indices"] = selected_indices

    # --- PHASE 2: OPT-IN PATCH UI ---
    with tab2:
        st.markdown("### Define Metadata Updates")
        st.caption("Only fields explicitly toggled ON will be applied to the selected variables.")

        patch_root = {}
        patch_nested = {"governance": {}, "cleaning": {}}

        # Root Fields
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

        # Governance Fields
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

        # Cleaning Fields
        with st.expander("Cleaning Strategies", expanded=False):
            c1, c2 = st.columns([1, 3])
            update_miss = c1.toggle("Update Missing Strategy", key="tgl_miss")
            if update_miss:
                patch_nested["cleaning"]["missing_strategy"] = c2.selectbox(
                    "New Missing Strategy",
                    options=["keep", "drop", "mean", "median", "mode"],
                    label_visibility="collapsed",
                )

        st.session_state["batch_patch"] = {"root": patch_root, "nested": patch_nested}

    # --- PHASE 3: COHERENCE CASCADE & COMMIT ---
    with tab3:
        st.markdown("### Preview & Commit Changes")

        selected_count = len(st.session_state["batch_selected_indices"])
        patch = st.session_state["batch_patch"]

        if selected_count == 0:
            st.warning("No variables selected. Go to Phase 1.")
            return

        active_updates = len(patch["root"]) + sum(len(v) for v in patch["nested"].values())
        if active_updates == 0:
            st.warning("No updates defined. Go to Phase 2 and toggle fields to update.")
            return

        st.info(
            f"Targeting **{selected_count}** variables with **{active_updates}** explicitly defined metadata changes."
        )

        # Generate Diff / Coherence Engine execution
        st.markdown("#### Coherence Pruning Summary")

        updated_variables = []
        total_pruned_keys = 0

        for idx in st.session_state["batch_selected_indices"]:
            var = copy.deepcopy(st.session_state["variables"][idx])

            # Apply Root Patch
            for k, v in patch["root"].items():
                var[k] = v

            # Apply Nested Patch
            for section, fields in patch["nested"].items():
                if fields:
                    if section not in var:
                        var[section] = {}
                    for k, v in fields.items():
                        var[section][k] = v

            # COHERENCE CASCADE: Prune invalid metadata keys based on new AT/DT
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
                    keys_to_remove = []
                    for k in var[section].keys():
                        if not is_field_visible(k, new_at, new_dt):
                            keys_to_remove.append(k)
                    for k in keys_to_remove:
                        del var[section][k]
                        pruned_for_this_var.append(k)

            total_pruned_keys += len(pruned_for_this_var)
            updated_variables.append((idx, var, pruned_for_this_var))

        # Display Diff
        if total_pruned_keys > 0:
            st.warning(
                f"⚠️ **Coherence Action:** {total_pruned_keys} incompatible metadata keys will be automatically pruned across the selected variables to maintain dictionary integrity."
            )
            with st.expander("View Pruning Details"):
                for idx, var, pruned in updated_variables:
                    if pruned:
                        st.write(f"- **{var.get('name')}**: Pruned `{', '.join(pruned)}`")
        else:
            st.success("✅ No coherence conflicts detected. All patches are safe to apply.")

        # Commit Button
        if st.button("🚀 Confirm & Apply Batch Update", type="primary", use_container_width=True):
            # Commit to ledger
            for idx, new_var, _ in updated_variables:
                st.session_state["variables"][idx] = new_var

            # Clear state
            st.session_state["batch_selected_indices"] = []
            st.session_state["batch_patch"] = {"root": {}, "nested": {}}

            st.success("Batch update applied successfully!")
            st.rerun()
