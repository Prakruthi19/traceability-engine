import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Import our logic modules using relative imports
from .translator import check_llama_connection
from .engine_logic import run_engine

# Load .env from the directory where the command is executed
load_dotenv(Path.cwd() / ".env")

def main():
    parser = argparse.ArgumentParser(
        prog="trace-gen", 
        description="Traceability Engine: AI-Powered Documentation"
    )
    parser.add_argument("--version", action="version", version="trace-gen 0.1.0")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Command: trace-gen run
    subparsers.add_parser("run", help="Analyze staged changes and update METHODS.md")
    
    # Command: trace-gen check
    subparsers.add_parser("check", help="Test Hugging Face API connectivity")

    args = parser.parse_args()

    if args.command == "check":
        print("🔍 Diagnostic: Testing API connection...", file=sys.stderr)
        success, message = check_llama_connection()
        if success:
            print(f"Success! Llama responded: {message}")
        else:
            print(f"Connection Failed: {message}")
            sys.exit(1)
    else:
        # Default behavior (if no command or 'run' is used)
        run_engine()

if __name__ == "__main__":
    main()