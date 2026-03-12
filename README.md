# 📚 AI Traceability Engine: Master Implementation Guide

This document contains the complete technical specifications, source code, and deployment steps for the **AI Traceability Engine**.

---

## 📂 1. Project Directory Structure
Ensure your folder is organized exactly as follows for the package installation to work:

```text
traceability-engine/
├── .gitignore               # CRITICAL: Exclude .env and build artifacts
├── pyproject.toml           # Package configuration & CLI entry points
├── README.md                # Project overview for GitHub
├── .env                     # Local secrets (API Keys)
└── traceability_engine/     # Source code package
    ├── __init__.py          # Identifies folder as a Python package
    ├── main.py              # CLI entry point & toggle logic
    ├── engine_logic.py      # Git orchestration & user loop
    ├── parser.py            # AST logic for logic-only diffs
    └── translator.py        # Llama 3.3 70B API integration
```
## Installation & Setup Guide
Step 1: Local Installation
Run this in the root folder to register the trace-gen command:
```bash
pip install -e .
```
## Step 2: Configure Environment
Create a .env file (this will be ignored by Git):
```bash
HUGGINGFACE_API_KEY=your_hf_token_here
TRACE_GEN_ENABLED=true
```
## Step 3: Activate Git Hook
Create a file at .git/hooks/pre-commit and paste:
```bash
#!/bin/sh
trace-gen run
```
