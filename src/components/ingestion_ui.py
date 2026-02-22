"""
Description: UI component for bulk ingestion of variables via CSV or Excel.
"""

import pandas as pd
import streamlit as st


@st.dialog("📥 Bulk Variable Ingestion", width="large")
def render_ingestion_ui():
    """
    Renders the file uploader and extraction logic for bulk variable ingestion.
    """
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
                target_col = st.selectbox("Select the column containing Variable Names:", options=df.columns)
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
