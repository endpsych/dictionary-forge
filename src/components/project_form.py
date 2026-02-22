"""
Description: UI component for Project Metadata and Stakeholder Registry.
"""

import streamlit as st


def render_project_form():
    """
    Renders the 'Project & Stakeholders' expander and manages
    the list of stakeholders in st.session_state['project_info'].
    """
    with st.expander("📂 Project Metadata & Stakeholder Registry", expanded=True):
        col1, col2 = st.columns(2)

        # Core Project Info
        st.session_state["project_info"]["project_name"] = col1.text_input(
            "Project Name", value=st.session_state["project_info"]["project_name"]
        )
        st.session_state["project_info"]["version"] = col2.text_input(
            "Version", value=st.session_state["project_info"]["version"]
        )
        st.session_state["project_info"]["description"] = st.text_area(
            "Project Description", value=st.session_state["project_info"]["description"]
        )

        st.divider()
        st.markdown("##### 👥 Stakeholder Registry")

        # Dynamic Stakeholder Rows
        # Use a copy of the list to iterate to prevent index errors during deletion
        for i, person in enumerate(st.session_state["project_info"]["stakeholders"]):
            sc1, sc2, sc3, sc4 = st.columns([2, 2, 3, 0.5])

            person["name"] = sc1.text_input(f"Name #{i + 1}", value=person.get("name", ""), key=f"sh_n_{i}")
            person["role"] = sc2.text_input(f"Role #{i + 1}", value=person.get("role", ""), key=f"sh_r_{i}")
            person["email"] = sc3.text_input(f"Email #{i + 1}", value=person.get("email", ""), key=f"sh_e_{i}")

            # Delete Button
            if sc4.button("🗑️", key=f"sh_del_{i}"):
                st.session_state["project_info"]["stakeholders"].pop(i)
                st.rerun()

        # Add Stakeholder Button
        if st.button("➕ Add Stakeholder"):
            st.session_state["project_info"]["stakeholders"].append({"name": "", "role": "", "email": ""})
            st.rerun()
