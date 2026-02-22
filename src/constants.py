"""
Description: Global constants and dynamic path resolution for the 'src' layout.
"""

import os
from pathlib import Path

# BASE_DIR points to the 'src' directory where this file lives
BASE_DIR = Path(__file__).resolve().parent

# ROOT_DIR points to the 'datadict' directory (one level up)
ROOT_DIR = BASE_DIR.parent

# Resolve the path to the YAML file located in the root directory
MASTER_CONFIG_PATH = os.path.join(ROOT_DIR, "metadata_definition.yaml")

# Terminal diagnostic check
if not os.path.exists(MASTER_CONFIG_PATH):
    print(f"DEBUG: File NOT found at {MASTER_CONFIG_PATH}")
else:
    print(f"DEBUG: File found at {MASTER_CONFIG_PATH}")

# Library of common Regular Expressions for Spanish and general business contexts
REGEX_LIBRARY = {
    "Custom Pattern": "",
    "Spanish DNI (ID)": r"^[0-9]{8}[TRWAGMYFPDXBNJZSQVHLCKE]$",
    "Spanish NIE (Foreigner ID)": r"^[XYZ][0-9]{7}[TRWAGMYFPDXBNJZSQVHLCKE]$",
    "Spanish CIF (Company Tax ID)": r"^[ABCDEFGHJNPQRSUVW][0-9]{7}[0-9A-J]$",
    "Spanish Postal Code": r"^(?:0[1-9]|[1-4]\d|5[0-2])\d{3}$",
    "Spanish Phone (Mobile/Landline)": r"^(?:\+34|0034|34)?[6789]\d{8}$",
    "Spanish IBAN": r"^ES\d{2}\d{4}\d{4}\d{2}\d{10}$",
    "Email Address": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    "URL / Website": r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$",
    "Alphanumeric (No Spaces)": r"^[a-zA-Z0-9]+$",
}

