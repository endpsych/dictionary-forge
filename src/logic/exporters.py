"""
# Description: Data Export and Transformation Engine for Dictionary Forge
"""


def flatten_json(y):
    """
    Flattens a nested dictionary for tabular export.
    """
    out = {}

    def flatten(x, name=""):
        if isinstance(x, dict):
            # Recursively drill down into all dictionaries
            for a in x:
                flatten(x[a], name + a + "_")
        elif isinstance(x, list):
            # Convert lists (like 'allowed_values') to comma-separated strings
            out[name[:-1]] = ", ".join(map(str, x))
        else:
            # Assign standard values directly
            out[name[:-1]] = x

    flatten(y)
    return out


def generate_sql_script(variables):
    """
    Translates the dictionary metadata into PostgreSQL CREATE TABLE syntax.
    Handles data type mapping, primary keys, and foreign key references.
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
            dtype = var.get("data_type")
            constraints = var.get("constraints", {})
            db_mapping = var.get("database_mapping", {})

            # Type Mapping: Python/Pandas -> PostgreSQL
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

            # Construct Column String
            col_str = f"    {col_name} {pg_type}"

            if db_mapping.get("is_primary_key"):
                col_str += " PRIMARY KEY"
            else:
                if constraints.get("unique"):
                    col_str += " UNIQUE"
                if constraints.get("nullable") is False:
                    col_str += " NOT NULL"

            # In-line Checks (Allowed Values / Ranges)
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

            # Foreign Key Registration
            fk_ref = db_mapping.get("foreign_key_reference", "").strip()
            if fk_ref:
                fk_defs.append(f"    FOREIGN KEY ({col_name}) REFERENCES {fk_ref}")

        sql_lines.append(",\n".join(col_defs + fk_defs))
        sql_lines.append(");\n")

    return "\n".join(sql_lines)
