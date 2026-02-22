"""
Description: Cleaning UI section for missing data strategies and outlier management.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field


def render_cleaning_section(nested_sections, current_at, current_dt, v_inputs, edit_data=None):
    """
    Renders the Cleaning section with a balanced two-column layout.
    Prioritizes Ground Truth (edit_data) to ensure coherence with Templates and Ledger.
    """
    if "cleaning" not in nested_sections:
        return

    # Extract section-specific ground truth
    edit_section = edit_data.get("cleaning", {}) if edit_data else {}
    cleaning_data = {}
    fields = nested_sections["cleaning"].get("fields", [])

    # Helper to find specific field definitions from the master schema
    def get_f(name):
        return next((f for f in fields if f["name"] == name), None)

    with st.container(border=True):
        col_left, col_right = st.columns(2)

        # --- COLUMN 1: DATA COMPLETION (Missing Strategy & Standardization) ---
        with col_left:
            # 1. Missing Strategy
            f_missing = get_f("missing_strategy")
            if f_missing:
                res_missing = render_input_field(
                    f_missing,
                    prefix="cleaning",
                    edit_value=edit_section.get("missing_strategy"),
                )
                if res_missing:
                    cleaning_data["missing_strategy"] = res_missing

            # 2. Standardization
            f_std = get_f("standardization") or {
                "name": "standardization",
                "dtype": "enum",
                "options": ["none", "z-score", "min-max", "robust"],
            }
            res_std = render_input_field(f_std, prefix="cleaning", edit_value=edit_section.get("standardization"))
            # Ensure we only commit if it's a meaningful selection
            if res_std and res_std != "none":
                cleaning_data["standardization"] = res_std

        # --- COLUMN 2: ANOMALY MANAGEMENT (Outlier Strategy & Threshold) ---
        with col_right:
            # 1. Outlier Strategy
            f_outlier = get_f("outlier_strategy") or {
                "name": "outlier_strategy",
                "dtype": "enum",
            }
            # Ensure standard options are available if missing from schema
            if not f_outlier.get("options"):
                f_outlier["options"] = ["keep", "clip", "drop", "flag"]

            res_outlier = render_input_field(
                f_outlier,
                prefix="cleaning",
                edit_value=edit_section.get("outlier_strategy"),
            )
            if res_outlier:
                cleaning_data["outlier_strategy"] = res_outlier

            # 2. Outlier Threshold (Conditional visibility based on strategy)
            if res_outlier and res_outlier != "keep":
                f_thresh = get_f("outlier_threshold") or {
                    "name": "outlier_threshold",
                    "dtype": "number",
                }
                res_thresh = render_input_field(
                    f_thresh,
                    prefix="cleaning",
                    edit_value=edit_section.get("outlier_threshold"),
                )
                if res_thresh is not None:
                    cleaning_data["outlier_threshold"] = res_thresh

            # 3. Regex Pattern (Conditional visibility for Strings)
            # This is often used for cleaning/validation of string data
            if current_dt == "string":
                res_regex = render_input_field(
                    {"name": "regex_pattern", "dtype": "string"},
                    prefix="cleaning",
                    data_type=current_dt,
                    edit_value=edit_section.get("regex_pattern"),
                )
                if res_regex:
                    cleaning_data["regex_pattern"] = res_regex

    # Commit local section data to the main input collection
    if cleaning_data:
        v_inputs["cleaning"] = cleaning_data
