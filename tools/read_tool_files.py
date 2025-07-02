from tools.decorators import tool
import os

@tool(name="read_tool_files", description="List all files in the tools directory.")
def read_tool_files() -> str:
    '''Returns a list of all files in the tools directory.'''
    return '\n'.join(os.listdir('tools'))