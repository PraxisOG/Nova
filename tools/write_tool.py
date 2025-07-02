from tools.decorators import tool
import os

@tool(name="write_tool", description="Write a Python file with custom code to create a new tool.")
def write_tool(filename: str, code_content: str) -> str:
    """
    Writes provided code into a .py file in the 'tools' directory.

    Args:
        filename (str): Name of the output Python file.
        code_content (str): Code content to be written into the file.

    Returns:
        str: Success message with full path to created file.

    Here is an example of what a tool should look like:

    from tools.decorators import tool
    import os

    @tool(name="hello_world", description="Print a friendly hello message.")

    # Example code
    def hello_world() -> str:
    '''returns a hello world greeting'''
    return "Hello, world!"
    """
    
    # Ensure the target is a .py file
    if not filename.endswith(".py"):
        raise ValueError("Filename must end with '.py'")

    output_path = "tools"  # Relative path; adjust as needed for your project structure
    os.makedirs(output_path, exist_ok=True)  # Create directory if it doesn't exist

    full_file_path = os.path.join(output_path, filename)

    with open(full_file_path, 'w') as f:
        f.write(code_content)

    return f"Successfully created tool at {full_file_path}"