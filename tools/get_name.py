from tools.decorators import tool
import os
import subprocess

@tool(name="get_name", description="Returns the name of the assistant.")

def get_name() -> str:
    """Returns the name of the assistant."""
    return "Nova"