"""
Description: Export utility functions for Dictionary Forge
"""

import io
import json

import pandas as pd
import yaml


def generate_yaml(export_obj):
    """Generates a YAML string from the export object."""
    return yaml.dump(export_obj, sort_keys=False)


def generate_json(export_obj):
    """Generates a formatted JSON string from the export object."""
    return json.dumps(export_obj, indent=4)


def generate_csv(df_preview):
    """Generates a CSV string from the flattened DataFrame."""
    csv_buffer = io.StringIO()
    df_preview.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()


def generate_excel(df_preview, project_info):
    """Generates an Excel binary buffer with separate sheets for variables and metadata."""
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        # Variables Sheet
        df_preview.to_excel(writer, sheet_name="Variables", index=False)
        # Project Metadata Sheet
        pd.DataFrame([project_info]).to_excel(writer, sheet_name="Project Info", index=False)
    return excel_buffer.getvalue()
