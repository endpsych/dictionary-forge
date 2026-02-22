"""
Description: Database Mapping UI section for physical storage definitions.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field


def render_database_mapping_section(current_at, current_dt, v_inputs, edit_data=None):
    """
    Renders the physical database mapping configuration.
    Defines where this variable lives in the downstream data warehouse.
    Prioritizes Ground Truth (edit_data) to ensure coherence with Templates and Ledger.
    """
    # Extract section-specific ground truth
    edit_db = edit_data.get("database_mapping", {}) if edit_data else {}

    with st.container(border=True):
        db_data = {}

        # Weighted column layout giving more space to text inputs than the toggle
        c1, c2, c3 = st.columns([2, 2, 1])

        with c1:
            res_table = render_input_field(
                {"name": "target_table", "dtype": "string"},
                prefix="database",
                edit_value=edit_db.get("target_table"),
            )
            if res_table:
                db_data["target_table"] = res_table

        with c2:
            res_col = render_input_field(
                {"name": "target_column", "dtype": "string"},
                prefix="database",
                edit_value=edit_db.get("target_column"),
            )
            if res_col:
                db_data["target_column"] = res_col

        with c3:
            res_pk = render_input_field(
                {"name": "is_primary_key", "dtype": "boolean"},
                prefix="database",
                edit_value=edit_db.get("is_primary_key"),
            )
            if res_pk is not None:
                db_data["is_primary_key"] = res_pk

        # Persist to master collection if data exists
        if db_data:
            v_inputs["database_mapping"] = db_data
