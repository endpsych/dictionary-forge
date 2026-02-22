"""
Description: Governance UI section for PII, data masking, and compliance scope.
"""

import streamlit as st

from components.variable_form.widgets import render_input_field


def render_governance_section(nested_sections, current_at, current_dt, v_inputs, edit_data=None):
    """
    Renders fields related to data privacy, regulatory compliance, and ownership.
    Prioritizes Ground Truth (edit_data) to ensure coherence with Templates and Ledger.
    """
    # Extract section-specific ground truth
    edit_gov = edit_data.get("governance", {}) if edit_data else {}
    gov_data = {}

    with st.container(border=True):
        # --- ROW 1: Ownership & Source ---
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            res_ds = render_input_field(
                {"name": "data_steward", "dtype": "string"},
                prefix="governance",
                edit_value=edit_gov.get("data_steward"),
            )
            if res_ds:
                gov_data["data_steward"] = res_ds
        with r1c2:
            res_ss = render_input_field(
                {"name": "source_system", "dtype": "string"},
                prefix="governance",
                edit_value=edit_gov.get("source_system"),
            )
            if res_ss:
                gov_data["source_system"] = res_ss

        st.write("")

        # --- ROW 2: Privacy & Security ---
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            res_sens = render_input_field(
                {
                    "name": "sensitivity",
                    "dtype": "enum",
                    "options": [
                        "Public",
                        "Internal",
                        "Confidential",
                        "Highly Confidential",
                        "PII",
                        "Restricted",
                    ],
                },
                prefix="governance",
                edit_value=edit_gov.get("sensitivity"),
            )
            if res_sens:
                gov_data["sensitivity"] = res_sens
        with r2c2:
            res_mask = render_input_field(
                {
                    "name": "masking_strategy",
                    "dtype": "enum",
                    "options": ["none", "hash", "partial_mask", "redact"],
                },
                prefix="governance",
                edit_value=edit_gov.get("masking_strategy"),
            )
            if res_mask:
                gov_data["masking_strategy"] = res_mask

        st.write("")

        # --- ROW 3: Compliance & PII ---
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            # Note: widgets.py handle dynamic loading of regulations if name is compliance_scope
            res_comp = render_input_field(
                {
                    "name": "compliance_scope",
                    "dtype": "multiselect",
                    "options": ["GDPR", "CCPA", "HIPAA", "SOX", "PCI-DSS", "FERPA"],
                },
                prefix="governance",
                edit_value=edit_gov.get("compliance_scope", []),
            )
            if res_comp:
                gov_data["compliance_scope"] = res_comp
        with r3c2:
            res_pii = render_input_field(
                {"name": "pii_flag", "dtype": "boolean"},
                prefix="governance",
                edit_value=edit_gov.get("pii_flag"),
            )
            if res_pii is not None:
                gov_data["pii_flag"] = res_pii

        st.write("")

        # --- ROW 4: Retention & Cadence ---
        r4c1, r4c2 = st.columns(2)
        with r4c1:
            res_ret = render_input_field(
                {
                    "name": "retention_period",
                    "dtype": "enum",
                    "options": [
                        "Transient (Not Stored)",
                        "1 Year",
                        "3 Years",
                        "5 Years",
                        "7 Years",
                        "10 Years",
                        "Indefinite",
                    ],
                },
                prefix="governance",
                edit_value=edit_gov.get("retention_period"),
            )
            if res_ret:
                gov_data["retention_period"] = res_ret

        with r4c2:
            res_freq = render_input_field(
                {
                    "name": "update_frequency",
                    "dtype": "enum",
                    "options": [
                        "Real-time",
                        "Hourly",
                        "Daily",
                        "Weekly",
                        "Monthly",
                        "Quarterly",
                        "Yearly",
                        "Static",
                    ],
                },
                prefix="governance",
                edit_value=edit_gov.get("update_frequency"),
            )
            if res_freq:
                gov_data["update_frequency"] = res_freq

    # Bridge results to main input collection
    if gov_data:
        v_inputs["governance"] = gov_data
