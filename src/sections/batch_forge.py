"""
Description: Unified UI component for the Batch Forge.
"""

import pandas as pd
import streamlit as st

from logic import generate_batch_dataframe, hydrate_row_from_flat
from logic.templates import get_template_list, load_template_data


@st.dialog("🚀 Batch Forge", width="large")
def render_batch_forge():
    st.caption("Mass-generate variables from a template baseline or ingest from existing datasets.")

    tab_template, tab_dataset = st.tabs(["📋 From Template", "📥 From Dataset/List"])

    # --- TAB 1: FROM TEMPLATE ---
    with tab_template:
        st.markdown(
            "Use this tool to rapidly generate multiple variables that share the same foundational metadata. "
            "Choose a template below to pre-fill the data grid, customize specific fields (such as the variable name), "
            "and commit the batch to your dictionary."
        )

        templates = get_template_list()

        if not templates:
            st.warning("No templates found in the library. Please create a template in the Variable Form first.")
        else:
            col1, col2 = st.columns([2, 1])

            with col1:
                t_options = ["--- Select Template ---"] + templates
                selected_t = st.selectbox("Select Template", options=t_options)

            with col2:
                num_vars = st.number_input("How many variables?", min_value=1, max_value=100, value=5)

            if selected_t != "--- Select Template ---":
                template_data = load_template_data(selected_t)

                template_desc = template_data.get("description", "No description available for this template.")
                st.info(f"**Template Description:** {template_desc}")

                # State Management for the Grid
                state_key = f"batch_df_{selected_t}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = generate_batch_dataframe(template_data, num_vars)
                elif len(st.session_state[state_key]) != num_vars:
                    current_df = st.session_state[state_key]
                    if num_vars > len(current_df):
                        new_rows = generate_batch_dataframe(template_data, num_vars - len(current_df))
                        new_rows["Row #"] = range(len(current_df) + 1, num_vars + 1)
                        st.session_state[state_key] = pd.concat([current_df, new_rows], ignore_index=True)
                    else:
                        st.session_state[state_key] = current_df.head(num_vars)

                # Focus Mode
                focus = st.multiselect(
                    "Column Focus Mode",
                    options=[
                        "Identification",
                        "Technical",
                        "Constraints",
                        "Cleaning",
                        "Governance",
                        "Database",
                    ],
                    default=["Identification", "Technical"],
                )

                all_cols = st.session_state[state_key].columns.tolist()

                visible_cols = ["Row #"]
                if "Identification" in focus:
                    visible_cols += ["name", "alias", "description"]
                if "Technical" in focus:
                    visible_cols += ["analytical_type", "data_type", "role"]
                if "Constraints" in focus:
                    visible_cols += [c for c in all_cols if c.startswith("constraints_")]
                if "Cleaning" in focus:
                    visible_cols += [c for c in all_cols if c.startswith("cleaning_")]
                if "Governance" in focus:
                    visible_cols += [c for c in all_cols if c.startswith("governance_")]
                if "Database" in focus:
                    visible_cols += [c for c in all_cols if c.startswith("database_mapping_")]

                if len(visible_cols) == 1:
                    st.info("Select at least one focus mode to view the grid.")
                else:
                    column_configuration = {"Row #": st.column_config.NumberColumn("Row #", disabled=True, format="%d")}

                    # The Grid
                    edited_df = st.data_editor(
                        st.session_state[state_key],
                        column_order=visible_cols,
                        column_config=column_configuration,
                        use_container_width=True,
                        num_rows="dynamic",
                        key=f"batch_forge_grid_{selected_t}",
                    )

                    # Commit Logic
                    st.write("")
                    if st.button(
                        "🔥 Commit Batch to Dictionary",
                        type="primary",
                        use_container_width=True,
                    ):
                        new_vars = []

                        for _, row in edited_df.iterrows():
                            if pd.notna(row["name"]) and str(row["name"]).strip() != "":
                                new_vars.append(hydrate_row_from_flat(row.to_dict()))

                        if new_vars:
                            st.session_state["variables"].extend(new_vars)
                            del st.session_state[state_key]
                            st.success(f"Successfully added {len(new_vars)} variables to the dictionary.")
                            st.rerun()
                        else:
                            st.error("No valid variables to commit. Ensure the 'name' column is filled out.")

    # --- TAB 2: FROM DATASET/LIST ---
    with tab_dataset:
        st.markdown("Upload an existing dataset or a variable list to quickly populate your dictionary queue.")

        if "pending_variables" not in st.session_state:
            st.session_state["pending_variables"] = []

        uploaded_file = st.file_uploader("Upload Data (.csv, .xlsx)", type=["csv", "xlsx"])

        if uploaded_file:
            try:
                # Parse file based on extension
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.success(f"Loaded: {df.shape[1]} columns, {df.shape[0]} rows.")

                # Extraction Strategy Selection
                ext_strategy = st.radio(
                    "Extraction Method:",
                    options=[
                        "Extract Column Headers (Raw Dataset)",
                        "Extract from a Specific Column (Data Dictionary)",
                    ],
                    horizontal=True,
                )

                extracted_names = []

                if ext_strategy == "Extract Column Headers (Raw Dataset)":
                    extracted_names = df.columns.tolist()
                else:
                    target_col = st.selectbox(
                        "Select the column containing Variable Names:",
                        options=df.columns,
                    )
                    if target_col:
                        extracted_names = df[target_col].dropna().astype(str).tolist()

                # Submission and Deduplication Logic
                st.write("")
                if st.button("➕ Queue Extracted Variables", type="primary"):
                    existing_defined = [v["name"] for v in st.session_state.get("variables", [])]

                    added_count = 0
                    for name in extracted_names:
                        clean_name = str(name).strip()
                        if (
                            clean_name
                            and clean_name not in st.session_state["pending_variables"]
                            and clean_name not in existing_defined
                        ):
                            st.session_state["pending_variables"].append(clean_name)
                            added_count += 1

                    if added_count > 0:
                        st.success(f"Added {added_count} variables to the queue.")
                        st.rerun()
                    else:
                        st.warning("No new variables added. All extracted names are already in the queue or defined.")

            except Exception as e:
                st.error(f"Error parsing file: {e}")

        # --- QUEUE MANAGEMENT UI ---
        if st.session_state["pending_variables"]:
            st.write("")
            with st.container(border=True):
                st.markdown(f"### ⏳ Pending Queue ({len(st.session_state['pending_variables'])})")

                # Display queue in an easy-to-read format
                cols = st.columns(4)
                for i, var_name in enumerate(st.session_state["pending_variables"]):
                    cols[i % 4].code(var_name)

                st.write("")
                if st.button("🗑️ Clear Queue", use_container_width=True):
                    st.session_state["pending_variables"] = []
                    st.rerun()
