"""
Description: Logic handler for Variable Form submissions and categorical hydration.
"""

import ast

import streamlit as st


def process_form_submission(v_inputs, current_at, current_dt):
    """
    Validates form inputs and commits the variable to session state.
    Handles both new additions and in-place updates for Edit Mode.
    """
    # 1. Basic Validation
    if not v_inputs.get("name"):
        st.error("Variable Name is required.")
        return False

    # 2. Categorical & Binary Logic Validation
    is_locked_binary = current_at == "binary" or current_dt == "bool"
    constraints = v_inputs.get("constraints", {})
    allowed_labels = constraints.get("allowed_values", [])

    if is_locked_binary and len(allowed_labels) != 2:
        st.error("❌ Boolean/Binary variables must have exactly 2 defined labels.")
        return False

    if current_dt == "category":
        # Check for Ordinal Rank Uniqueness
        mapping = constraints.get("ordinal_mapping", {})

        # Defensive check in case it's a string from UI state
        if isinstance(mapping, str):
            try:
                mapping = ast.literal_eval(mapping)
            except Exception:
                mapping = {}

        if isinstance(mapping, dict):
            ranks = list(mapping.values())
            if current_at == "ordinal" and len(ranks) != len(set(ranks)):
                st.error("❌ Ordinal variables must have unique ranks for each label.")
                return False

    # 3. Commit to Session State
    editing_idx = st.session_state.get("editing_index")

    if editing_idx is not None:
        # Update existing variable
        st.session_state["variables"][editing_idx] = v_inputs
        st.session_state["editing_index"] = None
        st.success(f"Variable '{v_inputs['name']}' updated.")
    else:
        # Append new variable
        st.session_state["variables"].append(v_inputs)
        st.success(f"Variable '{v_inputs['name']}' added to dictionary.")

    # 4. State Cleanup
    st.session_state["cat_rows_hydrated"] = False
    return True


def delete_variable(index):
    """
    Removes a variable from the dictionary and manages edit mode state safety.
    """
    if 0 <= index < len(st.session_state["variables"]):
        variable_name = st.session_state["variables"][index].get("name", "Unknown")

        # Remove from list
        st.session_state["variables"].pop(index)

        # Handle index synchronization for Edit Mode
        if st.session_state.get("editing_index") == index:
            st.session_state["editing_index"] = None
            st.session_state["cat_rows_hydrated"] = False
        elif st.session_state.get("editing_index") is not None and st.session_state["editing_index"] > index:
            st.session_state["editing_index"] -= 1

        st.success(f"Variable '{variable_name}' deleted.")
        st.rerun()


def initialize_categorical_rows(edit_data=None):
    """
    Synchronizes categorical row state with the Ground Truth (Template/Ledger).
    """
    fid = st.session_state.get("form_id", 0)

    # 1. Template/Edit Hydration (Higher Priority)
    if edit_data and edit_data.get("data_type") == "category":
        # Only hydrate if the form version has changed or hydration flag is False
        if st.session_state.get("last_form_id") != fid or not st.session_state.get("cat_rows_hydrated"):
            constraints = edit_data.get("constraints", {})
            allowed = constraints.get("allowed_values", [])
            mapping = constraints.get("ordinal_mapping", {})

            # --- DEFENSIVE PARSING FOR DATAFRAME ROUND-TRIPS ---
            if isinstance(allowed, str):
                try:
                    allowed = ast.literal_eval(allowed)
                except Exception:
                    allowed = []

            if isinstance(mapping, str):
                try:
                    mapping = ast.literal_eval(mapping)
                except Exception:
                    mapping = {}
            # ---------------------------------------------------

            if not isinstance(mapping, dict):
                mapping = {}

            # Map JSON structure to UI row structure
            hydrated_rows = []
            if isinstance(allowed, list):
                for val in allowed:
                    hydrated_rows.append({"label": val, "rank": mapping.get(val, 0)})

            # If no allowed values in template, default to one empty row
            if not hydrated_rows:
                hydrated_rows = [{"label": "", "rank": 0}]

            st.session_state["cat_rows"] = hydrated_rows
            st.session_state["cat_rows_hydrated"] = True
            st.session_state["last_form_id"] = fid
            return

    # 2. Standard Session Reset
    if "cat_rows" not in st.session_state or st.session_state.get("last_form_id") != fid:
        # Only reset if we are NOT in the middle of a hydration process
        if not st.session_state.get("cat_rows_hydrated", False):
            st.session_state["cat_rows"] = [{"label": "", "rank": 0}]
            st.session_state["last_form_id"] = fid
