"""
Description: Template & Blueprint Lifecycle Manager for Dictionary Forge
Handles storage, retrieval, and destructive state injection for metadata standards.
Part of the 'logic' module refactor.
"""

import json
import os

import streamlit as st
import yaml


def load_master_schema(config_path):
    """
    Loads the master YAML blueprint defining the schema structure.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


def load_all_templates(
    standard_path="config/templates_standard.yaml",
    user_path="config/templates_user.json",
):
    """
    Merges project-standard templates with custom user blueprints.
    """
    all_templates = {}

    # 1. Load Standard Blueprints (Immutable YAML)
    if os.path.exists(standard_path):
        with open(standard_path) as f:
            std_data = yaml.safe_load(f)
            if std_data and "templates" in std_data:
                all_templates.update(std_data["templates"])

    # 2. Load User-Defined Blueprints (Mutable JSON)
    if os.path.exists(user_path):
        os.makedirs(os.path.dirname(user_path), exist_ok=True)

        with open(user_path) as f:
            try:
                user_data = json.load(f)
                if user_data and "user_templates" in user_data:
                    all_templates.update(user_data["user_templates"])
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    return all_templates


def apply_template_to_state(template_data, fid):
    """
    Injects a blueprint's metadata into the active form state.
    Performs a targeted purge of technical fields while preserving identification.
    """
    # Keys to protect (Variable Name, Alias, etc. should not be overwritten by a template)
    preserve_keys = [f"f{fid}__name", f"f{fid}__alias", f"f{fid}__description"]
    form_prefix = f"f{fid}__"
    v_at_key = f"v_at_{fid}"

    # 1. Purge existing technical state for the specific form ID
    for key in list(st.session_state.keys()):
        if (key.startswith(form_prefix) or key == v_at_key) and key not in preserve_keys:
            del st.session_state[key]

    # 2. Inject Technical Core
    st.session_state[v_at_key] = template_data.get("analytical_type", "continuous")
    st.session_state[f"{form_prefix}data_type"] = template_data.get("data_type", "float64")
    st.session_state[f"{form_prefix}role"] = template_data.get("role", "feature")

    # 3. Inject Nested Metadata (Constraints, Cleaning, Governance, Database)
    for section in ["constraints", "cleaning", "governance", "database_mapping"]:
        if section in template_data:
            section_vals = template_data[section]
            for field, val in section_vals.items():
                # Specialized hydration for categorical lists
                if field == "allowed_values" and section == "constraints":
                    st.session_state["cat_rows"] = [{"label": v, "rank": i + 1} for i, v in enumerate(val)]
                    st.session_state["cat_rows_hydrated"] = True
                else:
                    # Flattened widget-key mapping
                    st.session_state[f"{form_prefix}{section}_{field}"] = val


def save_user_template(template_name, v_inputs, user_path="config/templates_user.json"):
    """
    Persists a generic version of the current form as a reusable blueprint.
    """
    import copy

    new_template = copy.deepcopy(v_inputs)

    # Scrub unique identification to keep the template generic
    for key in ["name", "alias", "description"]:
        new_template.pop(key, None)

    new_template["label"] = template_name

    # Load existing user data or initialize
    os.makedirs(os.path.dirname(user_path), exist_ok=True)
    data = {"user_templates": {}}
    if os.path.exists(user_path):
        with open(user_path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass

    # Slugify the name for the key and write back
    template_id = template_name.lower().replace(" ", "_")
    data["user_templates"][template_id] = new_template

    with open(user_path, "w") as f:
        json.dump(data, f, indent=4)
