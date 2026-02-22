"""
Description: Identification UI section for technical and business naming.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field


def render_identification_section(field_defs, v_inputs, edit_data=None):
    """
    Renders technical and business naming conventions.
    Prioritizes Ground Truth (edit_data) to ensure coherence with Templates and Ledger.
    """
    with st.container(border=True):
        c1, c2 = st.columns(2)

        with c1:
            v_inputs["name"] = render_input_field(
                field_defs.get("name"),
                edit_value=edit_data.get("name") if edit_data else "",
            )

        with c2:
            v_inputs["alias"] = render_input_field(
                field_defs.get("alias"),
                edit_value=edit_data.get("alias") if edit_data else "",
            )

        v_inputs["description"] = render_input_field(
            field_defs.get("description"),
            edit_value=edit_data.get("description") if edit_data else "",
        )
