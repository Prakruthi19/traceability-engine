import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the current working directory (where the user runs trace-gen)
load_dotenv(Path.cwd() / ".env")

def get_client():
    """Helper to initialize the OpenAI client with the HF Router."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None
    
    return OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=api_key,
    )

def check_llama_connection():
    """Diagnostic function for the 'trace-gen check' command."""
    client = get_client()
    if not client:
        return False, "HUGGINGFACE_API_KEY not found in environment or .env file."
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct:groq",
            messages=[{"role": "user", "content": "Respond with 'READY'"}],
            max_tokens=5,
            timeout=10
        )
        return True, completion.choices[0].message.content.strip()
    except Exception as e:
        return False, str(e)

def translate_to_methods(func_name, code_snippet):
    """
    Translates Python logic into a formal one-sentence documentation string.
    """
    client = get_client()
    if not client:
        return "Error: HUGGINGFACE_API_KEY not set."


    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct:groq",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a technical writer. Write a ONE-SENTENCE formal method description "
                        "for the provided code. Use an objective, academic tone. "
                        "Focus on the mathematical or structural intent."
                    )
                },
                {
                    "role": "user", 
                    "content": f"Function Name: {func_name}\nCode Snippet:\n{code_snippet}"
                }
            ],
            max_tokens=80,
            temperature=0.1
        )
        
        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"DEBUG API ERROR: {e}", file=sys.stderr)
        return f"Structural modification to the {func_name} routine."

if __name__ == "__main__":
    # Local test execution
    test_res = translate_to_methods("new_sum", "def new_sum(a, b): return a + b")
    print(f"\nResult: {test_res}")