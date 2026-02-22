"""
Description: Package initializer for the logic module.
Exposes the refactored engines (Coherence, Exporters, Transformers, Blueprints)
as a unified API for the Dictionary Forge application.
"""

# 1. Technical Coherence & Validation
# 4. Template & Blueprint Management
from .blueprints import (
    apply_template_to_state,
    load_all_templates,
    load_master_schema,
    save_user_template,
)
from .coherence import (
    get_dynamic_label,
    get_field_requirement,
    get_filtered_data_types,
    get_filtered_roles,
    guess_metadata_from_name,
    is_field_visible,
    validate_categorical_entropy,
)

# 2. Data Export & SQL Generation
from .exporters import flatten_json, generate_sql_script

# 5. Governance & Compliance
from .governance import load_regulations, save_regulations

# 3. Data Transformation & Grid Hydration
from .transformers import generate_batch_dataframe, hydrate_row_from_flat

__all__ = [
    "get_filtered_data_types",
    "get_filtered_roles",
    "is_field_visible",
    "get_dynamic_label",
    "get_field_requirement",
    "validate_categorical_entropy",
    "guess_metadata_from_name",
    "flatten_json",
    "generate_sql_script",
    "hydrate_row_from_flat",
    "generate_batch_dataframe",
    "load_master_schema",
    "load_all_templates",
    "apply_template_to_state",
    "save_user_template",
    "load_regulations",
    "save_regulations",
]
