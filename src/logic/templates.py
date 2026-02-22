"""
Description: Logic for managing variable metadata templates.
Handles directory discovery, reading YAML templates, and persisting new library entries.
"""

import os

import yaml

from constants import ROOT_DIR

TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")


def get_template_list():
    """Returns a list of available .yaml template names."""
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        return []
    return [f.replace(".yaml", "") for f in os.listdir(TEMPLATES_DIR) if f.endswith(".yaml")]


def load_template_data(template_name):
    """Reads a specific template file and returns the dictionary."""
    path = os.path.join(TEMPLATES_DIR, f"{template_name}.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def save_template_data(name, data):
    """Persists current variable metadata to the template library."""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    path = os.path.join(TEMPLATES_DIR, f"{name}.yaml")
    with open(path, "w") as f:
        yaml.dump(data, f, sort_keys=False)


def delete_template(template_name):
    """
    Removes a template file from the library.
    Returns True if successful, False otherwise.
    """
    path = os.path.join(TEMPLATES_DIR, f"{template_name}.yaml")
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
    except Exception:
        return False
