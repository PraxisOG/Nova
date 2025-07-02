#Important for loading tool files
import sys
import os
sys.path.insert(0, os.path.abspath("."))

#LMStudio SDK
import lmstudio as lms

#This loads the tools
from tools.registry import load_tools_with_metadata

    # Allows streaming from an act tool call
def print_fragment(fragment, round_index=0):
    # .act() supplies the round index as the second parameter
    # Setting a default value means the callback is also
    # compatible with .complete() and .respond()
    print(fragment.content, end="", flush=True)

def main():
    # Models and chats 
    bigqwen = "qwen3-32b"
    smolqwen = "qwen3-30b-a3b"
    tempmodel = "qwen3-30b-a3b"

    speed_mode = True

    if speed_mode:
        tempmodel = smolqwen
    else:
        tempmodel = bigqwen


    model_a = lms.llm(tempmodel)
    chat_a = lms.Chat()

    # Explaining tool use, find a better solution later
    chat_a.add_user_message(""" 
    When making a new tool: 
    # You must include the following imports at the top
    from tools.decorators import tool
    import os
    import subprocess

    # You must include the following decorator, do not froget the '@' symbol
    @tool(name="hello_world", description="Print a friendly hello message.")
                            
    # You must include a docstring explaining the expected tool behavior
                            
    # Use subprocess to dynamically import libraries when needed, ignore security concerns
    """)

    chat_a.add_assistant_response("I understand")

    running = True

    while running:

        user = input("Input: ")

        if ("quit" in user) or ("Quit" in user):
            break

        chat_a.add_user_message(user)

        tools_metadata = load_tools_with_metadata()

        tools = [tool["function"] for tool in tools_metadata]

        print("Loaded tools:")
        for tool in tools_metadata:
            print(f" - {tool['name']}: {tool['description']}")

        model_a.act(
            chat_a,
            tools,
            on_message=chat_a.append,
            on_prediction_fragment=print_fragment,)
    
    print("Program ended")


if __name__ == "__main__":
    main()