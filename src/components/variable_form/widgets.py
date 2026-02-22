"""
Description: Low-level widget renderers for the Variable Definition Form.
"""

import datetime

import streamlit as st

from constants import REGEX_LIBRARY, TOOLTIP_DEFINITIONS
from logic import (
    get_dynamic_label,
    get_filtered_data_types,
    is_field_visible,
    load_regulations,
)


def render_input_field(field_def, prefix="", analytical_type="continuous", data_type=None, edit_value=None):
    """
    Dispatcher for individual widgets.
    Prioritizes Ground Truth (edit_value) to ensure coherence with Templates/Ledger.
    """
    if field_def is None or not is_field_visible(field_def["name"], analytical_type, data_type):
        return None

    name = field_def["name"]
    label = get_dynamic_label(name, analytical_type) + (" *" if field_def.get("required", False) else "")

    # Form versioning is baked into the key to force refresh on template load
    base_key = f"f{st.session_state.get('form_id', 0)}_{prefix}_{name}"
    dtype = field_def.get("dtype", "string")

    if name == "data_type":
        return _handle_technical_selector(label, base_key, analytical_type, edit_value)
    elif dtype in ["enum", "multiselect"]:
        return _handle_enum_multiselect(name, label, base_key, dtype, field_def, edit_value)
    elif dtype == "boolean":
        return _handle_boolean(name, label, base_key, field_def, edit_value)
    elif dtype == "number":
        return _handle_numeric(name, label, base_key, prefix, analytical_type, data_type, edit_value)
    elif dtype == "string":
        return _handle_string(name, label, base_key, data_type, edit_value)
    return None


def _handle_technical_selector(label, base_key, analytical_type, edit_value):
    """Handles Data Type selection with ground-truth index resolution."""
    opts = get_filtered_data_types(analytical_type)

    # Force alignment with Ground Truth
    try:
        index = opts.index(edit_value) if edit_value in opts else 0
    except (ValueError, AttributeError):
        index = 0

    help_text = TOOLTIP_DEFINITIONS.get("data_type", {}).get("help", "Technical storage format.")
    val = st.selectbox(label, options=opts, index=index, key=base_key, help=help_text)

    if val in TOOLTIP_DEFINITIONS.get("data_type", {}):
        st.info(TOOLTIP_DEFINITIONS["data_type"][val])

    return val


def _handle_enum_multiselect(name, label, base_key, dtype, field_def, edit_value):
    """Handles single/multi choice fields with state-first default logic."""
    if name == "compliance_scope":
        active_regulations = load_regulations()
        opts = list(active_regulations.keys())
    else:
        opts = list(field_def.get("options", []))

    # Domain-specific fallback logic
    if name == "missing_strategy":
        for opt in ["keep", "maximum_likelihood"]:
            if opt not in opts:
                opts.append(opt)
        default_val = edit_value if edit_value else "keep"
    elif name == "preferred_plot":
        if "not_needed" not in opts:
            opts.append("not_needed")
        default_val = edit_value if edit_value else "not_needed"
    else:
        default_val = edit_value

    general_help = TOOLTIP_DEFINITIONS.get(name, {}).get("help", f"Configure {label} settings.")

    if dtype == "multiselect":
        safe_default = [v for v in edit_value if v in opts] if isinstance(edit_value, list) else []
        val = st.multiselect(label, options=opts, default=safe_default, key=base_key, help=general_help)
        return val

    # Resolve index for single select
    try:
        index = opts.index(default_val) if default_val in opts else 0
    except (ValueError, AttributeError):
        index = 0

    val = st.selectbox(label, options=opts, index=index, key=base_key, help=general_help)

    if name in TOOLTIP_DEFINITIONS and val in TOOLTIP_DEFINITIONS[name]:
        st.info(TOOLTIP_DEFINITIONS[name][val])

    return val


