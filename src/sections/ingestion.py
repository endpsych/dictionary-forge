"""
Description: Handles loading drafts from the bulk ingestion queue.
"""

import streamlit as st

from logic import guess_metadata_from_name


def render_queue_integration_section():
    if st.session_state.get("editing_index") is not None:
        return

    if st.session_state.get("pending_variables"):
        # 1. Inject CSS targeting the expander that contains the "Pending Ingestion Queue" text
        st.markdown(
            """
            <style>
            /* Target the expander by its internal label text */
            div[data-testid="stExpander"]:has(p:contains("Pending Ingestion Queue")) {
                border: 2px solid #FF4B4B !important;
                border-radius: 0.5rem;
                background-color: rgba(255, 75, 75, 0.05);
            }
            /* Add a subtle pulse animation to make it even more salient */
            div[data-testid="stExpander"]:has(p:contains("Pending Ingestion Queue")) {
                animation: pulse-red 2s infinite;
            }
            @keyframes pulse-red {
                0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
                70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        # 2. Render the expander normally
        with st.expander(
            f"📥 Pending Ingestion Queue ({len(st.session_state['pending_variables'])} variables)",
            expanded=True,
        ):
            st.info("Variables found in the batch queue. Select one to auto-fill the form and define it.")

            q_col1, q_col2 = st.columns([3, 1])
            with q_col1:
                selected_queued_var = st.selectbox(
                    "Select variable to define:",
                    ["--- Select ---"] + st.session_state["pending_variables"],
                    key="queue_selector",
                    label_visibility="collapsed",
                )
            with q_col2:
                if (
                    st.button("Load Draft", use_container_width=True, type="primary")
                    and selected_queued_var != "--- Select ---"
                ):
                    st.session_state["form_id"] += 1
                    fid = st.session_state["form_id"]
                    guesses = guess_metadata_from_name(selected_queued_var)

                    # Hydrate state for the main form
                    st.session_state[f"f{fid}__name"] = selected_queued_var
                    st.session_state[f"v_at_{fid}"] = guesses["analytical_type"]
                    st.session_state[f"f{fid}__data_type"] = guesses["data_type"]
                    st.session_state[f"f{fid}__role"] = guesses["role"]

                    st.rerun()
