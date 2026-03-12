import difflib

import git
import os
import sys
from .parser import compare_logic
from .translator import translate_to_methods
from concurrent.futures import ThreadPoolExecutor
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
        tasks = []
        for d in diffs:
            file_path = d.a_path
            if file_path.endswith(".py"):
                old_content = d.a_blob.data_stream.read().decode("utf-8") if d.a_blob else ""
                full_path = os.path.join(repo.working_dir, file_path)
                
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        new_content = f.read()
                    
                    # Store function data + file path for the audit trail
                    for func in compare_logic(old_content, new_content):
                        func['path'] = file_path
                        tasks.append(func)
        
        # 4. PARALLEL AI GENERATION
        # We start the AI thinking for ALL functions at once to save time
        print(f"Analyzing {len(tasks)} functions in parallel...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Create futures for all tasks
            futures = [executor.submit(translate_to_methods, f['name'], f['code']) for f in tasks]
            results = [f.result() for f in futures]
        # 5. SMART INTERACTIVE REVIEW
        # If there are many changes, warn the user
        print(f"\n\033[1m Change Summary ({len(tasks)} functions across {len(set(f['path'] for f in tasks))} files):\033[0m", file=sys.stderr)
        for i, func in enumerate(tasks):
            print(f"{i+1}. {func['name']} in {func['path']}", file=sys.stderr)
        show_diffs = True
        if len(tasks) > 5:
            print(f"\nLarge commit detected. Show detailed diffs for all {len(tasks)} functions? [y/n]: ", end='', file=sys.stderr, flush=True)
            with open('CON', 'r') as console:
                show_full_diff = (console.readline().strip().lower() == 'y')
        for i, func in enumerate(tasks):
            suggestion = results[i]
            print(f"\n\033[1;36m[{i+1}/{len(tasks)}] REVIEWING: {func['name']}\033[0m", file=sys.stderr)

            if show_full_diff:
                # Optimized Diff (limit to 10 lines of context)
                diff = list(difflib.unified_diff(
                    func['old_code'].splitlines(), 
                    func['code'].splitlines(), 
                    n=2, linterm='' # n=2 keeps the diff compact
                ))
                for line in diff[2:]: # Skip the header lines
                    if line.startswith('+'): print(f"\033[92m{line}\033[0m", file=sys.stderr)
                    elif line.startswith('-'): print(f"\033[91m{line}\033[0m", file=sys.stderr)

            print(f"\033[93mProposed Doc:\033[0m {suggestion}", file=sys.stderr)
            print("Accept [y], Edit [e], or Skip [s]? ", end='', file=sys.stderr, flush=True)
            
            with open('CON', 'r') as console:
                choice = console.readline().strip().lower()
            
            if choice == 'e':
                print("Enter version: ", end='', file=sys.stderr, flush=True)
                with open('CON', 'r') as console: suggestion = console.readline().strip()
            elif choice == 's':
                continue

            # 6. Write to METHODS.md (with file headers)
            with open("METHODS.md", "a", encoding="utf-8") as f:
                # Add a file header if it's the first function in a new file chunk
                if i == 0 or tasks[i]['path'] != tasks[i-1]['path']:
                    f.write(f"\n### File: {func['path']}\n")
                f.write(f"* **{func['name']}**: {suggestion}\n")

        
        print("\n Traceability engine run complete.")

        if not tasks:
            print("No logical changes detected in Python files.", file=sys.stderr)
            return
                    

    except Exception as e:
        print(f"Traceability Engine Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_engine()