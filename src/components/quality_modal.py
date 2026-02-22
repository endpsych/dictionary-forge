"""
Description: Diagnostic modal for data dictionary health and progress.
"""

import pandas as pd
import streamlit as st


@st.dialog("🛡️ Data Quality & Progress Audit", width="large")
def render_quality_modal():
    """
    Renders the centralized quality audit suite.
    Evaluates metadata richness and provides a roadmap to 100% completion.
    """
    defined_list = st.session_state.get("variables", [])
    pending_list = st.session_state.get("pending_variables", [])
    total = len(defined_list) + len(pending_list)

    if total == 0:
        st.info("The dictionary is currently empty. Add variables to begin the audit.")
        return

    # --- Section 1: Completion Metrics ---
    completion_rate = len(defined_list) / total
    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        st.markdown(f"**Overall Dictionary Completion: {completion_rate:.0%}**")
        st.progress(completion_rate)

    c2.metric("Defined", len(defined_list))
    c3.metric(
        "Pending",
        len(pending_list),
        delta=f"-{len(pending_list)}",
        delta_color="inverse",
    )

    if not defined_list:
        st.divider()
        st.warning("No variables have been defined yet. Quality analysis is unavailable.")
        return

    # --- Section 2: Quality Shield Analysis ---
    st.divider()
    st.subheader("📈 Definition Quality Audit")

    audit_data = []
    quality_counts = {"Gold": 0, "Silver": 0, "Bronze": 0}

    for var in defined_list:
        grade, score, missing = _calculate_audit_details(var)
        quality_counts[grade] += 1
        audit_data.append(
            {
                "Variable": var["name"],
                "Grade": grade,
                "Score": f"{score}%",
                "Missing for Gold": ", ".join(missing) if missing else "✅ Perfect",
            }
        )

    # High-level Quality Summary
    q1, q2, q3 = st.columns(3)
    q1.metric("🥇 Gold Standards", quality_counts["Gold"])
    q2.metric("🥈 Silver Tier", quality_counts["Silver"])
    q3.metric("🥉 Bronze / Draft", quality_counts["Bronze"])

    # Detailed Audit Table
    st.write("")
    st.markdown("##### 📝 Detailed Deficiency Report")
    df_audit = pd.DataFrame(audit_data)

    # Apply color highlighting to the Grade column
    def color_grade(val):
        color = "#d4af37" if val == "Gold" else "#c0c0c0" if val == "Silver" else "#cd7f32"
        return f"color: {color}; font-weight: bold"

    st.table(df_audit.style.applymap(color_grade, subset=["Grade"]))

    # --- Section 3: Actionable Jump-Links ---
    st.divider()
    col_edit, col_pending = st.columns(2)

    with col_edit:
        st.markdown("##### 📝 Quick Edit")
        var_to_edit = st.selectbox(
            "Jump to edit a variable:",
            options=[v["name"] for v in defined_list],
            key="quality_edit_select",
        )
        if st.button("Open in Form", use_container_width=True):
            idx = next(i for i, v in enumerate(defined_list) if v["name"] == var_to_edit)
            st.session_state["editing_index"] = idx
            st.session_state["form_id"] += 1
            st.session_state["cat_rows_hydrated"] = False
            st.rerun()

    with col_pending:
        if pending_list:
            st.markdown(f"##### 📥 Next in Queue ({len(pending_list)})")
            next_var = pending_list[0]
            if st.button(f"Define: {next_var}", type="primary", use_container_width=True):
                _load_variable_from_quality_modal(next_var)
        else:
            st.success("All pending variables have been defined!")


def _calculate_audit_details(var):
    """
    Enhanced grader that identifies specific missing metadata.
    """
    score = 0
    missing = []

    # Technical (40 pts)
    if var.get("name"):
        score += 10
    else:
        missing.append("Name")

    if var.get("analytical_type"):
        score += 10
    else:
        missing.append("Analytical Type")

    if var.get("data_type"):
        score += 10
    else:
        missing.append("Data Type")

    if var.get("role"):
        score += 10
    else:
        missing.append("Role")

    # Semantic (30 pts)
    if var.get("alias") and var.get("alias") != var.get("name"):
        score += 10
    else:
        missing.append("Unique Alias")

    desc = var.get("description", "")
    if len(desc) > 20:
        score += 20
    elif len(desc) > 0:
        score += 10
        missing.append("Detailed Description (>20 chars)")
    else:
        missing.append("Description")

    # Governance (30 pts)
    gov = var.get("governance", {})
    if gov.get("data_steward"):
        score += 10
    else:
        missing.append("Data Steward")

    if gov.get("pii_flag") is not None:
        score += 10
    else:
        missing.append("PII Flag")

    if gov.get("sensitivity"):
        score += 10
    else:
        missing.append("Sensitivity Level")

    if score >= 90:
        return "Gold", score, []
    if score >= 60:
        return "Silver", score, missing
    return "Bronze", score, missing


def _load_variable_from_quality_modal(var_name):
    """Transitions a variable from the pending queue to the active form."""
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
