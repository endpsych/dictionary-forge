# 📘 Dictionary Forge

**A universal, deterministic engine for generating and governing data dictionaries across diverse data ecosystems.**

Dictionary Forge is a professional-grade application designed to bridge the gap between logical data definitions and physical database implementations. It provides a robust interface for data architects and engineers to build standardized metadata repositories that are consistent, audited, and ready for deployment.

---


![App Screenshot](assets/app_screenshot.png)


---

## 🚀 Installation & Launch

Choose the method that best fits your workflow. Both methods ensure an isolated, high-performance environment using the `uv` package manager.

### Option A: Standard Launch (Non-Technical / One-Click)

Designed for reviewers who want to see the app immediately without using a terminal.

1. **Download** : Click the green **Code** button at the top and select  **Download ZIP** . Extract the folder.
2. **Setup** : Double-click `setup.bat`. This will automatically install `uv` and prepare the environment (Run this only once).
3. **Launch** : Double-click `run.bat`. The application will open automatically in your default browser.

### Option B: Developer Launch (CLI)

For users who prefer a traditional terminal-based setup.

**Bash**

```
# 1. Clone the repository
git clone https://github.com/your-username/dictionary-forge.git
cd dictionary-forge

# 2. Sync dependencies and create virtual environment
uv sync

# 3. Run the application
uv run streamlit run src/app.py
```

## ✨ Core Features

### 🛠️ Precision Metadata Modeling

Define exhaustive technical constraints to ensure downstream data quality:

* **Context-Aware Type System** : Support for diverse analytical types (Continuous, Nominal, Ordinal, Time-Series).
* **Strict Constraints** : Implement  **Regex patterns** , **numeric range limits** , and  **categorical allowed values** .
* **Automatic Coherence** : The engine dynamically prunes incompatible constraints based on your data type selections.

### 🏛️ Integrated Data Governance

* **Governance Metadata** : Capture sensitivity levels, PII (Personally Identifiable Information) flags, and ownership details.
* **Regulation Repository** : Access a built-in library of global regulations (GDPR, CCPA, etc.) with direct links to documentation to inform your governance decisions.

### ⚙️ Automation & Templating

* **Ground-Truth Templates** : Save frequently used metadata structures as reusable blueprints.
* **Batch Operations** : Use templates to perform massive additions to the dictionary, streamlining the documentation of large-scale schemas.

### 📤 Multi-Format Exports

Generate production-ready artifacts in one click:

* **Standard Formats** : Excel, CSV, JSON, and YAML.
* **Database Ready** : Automatic generation of **SQL DDL scripts** for instant schema deployment.

## 🎬 How to use the App

To see the app in action and learn how to perform specific tasks (like creating a template or running a batch update), please **check the `demos/` folder** in this repository.

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.

**Author:** Ender De Freitas

**Portfolio:** https://github.com/endpsych