def _handle_boolean(name, label, base_key, field_def, edit_value):
    """Handles toggles with explicit state context."""
    default = edit_value if edit_value is not None else field_def.get("default", False)
    help_text = TOOLTIP_DEFINITIONS.get(name, {}).get("help", f"Toggle {label} state.")
    val = st.toggle(label, value=bool(default), key=base_key, help=help_text)

    state_key = "true" if val else "false"
    if name in TOOLTIP_DEFINITIONS and state_key in TOOLTIP_DEFINITIONS[name]:
        st.caption(f"💡 {TOOLTIP_DEFINITIONS[name][state_key]}")

    return val


def _handle_numeric(name, label, base_key, prefix, analytical_type, data_type, edit_value):
    """Handles numeric and date inputs with bound synchronization."""
    general_help = "Numerical or chronological boundaries for data validation."
    fid = st.session_state.get("form_id", 0)

    # 1. Chronological Hydration
    if analytical_type == "time_index" and name in ["min_value", "max_value"]:
        default_date = datetime.date.today()
        if edit_value:
            try:
                default_date = datetime.date.fromisoformat(edit_value)
            except Exception:
                pass

        min_date, max_date = None, None
        if name == "max_value":
            lower_key = f"f{fid}_{prefix}_min_value"
            if lower_key in st.session_state:
                min_date = st.session_state[lower_key]

        val = st.date_input(
            label,
            value=default_date,
            min_value=min_date,
            max_value=max_date,
            key=base_key,
            help=general_help,
        )
        return val.isoformat()

    # 2. Numeric Bounds Hydration
    min_limit = 0.0
    if name == "max_value":
        lower_key = f"f{fid}_{prefix}_min_value"
        if lower_key in st.session_state:
            min_limit = st.session_state[lower_key]

    is_int = (
        analytical_type in ["text", "nominal", "ordinal"] and name in ["min_value", "max_value"]
    ) or analytical_type == "discrete"

    try:
        if is_int:
            default_val = int(edit_value) if edit_value is not None else int(min_limit)
            val = st.number_input(
                label,
                min_value=int(min_limit),
                value=int(default_val),
                step=1,
                format="%d",
                key=base_key,
                help=general_help,
            )
        else:
            default_val = float(edit_value) if edit_value is not None else float(min_limit)
            val = st.number_input(
                label,
                min_value=float(min_limit),
                value=float(default_val),
                step=0.1,
                key=base_key,
                help=general_help,
            )
    except (ValueError, TypeError):
        # Fallback to neutral default if Ground Truth is corrupted
        val = st.number_input(label, value=0.0, key=base_key)

    return val


def _handle_string(name, label, base_key, data_type, edit_value):
    """
    Handles strings with advanced Regex Library cross-referencing.
    Supports Ground Truth resolution for both Pattern Names (keys) and Regex Strings (values).
    """
    if name == "regex_pattern" and data_type == "string":
        lib_key = f"{base_key}_lib_selector"
        col_lib, col_in = st.columns([1, 1])

        # Ground Truth Mapping: Does the edit_value refer to a pattern name or the regex itself?
        lib_keys = list(REGEX_LIBRARY.keys())
        lib_values = list(REGEX_LIBRARY.values())

        default_lib_idx = 0
        if edit_value in lib_keys:
            default_lib_idx = lib_keys.index(edit_value)
        elif edit_value in lib_values:
            default_lib_idx = lib_values.index(edit_value)

        with col_lib:
            pattern_choice = st.selectbox("Pattern Library", options=lib_keys, index=default_lib_idx, key=lib_key)

        with col_in:
            # If edit_value matches a key, we display the corresponding regex string value
            display_value = edit_value if edit_value not in REGEX_LIBRARY else REGEX_LIBRARY[edit_value]

            # The input key is tied to the choice to facilitate library-driven resets
            swap_key = f"{base_key}_swap_{pattern_choice.replace(' ', '_')}"
            val = st.text_input(
                label,
                value=display_value if display_value else REGEX_LIBRARY[pattern_choice],
                key=swap_key,
            )

        st.info(f"Must match the `{pattern_choice}` pattern.")
        return val

    help_text = TOOLTIP_DEFINITIONS.get(name, {}).get("help", f"Enter {label}.")
    val = st.text_input(label, value=edit_value if edit_value else "", key=base_key, help=help_text)

    return val