TOOLTIP_DEFINITIONS = {
    "name": {
        "help": "Technical identifier for code/databases. Must use snake_case (e.g., user_signup_date). No spaces or special characters allowed."
    },
    "alias": {
        "help": "Business name in natural language. How stakeholders refer to this data in meetings or reports (e.g., 'Signup Date')."
    },
    "description": {
        "help": "Detailed dictionary definition. Include project-specific context, calculation logic, or business value for this variable."
    },
    "analytical_type": {
        "help": "Describes the mathematical nature and properties of the variable.",
        "continuous": "📏 Measured values with decimals (e.g., Price, Weight). These allow for precise mathematical scaling and averaging.",
        "discrete": "🔢 Countable whole numbers (e.g., Number of Children). Used for frequency counts; decimals are not logically possible.",
        "nominal": "🏷️ Unordered categories (e.g., Hair Color, City). Groups data where mathematical distance is meaningless.",
        "ordinal": "📶 Ordered categories with clear ranks (e.g., Size: S < M < L). Requires a numeric rank to preserve the logical sequence.",
        "binary": "⭕ Dual-state logic (e.g., Yes/No, 0/1). Highly efficient for classification models and True/False logic.",
        "text": "📝 Free-form unstructured text (e.g., Customer Reviews). Requires text-cleaning (lowercase, stripping) before processing.",
        "time_index": "📅 The primary chronological axis. Sets the temporal order for time-series analysis and forecasting.",
        "spatial": "📍 Geographic coordinates or locations (WKT, Lat/Long). Used for mapping and distance-based analysis.",
    },
    "data_type": {
        "help": "The technical format used for storage and computation.",
        "int64": "Whole numbers. The most memory-efficient format for counts and ID-based variables.",
        "float64": "Numbers with decimals. Necessary for high-precision measurements and currency values.",
        "string": "Text characters. Flexible for names but uses more memory than numeric types; ideal for categorical values.",
        "bool": "Logical True/False. Extremely fast processing with the smallest possible storage footprint.",
        "datetime64": "Timestamps. Enables chronological math like calculating age or time-elapsed between events.",
        "category": "Memory-optimized label system. Stores unique strings once; perfect for variables with many repeats like 'Status'.",
    },
    "role": {
        "help": "The functional purpose of this variable within your analysis or modeling project.",
        "target": "🎯 The 'Answer' column you want to predict (e.g., 'Will buy' vs 'Will not buy').",
        "feature": "⚙️ An input variable used to find patterns (e.g., 'Customer Age' helps predict 'Spend').",
        "id": "🔑 A unique key used only for tracking. This is never used for math or modeling.",
        "time_index": "📅 The master date/time column that defines the chronology of your dataset.",
        "group": "👥 A segmentation variable used to cluster data (e.g., 'Region' or 'Store ID').",
        "metadata": "ℹ️ Contextual data for human reference. Useful for logs but ignored by algorithms.",
    },
    "standardization": {
        "help": "Defines how to rescale numeric features to ensure they are on a comparable scale for algorithms.",
        "none": "Keep the original values. Scale is preserved as-is. Use if data is already scaled or if scale doesn't matter (e.g., Tree-based models).",
        "z-score": "Rescales data to a Mean of 0 and StdDev of 1. Essential for distance-based algorithms like SVM, KNN, or PCA.",
        "min-max": "Rescales values to a fixed [0, 1] range. Preferred for Neural Networks and preserving the sparsity of zero-values.",
        "robust": "Scales using Median and IQR. The best choice for data containing significant outliers that should not skew the scaling.",
    },
    "missing_strategy": {
        "help": "Sets the protocol for handling empty cells or missing observations.",
        "drop_row": "❌ Deletes the entire record. Use when the variable is critical and cannot be estimated.",
        "drop_col": "❌ Removes the variable entirely. Recommended only if more than 50% of the data is missing.",
        "mean": "📊 Fills empty cells with the average value. Use only for bell-curve distributed data.",
        "median": "📊 Fills with the middle value. More robust than 'Mean' for data with extreme outliers.",
        "mode": "📊 Fills with the most frequent value. The standard approach for Categorical data.",
        "constant": "📝 Fills with a fixed label (e.g., 'Unknown'). Keeps the record but marks the missingness clearly.",
        "ffill": "📉 Carries the last valid value forward. Mandatory for maintaining logic in Time Series data.",
        "keep": "👀 Retains empty cells. Preferred if your model (e.g., XGBoost) handles NaNs internally.",
        "maximum_likelihood": "🧮 Predicts missing values using statistical models based on other related data points.",
    },
    "outlier_strategy": {
        "help": "Sets the rule for extreme values that fall outside expected logical ranges.",
        "keep": "👀 No action. Outliers remain in the data. Use if extreme values are legitimate rare events.",
        "clip": "✂️ Capping. Replaces extreme values with a limit (e.g., Age 130 becomes 100) to reduce noise.",
        "drop": "❌ Deletion. Removes the row. Safest if you suspect the outlier is a typo or sensor error.",
        "flag": "🚩 Annotation. Keeps the value but adds a column marking the record for manual review.",
    },
    "preferred_plot": {
        "help": "Suggests the optimal chart type for automated reporting dashboards.",
        "histogram": "📊 Histogram: Shows the frequency and 'shape' of numeric distributions.",
        "boxplot": "📦 Boxplot: Highlights the median, quartiles, and identifies outliers visually.",
        "count_plot": "🏷️ Count Plot: Compares the frequency of different categories.",
        "line_chart": "📈 Line Chart: Displays changes, trends, and patterns over time.",
        "scatter_plot": "🌌 Scatter Plot: Reveals correlations between two numeric variables.",
        "not_needed": "⚪ No Plot: Skip visualization for IDs, unique strings, or non-visual data.",
    },
    "sensitivity": {
        "help": "Risk level of the data if accessed by unauthorized parties.",
        "Public": "🌍 General information safe for public release. No risk if leaked.",
        "Internal": "🏢 Company-use only. Not for public consumption but low risk to individuals.",
        "Confidential": "🔒 Restricted to specific departments (e.g., HR, Finance). Requires authorized access.",
        "Highly Confidential": "☣️ Critical sensitivity: Exposure could cause significant legal, financial, or reputational damage.",
        "PII": "👤 Personal: Directly identifies a human (Governed by Privacy Laws like GDPR).",
        "Restricted": "☢️ Highly sensitive secrets, passwords, or cryptographic keys. Extreme leak risk.",
    },
    "masking_strategy": {
        "help": "Method for obscuring sensitive data in non-production environments.",
        "none": "🔓 Unprotected: Original data is fully visible in all environments.",
        "hash": "🔐 Hashed: Scrambles data into an irreversible code; ideal for join-keys without exposing values.",
        "partial_mask": "🌗 Shielded: Shows only a part of the data (e.g., 'XXXX-XXXX-1234') for partial verification.",
        "redact": "⬛ Redacted: Replaces the entire value with a fixed string like '[REDACTED]'.",
    },
    "compliance_scope": {
        "help": "Identifies the regulatory frameworks governing this data.",
        "None": "⚖️ No specific regulatory constraints apply to this variable.",
        "GDPR (EU)": "🇪🇺 EU Data Privacy: Governs personal data, portability, and the 'right to be forgotten'.",
        "LOPDGDD (ES)": "🇪🇸 Spanish Privacy: Local implementation of GDPR with specific digital rights protections.",
        "ENS (ES)": "🛡️ National Security: Mandatory framework for Spanish Public Sector providers.",
        "LSSI-CE (ES)": "🛒 Digital Commerce: Regulation for E-commerce and cookie consent in Spain.",
        "PBC/FT (ES)": "💰 Anti-Money Laundering: Compliance standards for financial and real estate data.",
        "BdE Circulars (ES)": "🏦 Financial Reporting: Specific security standards from Banco de España.",
    },
    "database_mapping": {
        "target_table": "The physical destination in your database. Use format 'schema_name.table_name' (e.g., 'dm_sales.fact_orders').",
        "is_primary_key": {
            "help": "Identifies if this column is the unique ID for every row in the table.",
            "true": "🔑 Unique Row Identity. This column serves as the 'Source of Truth' and cannot be empty.",
            "false": "⚪ Standard Column. A regular descriptive attribute in the table.",
        },
        "foreign_key_reference": "🔗 Referential Link: Format 'table_name(column_name)'. Connects this column to an ID in another table.",
    },
    "ordinal_mapping": {"info": "Establishes a mathematical order for categories (e.g., Low=1, Medium=2, High=3)."},
    "frequency": {
        "N": "Nanoseconds: High-frequency engineering or physics data.",
        "U": "Microseconds: Precise system logs or high-frequency trading.",
        "L": "Milliseconds (ms): Standard for sensor data and web logs.",
        "S": "Seconds: Real-time telemetry and monitoring.",
        "min": "Minutes: Standard interval for IoT and traffic data.",
        "15min": "15-Minute: Common for utility billing and retail metrics.",
        "H": "Hourly: Standard for weather, energy, and hourly sales.",
        "D": "Daily: One observation per calendar day.",
        "B": "Business Day: Skips weekends (Saturday/Sunday).",
        "W": "Weekly: Observations every Sunday.",
        "W-MON": "Weekly (Monday): Standard for business reporting cycles.",
        "M": "Monthly: Month-end frequency.",
        "BM": "Business Month-end: Last working day of the month.",
        "MS": "Month Start: First day of the month.",
        "Q": "Quarterly: Standard for financial reporting (Q1, Q2, etc.).",
        "A": "Yearly: Annual observations (Year-end).",
        "BA": "Business Year-end: Last working day of the year.",
    },
    "nullable": {
        "true": "Field is optional. Missing values are allowed for this variable.",
        "false": "Field is mandatory. Data collection will fail if this value is missing.",
    },
    "pii_flag": {
        "true": "Contains personal identifiers. Triggers mandatory masking and privacy access controls.",
        "false": "Contains no personal information.",
    },
    "unique": {
        "help": "Ensures that every record in the dataset has a different value for this variable.",
        "true": "Mandatory uniqueness (e.g., Email). Prevents record duplication.",
        "false": "Duplicates allowed (e.g., multiple entries for the same 'Date').",
    },
}
