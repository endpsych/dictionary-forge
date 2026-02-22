"""
Description: Visualization UI section for chart preferences and color mapping.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field


def render_visualization_section(nested_sections, current_at, current_dt, v_inputs, edit_data=None):
    """
    Renders chart types, color palettes, and binning preferences.
    Synchronizes selections with the global v_inputs for dictionary generation.
    """
    if "visualization" not in nested_sections:
        return

    edit_section = edit_data.get("visualization", {}) if edit_data else {}
    visualization_data = {}
    fields = nested_sections["visualization"].get("fields", [])

    with st.container(border=True):
        # Header removed to eliminate redundancy with the Orchestrator's Accordion bar.

        # Standardized 3-column distribution for uniform fields (Chart Type, Color, etc.)
        cols = st.columns(3)
        for i, f in enumerate(fields):
            with cols[i % 3]:
                # Render using the centralized widget library to maintain consistency
                res = render_input_field(
                    f,
                    prefix="visualization",
                    analytical_type=current_at,
                    data_type=current_dt,
                    edit_value=edit_section.get(f["name"]),
                )

                # Filter out empty or default false values before persisting to metadata
                if res not in [None, "", False, []]:
                    visualization_data[f["name"]] = res

    # Persist the collected section data to the master input dictionary
    if visualization_data:
        v_inputs["visualization"] = visualization_data
