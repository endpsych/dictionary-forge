"""
Description: Core logic for Dictionary Forge
Implements multi-layered coherence matrices for Analytical, Technical, and Functional Roles.
Features: Smart Heuristics, PostgreSQL DDL Compiler, and Dynamic Field Visibility.
"""

import json
import os

import pandas as pd
import streamlit as st
import yaml


def load_master_schema(config_path):
    """
    Loads the YAML blueprint. Raises FileNotFoundError if missing.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


# ==============================================================================
# 1. TEMPLATE SYSTEM LOGIC
# ==============================================================================


def load_all_templates(
    standard_path="config/templates_standard.yaml",
    user_path="config/templates_user.json",
):
    """
    Merges hard-coded standard templates with user-defined templates.
    Returns a dictionary of available templates for the UI.
    """
    all_templates = {}

    # 1. Load Standard (YAML)
    if os.path.exists(standard_path):
        with open(standard_path) as f:
            std_data = yaml.safe_load(f)
            if std_data and "templates" in std_data:
                all_templates.update(std_data["templates"])

    # 2. Load User (JSON)
    if os.path.exists(user_path):
        if not os.path.exists(os.path.dirname(user_path)):
            os.makedirs(os.path.dirname(user_path), exist_ok=True)

        with open(user_path) as f:
            try:
                user_data = json.load(f)
                if user_data and "user_templates" in user_data:
                    all_templates.update(user_data["user_templates"])
            except json.JSONDecodeError:
                pass

    return all_templates


def apply_template_to_state(template_data, fid):
    """
    Destructive overwrite handler. Purges current form state and injects template data.
    Preserves unique identification fields (Name, Alias, Description).
    """
    # Identification keys to preserve (we don't want to lose the specific variable name)
    preserve_keys = [f"f{fid}__name", f"f{fid}__alias", f"f{fid}__description"]
    form_prefix = f"f{fid}__"
    v_at_key = f"v_at_{fid}"

    # 1. Purge existing form-related state
    for key in list(st.session_state.keys()):
        if (key.startswith(form_prefix) or key == v_at_key) and key not in preserve_keys:
            del st.session_state[key]

    # 2. Inject core technical config from template
    st.session_state[v_at_key] = template_data.get("analytical_type", "continuous")
    st.session_state[f"{form_prefix}data_type"] = template_data.get("data_type", "float64")
    st.session_state[f"{form_prefix}role"] = template_data.get("role", "feature")

    # 3. Inject nested metadata (constraints, cleaning, etc.)
    # The template structure mirrors the v_inputs structure
    for section in ["constraints", "cleaning", "governance", "database_mapping"]:
        if section in template_data:
            section_vals = template_data[section]
            for field, val in section_vals.items():
                # Handle categorical rows specifically to hydrate the UI list
                if field == "allowed_values" and section == "constraints":
                    st.session_state["cat_rows"] = [{"label": v, "rank": i + 1} for i, v in enumerate(val)]
                    st.session_state["cat_rows_hydrated"] = True
                else:
                    # Flattened keys for widgets (e.g., f0__constraints_min_value)
                    st.session_state[f"{form_prefix}{section}_{field}"] = val


def save_user_template(template_name, v_inputs, user_path="config/templates_user.json"):
    """
    Saves a current form configuration as a reusable user blueprint.
    Strips unique identifiers (name/alias) to keep templates generic.
    """
    import copy

    new_template = copy.deepcopy(v_inputs)

    # Strip unique identifiers
    new_template.pop("name", None)
    new_template.pop("alias", None)
    new_template.pop("description", None)
    new_template["label"] = template_name

    # Ensure path exists and load data
    os.makedirs(os.path.dirname(user_path), exist_ok=True)
    data = {"user_templates": {}}
    if os.path.exists(user_path):
        with open(user_path) as f:
            try:
                data = json.load(f)
            except Exception:
                pass

    # Append and write back
    template_id = template_name.lower().replace(" ", "_")
    data["user_templates"][template_id] = new_template

    with open(user_path, "w") as f:
        json.dump(data, f, indent=4)


# ==============================================================================
# 2. COHERENCE & VALIDATION LOGIC
# ==============================================================================


def get_filtered_data_types(analytical_type):
    """
    Enforces technical data coherence based on the analytical nature.
    """
    mapping = {
        "continuous": ["float64"],
        "discrete": ["int64"],
        "nominal": ["category", "string", "bool"],
        "ordinal": ["category"],
        "binary": ["bool", "int64"],
        "text": ["string"],
        "time_index": ["datetime64"],
        "spatial": ["float64", "string"],
    }
    return mapping.get(analytical_type, ["object"])


def get_filtered_roles(analytical_type, data_type=None):
    """
    Enforces functional role restriction to prevent logical analytical conflicts.
    """
    all_roles = ["feature", "target", "id", "time_index", "group", "metadata"]

    if analytical_type == "time_index" or data_type == "datetime64":
        return ["time_index"]

    if analytical_type == "text":
        return ["feature", "metadata"]

    if analytical_type == "spatial":
        return ["feature", "metadata"]

    if analytical_type == "binary":
        return ["feature", "target", "group", "metadata"]

    if analytical_type == "continuous":
        return ["feature", "target", "group", "metadata"]

    if analytical_type == "nominal":
        return ["feature", "target", "id", "group", "metadata"]

    return all_roles


def is_field_visible(field_name, analytical_type, data_type=None):
    """
    Determines if a metadata field is applicable based on the technical context.
    """
    if field_name in ["plot_color", "formatting"]:
        return False

    if analytical_type in ["continuous", "discrete"]:
        if field_name in [
            "allowed_values",
            "regex_pattern",
            "ordinal_mapping",
            "text_normalization",
            "encoding_strategy",
        ]:
            return False

    if analytical_type == "binary":
        forbidden = [
            "min_value",
            "max_value",
            "regex_pattern",
            "allowed_values",
            "ordinal_mapping",
            "unique",
            "outlier_strategy",
            "outlier_threshold",
            "standardization_strategy",
            "infinite_value_handling",
            "text_normalization",
        ]
        if field_name in forbidden:
            return False

    if analytical_type == "nominal":
        if field_name in [
            "outlier_strategy",
            "outlier_threshold",
            "ordinal_mapping",
            "standardization_strategy",
            "infinite_value_handling",
            "text_normalization",
        ]:
            return False

    if analytical_type == "text":
        if field_name in [
            "outlier_strategy",
            "outlier_threshold",
            "ordinal_mapping",
            "standardization_strategy",
            "infinite_value_handling",
            "encoding_strategy",
        ]:
            return False

    if analytical_type == "time_index":
        forbidden = [
            "allowed_values",
            "regex_pattern",
            "outlier_strategy",
            "outlier_threshold",
            "ordinal_mapping",
            "standardization_strategy",
            "infinite_value_handling",
            "text_normalization",
            "encoding_strategy",
        ]
        if field_name in forbidden:
            return False

    if analytical_type == "ordinal":
        if field_name in [
            "regex_pattern",
            "outlier_strategy",
            "outlier_threshold",
            "standardization_strategy",
            "infinite_value_handling",
            "text_normalization",
        ]:
            return False
    elif field_name == "ordinal_mapping":
        return False

    if field_name in ["standardization_strategy", "infinite_value_handling"] and analytical_type != "continuous":
        return False

    if field_name == "text_normalization" and analytical_type != "text":
        return False

    if field_name == "encoding_strategy" and analytical_type not in [
        "nominal",
        "ordinal",
        "binary",
    ]:
        return False

    if data_type:
        if data_type == "string" and field_name in [
            "outlier_strategy",
            "outlier_threshold",
            "ordinal_mapping",
            "standardization_strategy",
        ]:
            return False
        if data_type == "category" and field_name in [
            "min_value",
            "max_value",
            "regex_pattern",
            "outlier_strategy",
            "outlier_threshold",
            "standardization_strategy",
        ]:
            return False
        if data_type == "bool" and field_name in [
            "min_value",
            "max_value",
            "regex_pattern",
            "allowed_values",
            "unique",
            "outlier_strategy",
            "outlier_threshold",
            "ordinal_mapping",
            "standardization_strategy",
        ]:
            return False

    return True


def get_dynamic_label(field_name, analytical_type):
    """
    Transforms field names into context-aware human labels based on analytical type.
    """
    label = field_name.replace("_", " ").title()

    if field_name == "min_value":
        if analytical_type in ["continuous", "discrete", "spatial"]:
            return "Lower Numeric Bound"
        if analytical_type in ["text", "nominal", "ordinal"]:
            return "Minimum Character Length"
        if analytical_type == "time_index":
            return "Start Date"

    if field_name == "max_value":
        if analytical_type in ["continuous", "discrete", "spatial"]:
            return "Upper Numeric Bound"
        if analytical_type in ["text", "nominal", "ordinal"]:
            return "Maximum Character Length"
        if analytical_type == "time_index":
            return "End Date"

    if field_name == "pii_flag":
        return "Contains PII?"
    if field_name == "compliance_scope":
        return "Regulatory Compliance"
    if field_name == "retention_period":
        return "Data Retention Period"
    if field_name == "sla":
        return "Service Level Agreement (SLA)"

    return label


def get_field_requirement(field_name, analytical_type, data_type):
    """
    Determines if a field is mandatory based on technical coherence.
    """
    if field_name == "allowed_values" and data_type == "category":
        return True
    if field_name == "ordinal_mapping" and analytical_type == "ordinal":
        return True
    if field_name in ["unique", "nullable"] and analytical_type == "nominal" and data_type == "string":
        return True
    if field_name in ["data_steward", "sensitivity"]:
        return True
    return False


def validate_categorical_entropy(allowed_values):
    """
    Ensures a categorical variable has sufficient variance (N >= 2).
    """
    if not allowed_values:
        return False, "Category type requires an 'Allowed Values' list."

    unique_values = {v.strip() for v in allowed_values if v.strip()}

    if len(unique_values) < 2:
        return (
            False,
            f"Insufficient variance. Categories require at least 2 unique values (Found: {len(unique_values)}).",
        )

    return True, ""


def flatten_json(y):
    """
    Flattens a nested dictionary for tabular export.
    """
    out = {}

    def flatten(x, name=""):
        if isinstance(x, dict):
            if name.endswith(
                (
                    "ordinal_mapping_",
                    "constraints_",
                    "cleaning_",
                    "governance_",
                    "database_mapping_",
                )
            ):
                out[name[:-1]] = str(x)
            else:
                for a in x:
                    flatten(x[a], name + a + "_")
        elif isinstance(x, list):
            out[name[:-1]] = str(x)
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def generate_sql_script(variables):
    """
    Translates the dictionary metadata into PostgreSQL CREATE TABLE syntax.
    """
    tables = {}
    for var in variables:
        db_mapping = var.get("database_mapping", {})
        table_name = db_mapping.get("target_table", "").strip()
        if not table_name:
            table_name = "public_schema_table"
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append(var)

    sql_lines = ["-- Auto-generated PostgreSQL Schema by Dictionary Forge\n"]
    for table_name, table_vars in tables.items():
        sql_lines.append(f"CREATE TABLE {table_name} (")
        col_defs, fk_defs = [], []
        for var in table_vars:
            col_name = var.get("name", "unknown_column").replace(" ", "_").lower()
            dtype, constraints, db_mapping = (
                var.get("data_type"),
                var.get("constraints", {}),
                var.get("database_mapping", {}),
            )

            pg_type = "TEXT"
            if dtype == "int64":
                pg_type = "BIGINT"
            elif dtype == "float64":
                pg_type = "DOUBLE PRECISION"
            elif dtype == "bool":
                pg_type = "BOOLEAN"
            elif dtype == "datetime64":
                pg_type = "TIMESTAMP"
            elif dtype in ["string", "category"]:
                max_len = constraints.get("max_value")
                pg_type = f"VARCHAR({max_len})" if max_len and isinstance(max_len, int) else "VARCHAR(255)"

            col_str = f"    {col_name} {pg_type}"
            if db_mapping.get("is_primary_key"):
                col_str += " PRIMARY KEY"
            else:
                if constraints.get("unique"):
                    col_str += " UNIQUE"
                if constraints.get("nullable") is False:
                    col_str += " NOT NULL"

            allowed_vals = constraints.get("allowed_values")
            if allowed_vals and isinstance(allowed_vals, list):
                escaped = [f"'{str(v).replace(chr(39), chr(39) + chr(39))}'" for v in allowed_vals]
                col_str += f" CHECK ({col_name} IN ({', '.join(escaped)}))"
            elif dtype in ["int64", "float64"]:
                min_v, max_v = (
                    constraints.get("min_value"),
                    constraints.get("max_value"),
                )
                if min_v is not None:
                    col_str += f" CHECK ({col_name} >= {min_v})"
                if max_v is not None:
                    col_str += f" CHECK ({col_name} <= {max_v})"

            col_defs.append(col_str)
            fk_ref = db_mapping.get("foreign_key_reference", "").strip()
            if fk_ref:
                fk_defs.append(f"    FOREIGN KEY ({col_name}) REFERENCES {fk_ref}")

        sql_lines.append(",\n".join(col_defs + fk_defs))
        sql_lines.append(");\n")

    return "\n".join(sql_lines)


def guess_metadata_from_name(variable_name):
    """
    Heuristic engine to infer default analytical and technical types.
    """
    name_lower = str(variable_name).lower()
    defaults = {
        "analytical_type": "continuous",
        "data_type": "float64",
        "role": "feature",
    }

    if name_lower.endswith("_id") or name_lower == "id":
        defaults.update({"analytical_type": "discrete", "data_type": "int64", "role": "id"})
    elif name_lower.endswith(("_date", "_at", "_time")):
        defaults.update(
            {
                "analytical_type": "time_index",
                "data_type": "datetime64",
                "role": "time_index",
            }
        )
    elif name_lower.startswith(("is_", "has_", "flag_")):
        defaults.update({"analytical_type": "binary", "data_type": "bool", "role": "feature"})
    elif any(x in name_lower for x in ["name", "email", "desc"]):
        defaults.update({"analytical_type": "text", "data_type": "string", "role": "metadata"})
    elif any(x in name_lower for x in ["_cat", "_type", "_status"]):
        defaults.update({"analytical_type": "nominal", "data_type": "category", "role": "feature"})

    return defaults


# ==============================================================================
# 3. BATCH FORGE LOGIC
# ==============================================================================


def hydrate_row_from_flat(flat_row):
    """
    Takes a flat dictionary (from a dataframe row) and reconstructs
    the nested metadata structure (constraints, cleaning, etc.).
    """
    nested_var = {
        "name": flat_row.get("name"),
        "alias": flat_row.get("alias"),
        "description": flat_row.get("description"),
        "analytical_type": flat_row.get("analytical_type"),
        "data_type": flat_row.get("data_type"),
        "role": flat_row.get("role"),
        "constraints": {},
        "cleaning": {},
        "governance": {},
        "database_mapping": {},
        "visualization": {},
    }

    for key, value in flat_row.items():
        # Ensure prefix matching aligns with the 'prefix' argument in your sections
        for section in [
            "constraints",
            "cleaning",
            "governance",
            "database",
            "visualization",
        ]:
            # Map 'database' prefix back to 'database_mapping' key
            target_key = "database_mapping" if section == "database" else section
            prefix = f"{section}_"

            if key.startswith(prefix) and value is not None:
                # Safely ignore pandas NaNs which represent empty cells in the grid
                if isinstance(value, float) and pd.isna(value):
                    continue

                field_name = key.replace(prefix, "")
                nested_var[target_key][field_name] = value

    return nested_var


def generate_batch_dataframe(template_data, row_count):
    """
    Creates a flat Pandas DataFrame based on a template to populate the UI grid.
    Flattens nested sections using the standard section_field naming convention.
    """
    # Flatten the template to get initial values
    flat_template = {
        "Row #": 0,  # Placeholder for the visual counter
        "name": "",
        "alias": "",
        "description": "",
        "analytical_type": template_data.get("analytical_type"),
        "data_type": template_data.get("data_type"),
        "role": template_data.get("role"),
    }

    # Mapping for flattening
    sections_to_flatten = {
        "constraints": "constraints",
        "cleaning": "cleaning",
        "governance": "governance",
        "database_mapping": "database",  # Flattens to database_field
        "visualization": "visualization",
    }

    for source_key, prefix in sections_to_flatten.items():
        if source_key in template_data:
            for field, val in template_data[source_key].items():
                flat_template[f"{prefix}_{field}"] = val

    df = pd.DataFrame([flat_template] * row_count)
    df["Row #"] = range(1, row_count + 1)

    return df
