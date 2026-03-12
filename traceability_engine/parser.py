import ast
import sys

def extract_functions(code):
    """Parses code and returns a dictionary of {name: source_code}."""
    if not code:
        return {}
    try:
        # Standardize line endings for AST stability
        code = code.replace('\r\n', '\n')
        tree = ast.parse(code)
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    source = ast.get_source_segment(code, node)
                    # Ensure we have a string even if segment returns None
                    functions[node.name] = source if source is not None else ast.unparse(node)
                except Exception:
                    functions[node.name] = ast.unparse(node)
        return functions
    except Exception as e:
        # Don't print error for empty/new files
        if code.strip():
            print(f"AST Parse Error: {e}", file=sys.stderr)
        return {}

def compare_logic(old_code, new_code):
    """Compares function logic between two versions of a file."""
    # Normalize outer whitespace and line endings
    old_code = old_code.replace('\r\n', '\n').strip()
    new_code = new_code.replace('\r\n', '\n').strip()
    
    old_funcs = extract_functions(old_code)
    new_funcs = extract_functions(new_code)
    
    changes = []
    for name, new_source in new_funcs.items():
        clean_new = new_source.strip()
        
        # Check for brand new functions
        if name not in old_funcs:
            changes.append({
                "name": name, 
                "code": clean_new, 
                "old_code": "" # Nothing to diff against
            })
        else:
            # Check for changes in existing functions
            clean_old = old_funcs[name].strip()
            
            # Logic check: simple string comparison of the stripped source
            if clean_old != clean_new:
                changes.append({
                    "name": name, 
                    "code": clean_new, 
                    "old_code": clean_old # Added for Diff support!
                })
            
    return changes