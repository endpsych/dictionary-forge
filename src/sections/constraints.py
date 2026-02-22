"""
Description: Constraint logic including context-aware mapping, row truncation, and optional bounds.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field
from constants import TOOLTIP_DEFINITIONS
from logic import is_field_visible


def render_constraints_section(nested_sections, current_at, current_dt, v_inputs, edit_data=None):
    """Renders constraints with strict vertical flow, hydrated categorical rows, and toggleable bounds."""
    if "constraints" not in nested_sections:
        return
    edit_constraints = edit_data.get("constraints", {}) if edit_data else {}
    fid = st.session_state.get("form_id", 0)

    with st.container(border=True):
        section_data = {}
        fields = nested_sections["constraints"].get("fields", [])

        # 1. Bounds Section (Explicitly ordered with activation toggles)
        sub_cols = st.columns(3)
        bounds_fields = [f for f in fields if f["name"] in ["min_value", "max_value"]]
        other_non_bool = [
            f for f in fields if f["dtype"] not in ["boolean", "list"] and f["name"] not in ["min_value", "max_value"]
        ]

        for i, f in enumerate(bounds_fields):
            with sub_cols[i % 3]:
                # Check if this bound has a pre-existing value in the template/edit data
                existing_val = edit_constraints.get(f["name"])
                is_active_default = existing_val is not None

                # Dynamic toggle label
                toggle_label = "Enforce Minimum" if f["name"] == "min_value" else "Enforce Maximum"

                # The toggle controls whether the field renders and saves
                is_active = st.toggle(toggle_label, value=is_active_default, key=f"tgl_{f['name']}_{fid}")

                if is_active:
                    res = render_input_field(
                        f,
                        prefix="constraints",
                        analytical_type=current_at,
                        data_type=current_dt,
                        edit_value=existing_val,
                    )
                    # Even if the user enters 0, it is a valid explicit constraint if activated.
                    if res is not None:
                        section_data[f["name"]] = res

        # 2. Time Series Configuration
        if current_at == "time_index":
            st.write("---")
            st.markdown("**Timeline Logic**")
            _render_time_series_logic(section_data, edit_constraints, fid)

        # 3. Integrity Flags Section
        st.write("---")
        st.markdown("**Integrity Flags**")

        if other_non_bool:
            o_cols = st.columns(3)
            for i, f in enumerate(other_non_bool):
                with o_cols[i % 3]:
                    res = render_input_field(
                        f,
                        prefix="constraints",
                        analytical_type=current_at,
                        data_type=current_dt,
                        edit_value=edit_constraints.get(f["name"]),
                    )
                    if res is not None:
                        section_data[f["name"]] = res

        bool_fields = [f for f in fields if f["dtype"] == "boolean"]
        flag_cols = st.columns(max(len(bool_fields), 1))
        for i, f in enumerate(bool_fields):
            with flag_cols[i]:
                res = render_input_field(
                    f,
                    prefix="constraints",
                    analytical_type=current_at,
                    data_type=current_dt,
                    edit_value=edit_constraints.get(f["name"]),
                )
                if res is not None:
                    section_data[f["name"]] = res

        # 4. Categorical Mapping or Allowed Values
        is_cat_logic = (
            current_dt == "category" or current_at == "binary" or (current_at == "nominal" and current_dt == "bool")
        )
        if is_cat_logic:
            mapping_header = "🏁 Value Mapping & Ranks" if current_at == "ordinal" else "🏁 Categorical Value Mapping"
            with st.expander(mapping_header, expanded=True):
                _render_categorical_mapping(current_at, current_dt, section_data, fid)
        elif is_field_visible("allowed_values", current_at, current_dt):
            res = render_input_field(
                {"name": "allowed_values", "dtype": "list"},
                prefix="constraints",
                analytical_type=current_at,
                data_type=current_dt,
                edit_value=edit_constraints.get("allowed_values"),
            )
            if res:
                section_data["allowed_values"] = res

        v_inputs["constraints"] = section_data


def _render_time_series_logic(section_data, edit_constraints, fid):
    """Handles frequency selection and reactive monotonicity using fid-versioned keys."""
    t1, t2, t3 = st.columns([2, 0.5, 2.5])

    with t1:
        freq_dict = TOOLTIP_DEFINITIONS.get("frequency", {})
        freq_opts = list(freq_dict.keys())
        default_freq = edit_constraints.get("frequency", "D")
        idx = freq_opts.index(default_freq) if default_freq in freq_opts else 0

        freq = st.selectbox(
            "Time Frequency",
            options=freq_opts,
            index=idx,
            key=f"ts_freq_{fid}",
            help="Select the expected interval between observations.",
        )
        section_data["frequency"] = freq
        if freq in freq_dict:
            st.info(freq_dict[freq])

    with t3:
        mono = st.checkbox(
            "Monotonic",
            value=edit_constraints.get("monotonicity") == "strictly_increasing",
            key=f"ts_mono_{fid}",
            help="Ensures chronological integrity.",
        )
        if mono:
            section_data["monotonicity"] = "strictly_increasing"
            st.success("✅ **Sequence must move forward.**")
        else:
            section_data["monotonicity"] = "none"
            st.warning("⚠️ **Unordered timestamps allowed.**")


def _render_categorical_mapping(current_at, current_dt, section_data, fid):
    """Renders categorical inputs driven by the pre-hydrated st.session_state['cat_rows']."""
    is_locked_binary = current_at == "binary" or current_dt == "bool"

    # Validation for binary/bool locks
    if is_locked_binary and len(st.session_state.get("cat_rows", [])) > 2:
        st.session_state["cat_rows"] = st.session_state["cat_rows"][:2]

    mapping_info = (
        TOOLTIP_DEFINITIONS.get("ordinal_mapping", {}).get("info", "Establishes mathematical order.")
        if current_at == "ordinal"
        else "Defines valid unique labels. No mathematical order implied."
    )
    st.markdown(f"💡 {mapping_info}")

    rows_to_delete = []
    # Iterate over session state rows (hydrated via handlers.py)
    for i, row in enumerate(st.session_state.get("cat_rows", [])):
        cols = st.columns([3, 2, 1]) if current_at == "ordinal" else st.columns([5, 1])

        with cols[0]:
            # key includes fid to ensure reset on template load
            row_label = st.text_input(
                f"V{i + 1}",
                value=row["label"],
                key=f"cat_label_{fid}_{i}",
                label_visibility="collapsed",
                placeholder="Label name...",
            )
            st.session_state["cat_rows"][i]["label"] = row_label

        if current_at == "ordinal":
            with cols[1]:
                row_rank = st.number_input(
                    f"R{i + 1}",
                    value=row["rank"],
                    key=f"cat_rank_{fid}_{i}",
                    label_visibility="collapsed",
                    step=1,
                )
                st.session_state["cat_rows"][i]["rank"] = row_rank

        if not is_locked_binary and len(st.session_state["cat_rows"]) > 1:
            with cols[-1]:
                if st.button("🗑️", key=f"del_{fid}_{i}"):
                    rows_to_delete.append(i)

    if rows_to_delete:
        for idx in reversed(rows_to_delete):
            st.session_state["cat_rows"].pop(idx)
        st.rerun()

    if not is_locked_binary:
        if st.button("➕ Add Row", key=f"add_row_{fid}", use_container_width=True):
            st.session_state["cat_rows"].append({"label": "", "rank": len(st.session_state["cat_rows"]) + 1})
            st.rerun()

    # Collect valid values for section_data
    valid_labels = [r["label"].strip() for r in st.session_state["cat_rows"] if r["label"].strip()]
    section_data["allowed_values"] = valid_labels
    if current_at == "ordinal" or is_locked_binary:
        section_data["ordinal_mapping"] = {
            r["label"].strip(): r["rank"] for r in st.session_state["cat_rows"] if r["label"].strip()
        }
