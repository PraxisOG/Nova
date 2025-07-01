# tools/hello.py
from tools.decorators import tool

@tool(name="hello_world", description="Print a friendly hello message.")
def hello_world() -> str:
    """Returns a 'Hello, world!' greeting."""
    return "Hello, world!"
