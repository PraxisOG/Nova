import sys
import os
sys.path.insert(0, os.path.abspath("."))
import tkinter as tk
from tkinter import scrolledtext

# LMStudio SDK
import lmstudio as lms

# This loads the tools
from tools.registry import load_tools_with_metadata


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LM Studio Chat Interface")

        # Initialize model and chat
        self.model_a = lms.llm("qwen3-32b")
        self.chat_a = lms.Chat()

        # GUI Elements
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=10, pady=5)

        self.input_box = tk.Entry(self.input_frame, width=60)
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_box.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Output area
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, state='disabled')
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Load and display tools
        self.tools_metadata = load_tools_with_metadata()
        self.display_tools()

    def send_message(self, event=None):
        user_input = self.input_box.get().strip()
        if not user_input:
            return

        # Display user message in output area
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, f"User: {user_input}\n")
        self.output_area.config(state='disabled')
        self.input_box.delete(0, tk.END)

        # Add to chat history
        self.chat_a.add_user_message(user_input)

        # Prepare tools for processing
        tools = [tool["function"] for tool in self.tools_metadata]

        # Process the message using model and display results
        self.model_a.act(
            self.chat_a,
            tools,
            on_message=self.on_model_message
        )

    def on_model_message(self, fragment):
        """Callback function to handle streaming responses from the model."""
        content = fragment.content if hasattr(fragment, 'content') else str(fragment)
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, f"Model: {content}\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def display_tools(self):
        """Display the list of available tools in the output area."""
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, "Loaded Tools:\n")
        for tool in self.tools_metadata:
            name = tool.get("name", "Unknown Tool")
            description = tool.get("description", "No description.")
            self.output_area.insert(tk.END, f" - {name}: {description}\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()