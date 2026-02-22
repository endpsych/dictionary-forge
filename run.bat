@echo off
title Dictionary Forge - Launching
echo Starting the Dictionary Forge application...
:: Use 'uv run' to ensure it uses the isolated project environment
uv run streamlit run src/app.py
pause