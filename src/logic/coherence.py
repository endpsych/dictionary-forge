"""
Description: Technical Coherence Engine for Dictionary Forge
Handles data type filtering, role enforcement, and context-aware UI logic.
Part of the 'logic' module refactor.
"""


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
