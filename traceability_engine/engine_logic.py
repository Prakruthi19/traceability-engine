import difflib
import time

import git
import os
import sys
from .parser import compare_logic
from .translator import translate_to_methods
from concurrent.futures import ThreadPoolExecutor, as_completed
def run_engine():
    """
    Main orchestrator for the traceability engine.
    Analyzes Git diffs, detects logic changes, and prompts for AI documentation.
    """
    print("\n[Traceability Engine] Initializing analysis...", file=sys.stderr)
    start_time = time.time()
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
        
        print(f"Processing {len(tasks)} functions in parallel...", file=sys.stderr)
        results_map = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Map futures to their index so we keep them in order later
            future_to_index = {
                executor.submit(translate_to_methods, f['name'], f['code']): i 
                for i, f in enumerate(tasks)
            }
            
            completed = 0
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                results_map[index] = future.result()
                completed += 1
                # Simple progress bar update
                percent = int((completed / len(tasks)) * 100)
                sys.stderr.write(f"\rProgress: [{'#' * (percent // 10)}{'.' * (10 - (percent // 10))}] {percent}%")
                sys.stderr.flush()

        # Finalize the timer for the AI phase
        ai_duration = time.time() - start_time
        print(f"\nAI Generation completed in {ai_duration:.2f}s", file=sys.stderr)

        # --- REVIEW PHASE ---
        show_diffs = True
        if len(tasks) > 5:
            print(f"\n{len(tasks)} updates detected. Show diffs? [y/n]: ", end='', file=sys.stderr, flush=True)
            with open('CON', 'r') as console:
                show_diffs = (console.readline().strip().lower() == 'y')

        for i, func in enumerate(tasks):
            suggestion = results_map[i]
            print(f"\n\033[1;36m[{i+1}/{len(tasks)}] {func['name']}\033[0m", file=sys.stderr)

            if show_diffs:
                diff = list(difflib.unified_diff(
                    func.get('old_code', "").splitlines(), 
                    func['code'].splitlines(), 
                    n=1, lineterm=''
                ))
                for line in diff[2:]:
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

            with open("METHODS.md", "a", encoding="utf-8") as f:
                if i == 0 or tasks[i]['path'] != tasks[i-1]['path']:
                    f.write(f"\n### File: {func['path']}\n")
                f.write(f"* **{func['name']}**: {suggestion}\n")

        print(f"\n✅ Total run time: {time.time() - start_time:.2f}s")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)

    except Exception as e:
        print(f"Traceability Engine Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_engine()