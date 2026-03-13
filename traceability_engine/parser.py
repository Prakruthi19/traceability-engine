import ast
import sys
import hashlib

def get_logic_hash(node):
    """
    Creates a MD5 hash of the function's structural logic.
    Using ast.unparse(node) ensures comments and whitespace don't affect the hash.
    """
    # Convert the AST node back to a standardized string (removes comments/formatting)
    logic_string = ast.unparse(node)
    return hashlib.md5(logic_string.encode('utf-8')).hexdigest()

def extract_functions_with_hashes(code):
    """Parses code and returns a dictionary of {name: {'source': src, 'hash': h}}."""
    if not code:
        return {}
    try:
        code = code.replace('\r\n', '\n')
        tree = ast.parse(code)
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                source = ast.unparse(node) # Use unparse for consistent 'clean' source
                f_hash = get_logic_hash(node)
                
                functions[node.name] = {
                    "source": source,
                    "hash": f_hash
                }
        return functions
    except Exception as e:
        if code.strip():
            print(f"AST Parse Error: {e}", file=sys.stderr)
        return {}

def compare_logic(old_code, new_code):
    """Optimized comparison using AST hashing."""
    # 1. Extract functions and their logic hashes
    old_funcs = extract_functions_with_hashes(old_code)
    new_funcs = extract_functions_with_hashes(new_code)
    
    changes = []
    
    # 2. Iterate through new functions (O(N) lookup)
    for name, new_data in new_funcs.items():
        # Case A: Brand New Function
        if name not in old_funcs:
            changes.append({
                "name": name, 
                "code": new_data["source"], 
                "old_code": ""
            })
        # Case B: Modified Logic (Compare Hashes, not strings!)
        elif old_funcs[name]["hash"] != new_data["hash"]:
            changes.append({
                "name": name, 
                "code": new_data["source"], 
                "old_code": old_funcs[name]["source"]
            })
            
    return changes