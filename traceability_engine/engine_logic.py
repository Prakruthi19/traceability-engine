import git
import os
import sys
from .parser import compare_logic
from .translator import translate_to_methods

def run_engine():
    """
    Main orchestrator for the traceability engine.
    Analyzes Git diffs, detects logic changes, and prompts for AI documentation.
    """
    print("\n[Traceability Engine] Initializing analysis...", file=sys.stderr)
    try:
        # 1. Initialize the Repo
        repo = git.Repo(search_parent_directories=True)
        if repo.bare:
            print("Error: Bare repository detected.", file=sys.stderr)
            return

        # 2. Get the Diffs (R=True is vital for showing new functions correctly)
        try:
            diffs = repo.index.diff("HEAD", R=True)
        except Exception:
            # Fallback for the absolute first commit (no HEAD exists)
            diffs = repo.index.diff(None, staged=True)

        if not diffs:
            print("No staged changes found in Python files.", file=sys.stderr)
            return

        # 3. Process the changes
        for d in diffs:
            file_path = d.a_path
            
            # Only process Python files
            if file_path.endswith(".py"):
                
                # Get Old Content (from the last commit/HEAD)
                old_content = ""
                if d.a_blob:
                    old_content = d.a_blob.data_stream.read().decode("utf-8")

                # Get New Content (current file on your disk)
                full_path = os.path.join(repo.working_dir, file_path)
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        new_content = f.read()
                        print(f"DEBUG: Analyzing {file_path}...", file=sys.stderr)
                else:
                    new_content = ""

                # 4. Compare using AST parser
                changed_functions = compare_logic(old_content, new_content)
                
                if not changed_functions:
                    continue

                print(f"\n[LOGIC CHANGE] Found {len(changed_functions)} updates in {file_path}", file=sys.stderr)
                
                # 5. Document and Prompt loop
                for func_data in changed_functions:
                    name = func_data['name']
                    code = func_data['code']
                    
                    # Call Llama via the translator
                    suggestion = translate_to_methods(name, code)
                    
                    print(f"\nProposed for '{name}':", file=sys.stderr)
                    print(f"> {suggestion}", file=sys.stderr)
                    
                    # User-in-the-Loop: Get input from the console directly
                    print("Accept [y], Edit [e], or Skip [s]? ", end='', file=sys.stderr, flush=True)
                    with open('CON', 'r') as console:
                        choice = console.readline().strip().lower()
                    
                    final_description = suggestion
                    if choice == 'e':
                        print("Enter your version: ", end='', file=sys.stderr, flush=True)
                        with open('CON', 'r') as console:
                            final_description = console.readline().strip()
                    elif choice == 's':
                        print(f"Skipping {name}...", file=sys.stderr)
                        continue

                    # Write to METHODS.md
                    with open("METHODS.md", "a", encoding="utf-8") as f:
                        # Log the file header if it's the first function for this file
                        f.write(f"\n## File: {file_path}\n")
                        f.write(f"* **{name}**: {final_description}\n")
                            
                    print(f"Documented: {name}")

        print("\nTraceability engine run complete.")

    except Exception as e:
        print(f"Traceability Engine Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_engine()