"""
Description: Technical Configuration UI section for analytical types, data types, and roles.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field
from constants import TOOLTIP_DEFINITIONS
from logic import get_filtered_roles


def render_technical_config_section(field_defs, v_inputs, edit_data=None):
    """
    Renders core technical settings.
    Functional role restriction is enforced here via logic.py.
    """
    fid = st.session_state.get("form_id", 0)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)

        # 1. Analytical Type Selection
        at_def = field_defs.get("analytical_type", {"options": []})
        # Ensure time_index is available for temporal variables
        if "time_index" not in at_def["options"]:
            at_def["options"].append("time_index")

        # GROUND TRUTH RESOLUTION:
        # Prioritize edit_data (from template/ledger) to drive dependent widgets.
        default_at = edit_data.get("analytical_type", "continuous") if edit_data else "continuous"

        try:
            at_index = at_def["options"].index(default_at)
        except (ValueError, AttributeError):
            at_index = 0

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
        # The DT widget is filtered based on the current_at resolved above.
        with c2:
            current_dt = render_input_field(
                {"name": "data_type", "dtype": "enum"},
                analytical_type=current_at,
                edit_value=edit_data.get("data_type") if edit_data else None,
            )
            v_inputs["data_type"] = current_dt

        # 3. Functional Role Selection (Reactive Filter)
        with c3:
            # Filter valid roles based on the current AT and DT selection
            valid_roles = get_filtered_roles(current_at, current_dt)
            edit_role = edit_data.get("role") if edit_data else None

            # Fallback if previous role is no longer valid under new constraints
            if edit_role not in valid_roles:
                edit_role = "feature"

            v_inputs["role"] = render_input_field(
                {"name": "role", "dtype": "enum", "options": valid_roles},
                edit_value=edit_role,
            )

    return current_at, current_dt
