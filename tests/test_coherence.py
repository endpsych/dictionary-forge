# Description: Unit tests for the technical coherence engine.
# Verifies that analytical types return the correct allowed technical data types.

from logic.coherence import get_filtered_data_types


def test_get_filtered_data_types_continuous():
    """Tests if a 'continuous' type correctly locks to 'float64'."""
    # Arrange
    input_type = "continuous"
    expected_output = ["float64"]

    # Act
    actual_output = get_filtered_data_types(input_type)

    # Assert
    assert actual_output == expected_output


def test_get_filtered_data_types_fallback():
    """Tests the fallback mechanism for unknown types."""
    # Arrange
    input_type = "random_garbage_string"
    expected_output = ["object"]

    # Act
    actual_output = get_filtered_data_types(input_type)

    # Assert
    assert actual_output == expected_output
