"""
Description: Professional Master-Detail Regulatory Compliance Manager.
"""

import streamlit as st

from logic import load_regulations, save_regulations


@st.dialog("⚖️ Regulatory Compliance Manager", width="large")
def render_governance_manager():
    """
    Split-pane browser for regulations with a searchable index
    and professional fact-sheet reader.
    """
    # 1. State Initialization
    if "reg_manager_view" not in st.session_state:
        st.session_state["reg_manager_view"] = "LIST"

    if "selected_reg_abbr" not in st.session_state:
        st.session_state["selected_reg_abbr"] = None

    if "reg_edit_mode" not in st.session_state:
        st.session_state["reg_edit_mode"] = False

    regs = load_regulations()

    # 2. Layout Columns
    col_index, col_detail = st.columns([1, 2.2], gap="large")

    # --- LEFT COLUMN: SEARCHABLE NAVIGATION INDEX ---
    with col_index:
        st.markdown("### 📋 Index")

        # Space-optimized Search Bar
        search_query = st.text_input(
            "Search Index",
            placeholder="Search name or jurisdiction...",
            label_visibility="collapsed",
            key="reg_search_input",
        ).lower()

        with st.container(height=500, border=True):
            if not regs:
                st.info("No regulations defined.")
            else:
                # Filter Logic for Abbreviation and Jurisdiction
                filtered_abbrs = []
                for abbr, details in regs.items():
                    jur = details.get("jurisdiction", "").lower()
                    if search_query in abbr.lower() or search_query in jur:
                        filtered_abbrs.append(abbr)

                if not filtered_abbrs:
                    st.caption("No matches found.")

                for abbr in sorted(filtered_abbrs):
                    details = regs.get(abbr, {})
                    jur = details.get("jurisdiction", "Global")

                    is_selected = st.session_state["selected_reg_abbr"] == abbr
                    btn_type = "primary" if is_selected else "secondary"

                    # Label format: Abbreviation (Jurisdiction)
                    if st.button(
                        f"**{abbr}** ({jur})",
                        key=f"nav_{abbr}",
                        use_container_width=True,
                        type=btn_type,
                    ):
                        st.session_state["selected_reg_abbr"] = abbr
                        st.session_state["reg_manager_view"] = "DETAILS"
                        st.session_state["reg_edit_mode"] = False
                        st.rerun()

        st.write("")
        if st.button("➕ Create New Framework", type="primary", use_container_width=True):
            st.session_state["reg_manager_view"] = "ADD"
            st.session_state["selected_reg_abbr"] = None
            st.rerun()

    # --- RIGHT COLUMN: READER / EDITOR ---
    with col_detail:
        # A. DEFAULT STATE
        if st.session_state["reg_manager_view"] == "LIST" and not st.session_state["selected_reg_abbr"]:
            st.markdown("### 🔍 Detail View")
            st.info("Select a regulation from the index to view its full documentation.")

        # B. SOLIDIFIED READER MODE
        elif st.session_state["reg_manager_view"] == "DETAILS" and not st.session_state["reg_edit_mode"]:
            abbr = st.session_state["selected_reg_abbr"]
            details = regs.get(abbr, {})

            h1, h2 = st.columns([3, 1])
            h1.markdown("### 📄 Regulation Overview")
            if h2.button("✏️ Edit", use_container_width=True):
                st.session_state["reg_edit_mode"] = True
                st.rerun()

            with st.container(height=500, border=True):
                st.markdown(f"## {details.get('full_name', 'Unnamed Framework')}")
                st.markdown(f"#### {abbr}")
                st.caption(f"📍 Jurisdiction: **{details.get('jurisdiction', 'Global')}**")

                st.divider()
                st.markdown("**🔗 Documentation Link**")
                url = details.get("url", "#")
                st.markdown(f"[{url}]({url})")

                st.write("")
                st.markdown("**📝 Full Description**")
                st.markdown(details.get("description", "*No description provided.*"))

        # C. EDITION MODE
        elif st.session_state["reg_edit_mode"] and st.session_state["selected_reg_abbr"]:
            old_abbr = st.session_state["selected_reg_abbr"]
            details = regs.get(old_abbr, {})

            st.markdown("### 📝 Editing Framework")

            with st.container(height=500, border=True):
                with st.form(f"edit_form_{old_abbr}", border=False):
                    new_full = st.text_input("Full Name", value=details.get("full_name", ""))

                    c1, c2 = st.columns(2)
                    new_abbr = c1.text_input("Abbreviated Name", value=old_abbr)
                    new_jur = c2.text_input("Jurisdiction", value=details.get("jurisdiction", "Global"))

                    new_url = st.text_input("Official URL", value=details.get("url", ""))
                    new_desc = st.text_area("Description", value=details.get("description", ""), height=180)

                    st.divider()
                    btn_save, btn_del, btn_cancel = st.columns(3)

                    if btn_save.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                        # Key Migration logic for safe renaming
                        if new_abbr != old_abbr:
                            del regs[old_abbr]

                        regs[new_abbr.strip()] = {
                            "full_name": new_full.strip(),
                            "jurisdiction": new_jur.strip(),
                            "description": new_desc.strip(),
                            "url": new_url.strip(),
                        }
                        save_regulations(regs)
                        st.session_state["selected_reg_abbr"] = new_abbr.strip()
                        st.session_state["reg_edit_mode"] = False
                        st.rerun()

                    if btn_cancel.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state["reg_edit_mode"] = False
                        st.rerun()

                    if btn_del.form_submit_button("🗑️ Delete", use_container_width=True):
                        del regs[old_abbr]
                        save_regulations(regs)
                        st.session_state["selected_reg_abbr"] = None
                        st.session_state["reg_manager_view"] = "LIST"
                        st.rerun()

        # D. ADD NEW MODE
        elif st.session_state["reg_manager_view"] == "ADD":
            st.markdown("### ➕ Add New Framework")
            with st.container(height=500, border=True):
                with st.form("add_reg_form", clear_on_submit=True, border=False):
                    new_full = st.text_input("Full Name *")
                    a1, a2 = st.columns(2)
                    new_abbr = a1.text_input("Abbreviation *")
                    new_jur = a2.text_input("Jurisdiction *")
                    new_url = st.text_input("Official URL *")
                    new_desc = st.text_area("Description", height=150)

                    st.divider()
                    sub_save, sub_cancel = st.columns(2)
                    if sub_save.form_submit_button("💾 Save Regulation", type="primary", use_container_width=True):
                        if new_abbr and new_jur and new_full and new_url:
                            abbr_clean = new_abbr.strip()
                            regs[abbr_clean] = {
                                "full_name": new_full.strip(),
                                "jurisdiction": new_jur.strip(),
                                "description": new_desc.strip(),
                                "url": new_url.strip(),
                            }
                            save_regulations(regs)
                            st.session_state["selected_reg_abbr"] = abbr_clean
                            st.session_state["reg_manager_view"] = "DETAILS"
                            st.rerun()
                        else:
                            st.error("Missing required fields (*)")

                    if sub_cancel.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state["reg_manager_view"] = "LIST"
                        st.rerun()

    # --- FOOTER ---
    st.divider()
    if st.button("✖️ Close Compliance Manager", use_container_width=True):
        st.session_state["show_gov_manager"] = False
        st.rerun()
