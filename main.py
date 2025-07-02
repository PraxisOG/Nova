import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QListWidget,
    QRadioButton, QHBoxLayout, QLabel, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

# Your existing code imports would go here
import os
sys.path.insert(0, os.path.abspath("."))
import lmstudio as lms
from tools.registry import load_tools_with_metadata

def load_txt(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

class ChatWorker(QObject):
    fragment_signal = pyqtSignal(str)
    tool_list_signal = pyqtSignal(list)

    def __init__(self, chat_a, model_a, speed_mode):
        super().__init__()
        self.chat_a = chat_a
        self.model_a = model_a
        self.speed_mode = speed_mode

    def process_message(self, user_msg):
        # Add to chat history
        self.chat_a.add_user_message(user_msg)

        # Load tools and update UI
        tools_metadata = load_tools_with_metadata()
        self.tool_list_signal.emit(tools_metadata)

        # Process model response
        tools = [tool["function"] for tool in tools_metadata]

        # Allows streaming from .act
        def print_fragment(fragment, round_index):
            self.fragment_signal.emit(fragment.content)

        # Changes between slower and faster models
        if self.speed_mode:
            tempmodel = "qwen3-4b"
        else:
            tempmodel = "qwen3-32b"

        # Bot response
        model_a = lms.llm(tempmodel)
        model_a.act(
            self.chat_a,
            tools,
            on_prediction_fragment=print_fragment
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nova Chat Interface")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize chat components
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_send)
        
        # Model selection controls
        self.speed_mode_checkbox = QCheckBox("Speed Mode (Qwen MOE)")
        self.speed_mode_checkbox.setChecked(True)
        
        self.chat_a = lms.Chat()
        self.model_a = lms.llm("qwen3-4b")

        # Setup Instructions for Scriptwriting
        instruction_file = "context/Scriptwriting_inst.txt"
        try:
            instructions = load_txt(instruction_file)
        except Exception as e:
            instructions = f"Error loading instructions: {str(e)}"

        self.chat_a.add_user_message(instructions)

        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Chat display area
        chat_container = QWidget()
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(QLabel("Chat History"))
        chat_layout.addWidget(self.chat_history)
        chat_container.setLayout(chat_layout)
        
        # Input controls
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        # Tool list area
        tool_list_widget = QListWidget()
        
        main_layout.addWidget(chat_container)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.speed_mode_checkbox)
        main_layout.addWidget(tool_list_widget)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Connect signals
        self.worker_thread = None
        
    def handle_send(self):
        user_msg = self.input_field.text()
        if not user_msg:
            return
            
        self.input_field.clear()
        
        # Add user message to history
        self.chat_history.append(f"<b>You: </b> {user_msg}")
        
        # Create and start worker thread
        self.worker_thread = ChatWorker(
            chat_a=self.chat_a,
            model_a=self.model_a,
            speed_mode=self.speed_mode_checkbox.isChecked()
        )
        
        assistant_name = "<b>Nova: </b>"
        self.chat_history.append(assistant_name)
        self.worker_thread.fragment_signal.connect(self.update_chat)
        self.worker_thread.tool_list_signal.connect(self.update_tool_list)
        
        thread = threading.Thread(
            target=self.worker_thread.process_message, 
            args=(user_msg,),
            daemon=True
        )
        thread.start()
    
    def update_chat(self, text):
        self.chat_history.insertPlainText(text)
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )
        
    def update_tool_list(self, tools_metadata):
        tool_list_widget = self.findChild(QListWidget)
        tool_list_widget.clear()
        
        for tool in tools_metadata:
            item_text = f"{tool['name']} - {tool['description']}"
            tool_list_widget.addItem(item_text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    print("Program ended")


if __name__ == "__main__":
    main()