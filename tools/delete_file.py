from tools.decorators import tool
import os

@tool(name="delete_file", description="Delete a file from the tools directory (excluding protected files).")
def delete_file(filename: str) -> str:
    '''Deletes a file from the tools directory, excluding protected files.

    Args:
        filename (str): Name of the file to delete.

    Returns:
        str: Success or error message.
    '''
    tools_dir = "tools"
    protected_files = {"decorators.py", "registry.py", "write_tool.py", "list_tools_folder.py", "__init__.py","delete_file.py", "__pycache__"}

    if filename in protected_files:
        return f'Error: "{filename}" is a protected file and cannot be deleted.'

    file_path = os.path.join(tools_dir, filename)
    if not os.path.isfile(file_path):
        return f'Error: File "{filename}" does not exist in the tools directory.'

    try:
        os.remove(file_path)
        return f'Successfully deleted "{filename}" from the tools directory.'
    except Exception as e:
        return f'Error deleting "{filename}": {str(e)}'