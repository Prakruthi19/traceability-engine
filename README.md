# 🚀 AI Traceability Engine

An automated, AI-powered documentation tool that lives in your Git workflow. It identifies functional logic changes using **AST (Abstract Syntax Tree)** parsing and generates formal method descriptions using **Llama 3.3 70B**.



## ✨ Key Features
* **AST-Based Detection:** Unlike standard diff tools that trigger on every line change, this engine parses Python code to detect actual logic modifications, ignoring simple formatting or whitespace changes.
* **High-Fidelity AI Documentation:** Leverages **Llama 3.3 70B** via the Hugging Face Router for near-instant, academic-grade method descriptions.
* **Human-in-the-Loop:** Interactive CLI allows you to **Accept**, **Edit**, or **Skip** suggestions before they are written to disk.
* **Automatic Segregation:** Organizes your documentation by file within `METHODS.md` to ensure a clean, navigable audit trail.

---

## 🛠️ Installation

### 1. Install Globally (Local Development)
Clone the repository and install it in editable mode:
```powershell
git clone [https://github.com/your-username/traceability-engine.git](https://github.com/your-username/traceability-engine.git)
cd traceability-engine
pip install -e .