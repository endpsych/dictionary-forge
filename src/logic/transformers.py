"""
Description: Data Transformation and Hydration Engine for Dictionary Forge
"""

import pandas as pd


def hydrate_row_from_flat(flat_row):
    """
    Takes a flat dictionary (representing a single row from a dataframe)
    and reconstructs the nested metadata structure (constraints, cleaning, etc.).
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
    }

    for key, value in flat_row.items():
        # Map flat keys like 'constraints_min_value' into their respective nested dicts
        for section in ["constraints", "cleaning", "governance", "database_mapping"]:
            prefix = f"{section}_"
            if key.startswith(prefix) and value is not None:
                # Safely ignore pandas NaNs which represent empty cells in the grid
                if isinstance(value, float) and pd.isna(value):
                    continue

                field_name = key.replace(prefix, "")
                nested_var[section][field_name] = value

    return nested_var


def generate_batch_dataframe(template_data, row_count):
    """
    Creates a flat Pandas DataFrame based on a blueprint template to populate the UI grid.
    Includes a purely visual 'Row #' counter for user reference.
    """
    # Flatten the template to get initial default values for the grid
    flat_template = {
        "Row #": 0,  # Placeholder for the visual counter
        "name": "",
        "alias": "",
        "description": "",
        "analytical_type": template_data.get("analytical_type"),
        "data_type": template_data.get("data_type"),
        "role": template_data.get("role"),
    }

    # Extract nested sections into flattened key-value pairs
    for section in ["constraints", "cleaning", "governance", "database_mapping"]:
        if section in template_data:
            for field, val in template_data[section].items():
                flat_template[f"{section}_{field}"] = val

    # Create the dataframe and inject the sequential row counter
    df = pd.DataFrame([flat_template] * row_count)
    df["Row #"] = range(1, row_count + 1)

    return df
