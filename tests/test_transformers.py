# Description: Unit tests for the data transformation engine.
# Verifies the bidirectional conversion between nested JSON blueprints and flat Pandas DataFrames.

import pandas as pd

from logic.transformers import generate_batch_dataframe, hydrate_row_from_flat


def test_hydrate_row_from_flat_basic():
    """
    Tests if a flat dictionary (mimicking a grid row) correctly rebuilds
    its nested 'constraints' and 'cleaning' subsections.
    """
    # Arrange
    flat_input = {
        "name": "customer_age",
        "analytical_type": "continuous",
        "data_type": "float64",
        "role": "feature",
        "constraints_min_value": 18.0,
        "constraints_max_value": 99.0,
        "cleaning_outlier_strategy": "clip",
    }

    # Act
    nested_output = hydrate_row_from_flat(flat_input)

    # Assert
    assert nested_output["name"] == "customer_age"
    assert nested_output["constraints"]["min_value"] == 18.0
    assert nested_output["constraints"]["max_value"] == 99.0
    assert nested_output["cleaning"]["outlier_strategy"] == "clip"
    # Ensure empty sections are initialized
    assert nested_output["governance"] == {}


def test_hydrate_row_from_flat_ignores_nans():
    """
    Tests if Pandas NaN values (representing empty cells in the UI)
    are correctly ignored and excluded from the nested JSON.
    """
    # Arrange
    import numpy as np

    flat_input = {
        "name": "transaction_id",
        "constraints_unique": True,
        "constraints_regex_pattern": np.nan,  # Simulating an empty UI cell
        "cleaning_infinite_value_handling": None,
    }

    # Act
    nested_output = hydrate_row_from_flat(flat_input)

    # Assert
    assert "unique" in nested_output["constraints"]
    assert "regex_pattern" not in nested_output["constraints"]


def test_generate_batch_dataframe():
    """
    Tests if the DataFrame generator builds the exact requested dimensions
    and flattens the blueprint properly.
    """
    # Arrange
    template_blueprint = {
        "analytical_type": "nominal",
        "data_type": "category",
        "role": "feature",
        "constraints": {"nullable": False},
    }
    target_row_count = 5

    # Act
    df = generate_batch_dataframe(template_blueprint, target_row_count)

    # Assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert "Row #" in df.columns
    assert "constraints_nullable" in df.columns
    assert df.iloc[0]["constraints_nullable"] is False
