from tools.decorators import tool
import os

# Determine the absolute path to this script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

@tool(name="read_py_files", description="Reads a specified .py file in the same directory as this script and returns its name and content.")
def read_py_files(filename: str) -> dict:
    """Returns dictionary of {filename: content} for the specified .py file."""
    
    # Ensure the filename has a .py extension
    if not filename.endswith('.py'):
        return {}
    
    # Construct full path to the target file
    full_path = os.path.join(script_dir, filename)
    
    # Check that it is a valid file and located directly in script's directory (no subdirectories)
    if not os.path.isfile(full_path) or os.path.dirname(full_path) != script_dir:
        return {}
    
    # Read the content of the specified .py file
    with open(full_path, 'r') as f:
        return {filename: f.read()}