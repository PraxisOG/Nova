from tools.decorators import tool
import os

@tool(name="list_tools_folder", description="List all files in the tools directory.")
def list_tools_folder() -> str:
    '''Returns a string listing all files in the tools directory.'''
    directory_path = "tools"
    if not os.path.exists(directory_path):
        return f"The directory {directory_path} does not exist."
    files = os.listdir(directory_path)
    return '\n'.join(files)