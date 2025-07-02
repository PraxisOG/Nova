import importlib
import os

def load_tools_with_metadata():
    tools = []
    folder = "tools"
    tool_modules = [
        f[:-3] for f in os.listdir(folder)
        if f.endswith(".py") and not f.startswith("__") and f not in {"registry.py", "decorators.py"}
    ]

    for mod_name in tool_modules:
        module = importlib.import_module(f"tools.{mod_name}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and hasattr(attr, "_tool_metadata"):
                tools.append(attr._tool_metadata)

    return tools
