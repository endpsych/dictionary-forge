"""
Description: Sidebar component for tracking variable definition progress.
"""

import streamlit as st


def render_variable_tracker():
    """
    Renders the progress tracker and quality shield in the sidebar.
    """
    st.sidebar.header("🛡️ Quality & Progress")

    defined_list = st.session_state.get("variables", [])
    pending_list = st.session_state.get("pending_variables", [])

    total = len(defined_list) + len(pending_list)

    if total == 0:
        st.sidebar.info("No variables in scope. Start by adding one or ingesting a file.")
        return

    # 1. Progress Metrics
    completion_rate = len(defined_list) / total
    st.sidebar.metric(
        label="Dictionary Status",
        value=f"{len(defined_list)} / {total}",
        delta=f"{len(pending_list)} Pending",
        delta_color="inverse",
    )
    st.sidebar.progress(completion_rate)

    # 2. Data Quality Shield Analysis
    if defined_list:
        st.sidebar.divider()
        st.sidebar.subheader("📈 Definition Quality")

        quality_counts = {"Gold": 0, "Silver": 0, "Bronze": 0}
        graded_vars = []

        for var in defined_list:
            grade, score = _calculate_definition_grade(var)
            quality_counts[grade] += 1
            graded_vars.append((var["name"], grade, score))

        # Show Quality Distribution
        c1, c2, c3 = st.sidebar.columns(3)
        c1.metric("🥇", quality_counts["Gold"])
        c2.metric("🥈", quality_counts["Silver"])
        c3.metric("🥉", quality_counts["Bronze"])

        with st.sidebar.expander("📝 Defined Variables"):
            for name, grade, score in graded_vars:
                icon = "🟢" if grade == "Gold" else "🟡" if grade == "Silver" else "🟠"
                st.write(f"{icon} **{name}** ({score}%)")

    # 3. Pending Queue
    if pending_list:
        st.sidebar.divider()
        with st.sidebar.expander(f"📥 Pending Queue ({len(pending_list)})", expanded=True):
            for var_name in pending_list:
                if st.button(f"📌 {var_name}", key=f"track_{var_name}", use_container_width=True):
                    _load_variable_from_tracker(var_name)


def _calculate_definition_grade(var):
    """
    Evaluates a variable across multiple dimensions.
    Returns: (Grade String, Score Integer)
    """
    score = 0
    # Technical (40 pts)
    if var.get("name"):
        score += 10
    if var.get("analytical_type"):
        score += 10
    if var.get("data_type"):
        score += 10
    if var.get("role"):
        score += 10

    # Semantic (30 pts)
    if var.get("alias") and var.get("alias") != var.get("name"):
        score += 10
    desc = var.get("description", "")
    if len(desc) > 20:
        score += 20
    elif len(desc) > 0:
        score += 10

    # Governance (30 pts)
    gov = var.get("governance", {})
    if gov.get("data_steward"):
        score += 10
    if gov.get("pii_flag") is not None:
        score += 10
    if gov.get("sensitivity"):
        score += 10

    if score >= 90:
        return "Gold", score
    if score >= 60:
        return "Silver", score
    return "Bronze", score


def _load_variable_from_tracker(var_name):
    """Jump-starts the form for a specific variable."""
    from logic import guess_metadata_from_name

    st.session_state["form_id"] += 1
    fid = st.session_state["form_id"]
    guesses = guess_metadata_from_name(var_name)
    st.session_state[f"f{fid}__name"] = var_name
    st.session_state[f"v_at_{fid}"] = guesses["analytical_type"]
    st.session_state[f"f{fid}__data_type"] = guesses["data_type"]
    st.session_state[f"f{fid}__role"] = guesses["role"]
    st.session_state["cat_rows"] = [{"label": "", "rank": i + 1} for i in range(2)]
    st.session_state["last_form_id"] = fid
    st.session_state["editing_index"] = None
    st.session_state["cat_rows_hydrated"] = False
    st.rerun()
