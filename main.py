import sys
import threading
import time  # Added missing import
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QListWidget,
    QRadioButton, QHBoxLayout, QLabel, QCheckBox, QFileDialog,
    QTabWidget, QPlainTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot  # Added pyqtSlot
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat  # <<-- Added for coloring


# Your existing imports (lmstudio, tools, etc.)
import os
sys.path.insert(0, os.path.abspath("."))
import lmstudio as lms
from tools.registry import load_tools_with_metadata


class ChatWorker(QObject):
    fragment_signal = pyqtSignal(str)
    tool_list_signal = pyqtSignal(list)

    def __init__(self, chat_a, model_a, speed_mode):
        super().__init__()
        self.chat_a = chat_a  # lms.Chat instance for conversation history
        self.model_a = model_a  # already set based on user preference (speed mode)
        self.speed_mode = speed_mode

    @pyqtSlot(str)
    def process_message(self, user_msg):
        try:
            # Add to chat history in the LLM context
            self.chat_a.add_user_message("User: " + user_msg)

            # Load available tools and update UI list before processing
            tools_metadata = load_tools_with_metadata()
            self.tool_list_signal.emit(tools_metadata)
            tools = [tool["function"] for tool in tools_metadata]

            full_response = []

            def print_fragment(fragment, round_index):
                content = fragment.content  # Assuming the model returns a 'content' attribute
                full_response.append(content)
                self.fragment_signal.emit(content)

            # Use the correct model (already passed via __init__)
            self.model_a.act(
                chat=self.chat_a,
                tools=tools,
                on_prediction_fragment=print_fragment
            )

            # Load available tools again and update UI list after processing
            tools_metadata = load_tools_with_metadata()
            self.tool_list_signal.emit(tools_metadata)

            # Add assistant's full response to the LLM context for future reference
            if full_response:
                full_response_text = ''.join(full_response)
                self.chat_a.add_assistant_response(full_response_text)

        except Exception as e:
            error_msg = f"<b>Error:</b> {str(e)}"
            self.fragment_signal.emit(error_msg)


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

        # New: Code editor and output window
        self.code_editor = QPlainTextEdit()
        self.output_window = QTextEdit()
        self.output_window.setReadOnly(True)

        # Model & Chat setup
        self.chat_a = lms.Chat()
        self.model_a = lms.llm("qwen3-32b")
        
        # Load initial instructions
        instruction_file = "context/Scriptwriting_inst.txt"
        try:
            with open(instruction_file, 'r', encoding='utf-8') as f:
                instructions = f.read()
        except Exception as e:
            instructions = f"Error loading instructions: {str(e)}"
        self.chat_a.add_user_message(instructions)

        # UI setup
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Tabs for Chat and Code Editor
        tab_widget = QTabWidget()

        # Chat Tab
        chat_container = QWidget()
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(QLabel("Chat History"))
        chat_layout.addWidget(self.chat_history)
        chat_container.setLayout(chat_layout)

        # Input Controls (inside Chat Tab)
        input_layout = QHBoxLayout()
        self.input_field.returnPressed.connect(self.handle_send)  # Enter key sends
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.handle_send)

        chat_layout.addLayout(input_layout)
        
        tab_widget.addTab(chat_container, " Chat ")

        # Code Editor Tab
        code_tab = QWidget()
        code_layout = QVBoxLayout()
        code_layout.addWidget(QLabel("Code Editor"))
        code_layout.addWidget(self.code_editor)
        run_button = QPushButton("Run Code")
        run_button.clicked.connect(self.execute_code)
        code_layout.addWidget(run_button)

        output_label = QLabel("Output:")
        code_layout.addWidget(output_label)
        code_layout.addWidget(self.output_window)
        
        code_tab.setLayout(code_layout)
        tab_widget.addTab(code_tab, " Code ")

        # Bottom UI Buttons
        self.speed_mode_checkbox = QCheckBox("Speed Mode - Qwen A3B")
        save_button = QPushButton("Save Chat")
        load_button = QPushButton("Load Chat")
        summarize_button = QPushButton("Summarize Chat")

        # Create a QHBoxLayout to hold Speed Mode checkbox and Dark Mode button side-by-side
        bottom_controls_layout = QHBoxLayout()
        
        dark_mode_button = QCheckBox("Dark Mode")
        dark_mode_button.setCheckable(True)  # Makes it toggle-able (on/off)
        dark_mode_button.clicked.connect(self.toggle_dark_mode)

        bottom_controls_layout.addWidget(self.speed_mode_checkbox)
        bottom_controls_layout.addWidget(dark_mode_button)

        main_layout.addWidget(tab_widget)
        main_layout.addLayout(bottom_controls_layout)  # Add the QHBoxLayout with both widgets
        main_layout.addWidget(save_button)
        main_layout.addWidget(load_button)
        main_layout.addWidget(summarize_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect signals
        save_button.clicked.connect(self.save_chat)
        load_button.clicked.connect(self.load_chat)
        summarize_button.clicked.connect(self.summarize_chat)

    def toggle_dark_mode(self):
        if self.sender().isChecked():
            # Apply global dark mode styles
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
                QTabWidget::pane {
                    border-top: 1px solid #444; /* Border under the tabs */
                }
                QTabBar::tab {
                    background-color: #3c3c3c;
                    color: white;
                    padding: 5px 10px;
                    margin-right: 2px;
                    border: 1px solid #444;
                    border-bottom: none; /* Remove bottom border */
                }
                QTabBar::tab:selected {
                    background-color: #2b2b2b;
                    font-weight: bold;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    border: 1px solid #555;
                }
            """)
        else:
            self.setStyleSheet("")

    def handle_send(self):
        user_msg = self.input_field.text().strip()
        if not user_msg:
            return
            
        self.input_field.clear()
        
        # Add to history
        self.chat_history.append(f"<b>User: </b> {user_msg}")
        
        # Start worker thread
        speed_mode = self.speed_mode_checkbox.isChecked()
        model_name = "qwen3-30b-a3b" if speed_mode else "qwen3-32b"
        
        self.worker_thread = ChatWorker(
            chat_a=self.chat_a,
            model_a=lms.llm(model_name),
            speed_mode=speed_mode
        )
        
        assistant_label = "<b>Nova: </b>"
        self.chat_history.append(assistant_label)
        
        self.worker_thread.fragment_signal.connect(self.update_chat)
        self.worker_thread.tool_list_signal.connect(self.update_tool_list)
        
        thread = threading.Thread(
            target=self.worker_thread.process_message, 
            args=(user_msg,),
            daemon=True
        )
        thread.start()

    def save_chat(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Chat", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.chat_history.toPlainText())
                QMessageBox.information(self, "Saved", "Chat saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save chat: {str(e)}")

    def load_chat(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Chat", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update LLM context
                self.chat_a.clear_history()  # Clear existing history
                
                # Parse and add messages correctly (basic implementation)
                for line in content.splitlines():
                    if line.startswith("User: "):
                        self.chat_a.add_user_message(line[6:])
                    elif line.startswith("Nova: "):
                        self.chat_a.add_assistant_response(line[6:])  # Assumes this method exists
                
                # Update UI
                self.chat_history.setPlainText(content)
                QMessageBox.information(self, "Loaded", "Chat loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load chat: {str(e)}")

    def summarize_chat(self):
        summary_worker = ChatWorker(
            chat_a=self.chat_a,
            model_a=lms.llm("qwen3-30b-a3b"),
            speed_mode=True
        )
        
        # Summary display in output window
        self.output_window.clear()
        self.output_window.append("<b>Summary:</b>")
        
        summary_worker.fragment_signal.connect(self.output_window.insertPlainText)
        thread = threading.Thread(
            target=summary_worker.process_message, 
            args=("Please summarize this conversation.",),
            daemon=True
        )
        thread.start()

    def execute_code(self):
        code = self.code_editor.toPlainText()
        if not code:
            return
            
        self.output_window.clear()
        
        try:
            # Use subprocess for safe execution with timeout
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=10  # Prevent infinite loops
            )
            
            output = f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
            self.output_window.setPlainText(output)
        except subprocess.CalledProcessError as e:
            self.output_window.setPlainText(f"Error: {e}")
        except Exception as e:
            self.output_window.setPlainText(f"Unexpected error: {str(e)}")

    def update_chat(self, text):
        self.chat_history.insertPlainText(text)
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    def update_tool_list(self, tools_metadata):
        tool_list = self.findChild(QListWidget)
        if not tool_list:
            return
            
        tool_list.clear()
        
        for tool in tools_metadata:
            item_text = f"{tool['name']} - {tool['description']}"
            tool_list.addItem(item_text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import subprocess  # Needed for code execution
    main()