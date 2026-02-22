"""
Description: Streamlit dialog component for centralized data dictionary exports.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from components.export_utils import (
    generate_csv,
    generate_excel,
    generate_json,
    generate_yaml,
)
from logic import flatten_json, generate_sql_script


@st.dialog("📤 Export Data Dictionary", width="large")
def render_export_modal():
    """
    Renders the centralized export menu.
    Calculates binary buffers only when the modal is active.
    """
    vars_list = st.session_state.get("variables", [])
    project_info = st.session_state.get("project_info", {})

    if not vars_list:
        st.warning("No variables available to export.")
        return

    st.markdown(f"**Project:** {project_info.get('project_name', 'Untitled')}")
    st.markdown(f"**Variable Count:** {len(vars_list)}")
    st.divider()

    # --- Data Preparation ---
    # Prepare the comprehensive export object
    export_obj = {
        "project_metadata": project_info,
        "generated_at": datetime.now().isoformat(),
        "variables": vars_list,
    }

    # Prepare flattened DataFrame for tabular formats
    df_preview = pd.DataFrame([flatten_json(v) for v in vars_list])

    # --- UI Grid for Downloads ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🛠️ Developer Formats")

        # 1. YAML
        yaml_data = generate_yaml(export_obj)
        st.download_button(
            label="Download YAML",
            data=yaml_data,
            file_name="data_dictionary.yaml",
            mime="text/yaml",
            use_container_width=True,
        )
        st.caption("Best for human-readable configuration and version control.")

        # 2. JSON
        json_data = generate_json(export_obj)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="data_dictionary.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption("Standard format for API integration and programmatic ingestion.")

        # 3. SQL
        sql_data = generate_sql_script(vars_list)
        st.download_button(
            label="Download SQL",
            data=sql_data,
            file_name="schema.sql",
            mime="text/plain",
            use_container_width=True,
        )
        st.caption("PostgreSQL DDL script for database schema initialization.")

    with col2:
        st.markdown("### 📊 Tabular Formats")

        # 4. Excel
        excel_data = generate_excel(df_preview, project_info)
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name="data_dictionary.xlsx",
            use_container_width=True,
        )
        st.caption("Formatted workbook for business stakeholders and documentation.")

        # 5. CSV
        csv_data = generate_csv(df_preview)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="data_dictionary.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("Raw tabular data for PowerBI, Tableau, or Python/R analysis.")

    st.divider()
    st.info("💡 Tip: All exports include governance metadata and compliance scopes.")
