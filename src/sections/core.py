"""
Description: Core Identification and Technical Configuration UI sections.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field
from constants import TOOLTIP_DEFINITIONS
from logic import get_filtered_roles


def render_identification_section(field_defs, v_inputs, edit_data=None):
    """Renders technical and business naming conventions."""
    with st.container(border=True):
        st.markdown("🆔 **IDENTIFICATION**")
        c1, c2 = st.columns(2)
        with c1:
            v_inputs["name"] = render_input_field(
                field_defs.get("name"),
                edit_value=edit_data.get("name") if edit_data else None,
            )
        with c2:
            v_inputs["alias"] = render_input_field(
                field_defs.get("alias"),
                edit_value=edit_data.get("alias") if edit_data else None,
            )

        v_inputs["description"] = render_input_field(
            field_defs.get("description"),
            edit_value=edit_data.get("description") if edit_data else None,
        )


def render_technical_config_section(field_defs, v_inputs, edit_data=None):
    """
    Renders core technical settings.
    Functional role restriction is enforced here via logic.py.
    """
    fid = st.session_state["form_id"]

    with st.container(border=True):
        st.markdown("⚙️ **TECHNICAL CONFIG**")
        c1, c2, c3 = st.columns(3)

        # 1. Analytical Type Selection
        at_def = field_defs.get("analytical_type")
        if "time_index" not in at_def["options"]:
            at_def["options"].append("time_index")

        at_index = 0
        if edit_data:
            try:
                at_index = at_def["options"].index(edit_data.get("analytical_type"))
            except ValueError:
                pass

        with c1:
            at_help = TOOLTIP_DEFINITIONS.get("analytical_type", {}).get("help", "Defines the mathematical nature.")
            current_at = st.selectbox(
                "Analytical Type *",
                options=at_def["options"],
                index=at_index,
                key=f"v_at_{fid}",
                help=at_help,
            )
            v_inputs["analytical_type"] = current_at
            if current_at in TOOLTIP_DEFINITIONS.get("analytical_type", {}):
                st.info(TOOLTIP_DEFINITIONS["analytical_type"][current_at])

        # 2. Data Type Selection
        with c2:
            current_dt = render_input_field(
                {"name": "data_type", "dtype": "enum"},
                analytical_type=current_at,
                edit_value=edit_data.get("data_type") if edit_data else None,
            )
            v_inputs["data_type"] = current_dt

        # 3. Functional Role Selection (Reactive Filter)
        with c3:
            valid_roles = get_filtered_roles(current_at, current_dt)
            edit_role = edit_data.get("role") if edit_data else None

            # Fallback if previous role is no longer valid under new AT/DT constraints
            if edit_role not in valid_roles:
                edit_role = "feature"

            v_inputs["role"] = render_input_field(
                {"name": "role", "dtype": "enum", "options": valid_roles},
                analytical_type=current_at,
                edit_value=edit_role,
            )

        return current_at, current_dt
