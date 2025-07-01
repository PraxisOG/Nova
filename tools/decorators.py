# tools/decorators.py

def tool(name=None, description=None):
    def wrapper(func):
        func._tool_metadata = {
            "name": name or func.__name__,
            "description": description or func.__doc__ or "",
            "function": func,
        }
        return func
    return wrapper
