"""
Main entry point for the Variable Definition Form.
"""

import streamlit as st

import sections

from .handlers import initialize_categorical_rows, process_form_submission


def render_variable_form(variable_fields):
    """
    Renders the complete variable definition form.
    Handles hydration logic for Templates and Edit Mode.
    Captures full metadata payload and syncs with Sidebar Template Manager.
    """
    # 1. Check for Hydration Source (Template or Edit Mode)
    editing_idx = st.session_state.get("editing_index")
    edit_data = None

    # Check for loaded template first (Template Hub integration)
    if st.session_state.get("loaded_template"):
        # FORCE WIDGET REBIRTH: Increment form_id to rotate all widget keys
        st.session_state["form_id"] += 1
        curr_fid = st.session_state["form_id"]
        prev_fid = curr_fid - 1

        edit_data = st.session_state["loaded_template"]

        # IDENTITY PRESERVATION BRIDGE:
        # Preserve identity fields if they were excluded from the template payload
        for field in ["name", "alias", "description"]:
            if field not in edit_data:
                existing_val = st.session_state.get(f"f{prev_fid}__{field}")
                if existing_val:
                    st.session_state[f"f{curr_fid}__{field}"] = existing_val

        # Display Dynamic Hydration Report
        report = st.session_state.get("hydration_report", "Hydrating form from blueprint metadata.")
        st.info(f"✨ {report}")

        # Cleanup Template Flags
        st.session_state["loaded_template"] = None
        st.session_state.pop("hydration_report", None)

    elif editing_idx is not None:
        st.subheader(f"📝 Editing Variable: {st.session_state['variables'][editing_idx]['name']}")
        edit_data = st.session_state["variables"][editing_idx]
        if st.button("❌ Cancel Edit", use_container_width=True):
            st.session_state["editing_index"] = None
            st.session_state["cat_rows_hydrated"] = False
            st.rerun()
    else:
        sections.render_queue_integration_section()

    # 2. Setup State (Hydrate categorical rows from edit_data ground truth)
    initialize_categorical_rows(edit_data=edit_data)

    # 3. Initialize data collection objects
    v_inputs = {}
    field_defs = {f["name"]: f for f in variable_fields if f["dtype"] != "dict"}
    nested_sections = {f["name"]: f for f in variable_fields if f["dtype"] == "dict"}

    # 4. Sequential Section Rendering
    with st.expander("🆔 Identification", expanded=True):
        sections.render_identification_section(field_defs, v_inputs, edit_data=edit_data)

    with st.expander("⚙️ Technical Configuration", expanded=False):
        current_at, current_dt = sections.render_technical_config_section(field_defs, v_inputs, edit_data=edit_data)

    with st.expander("📏 Constraints", expanded=False):
        sections.render_constraints_section(nested_sections, current_at, current_dt, v_inputs, edit_data=edit_data)

    with st.expander("🧼 Cleaning", expanded=False):
        sections.render_cleaning_section(nested_sections, current_at, current_dt, v_inputs, edit_data=edit_data)

    with st.expander("📊 Visualization", expanded=False):
        sections.render_visualization_section(nested_sections, current_at, current_dt, v_inputs, edit_data=edit_data)

    with st.expander("⚖️ Governance", expanded=False):
        sections.render_governance_section(nested_sections, current_at, current_dt, v_inputs, edit_data=edit_data)

    with st.expander("🗄️ Database Mapping", expanded=False):
        sections.render_database_mapping_section(current_at, current_dt, v_inputs, edit_data=edit_data)

    # 5. Global Action Bar Sync
    # Sync current inputs to session state for the global action bar to access during save.
    st.session_state["active_v_inputs"] = v_inputs
    st.session_state["current_at"] = current_at
    st.session_state["current_dt"] = current_dt


__all__ = [
    "process_form_submission",
    "initialize_categorical_rows",
    "render_variable_form",
]
