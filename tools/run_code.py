from tools.decorators import tool
import subprocess

@tool(name="run_code", description="Executes given Python code and returns output/errors.")
def run_code(code: str) -> str:
    '''Takes a string with valid python code, and returns the output and any errors encountered'''
    if not code.strip():
        return "No code provided."

    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
        return output.strip() or "No output generated."
    except subprocess.CalledProcessError as e:
        return f"Execution error: {e}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"