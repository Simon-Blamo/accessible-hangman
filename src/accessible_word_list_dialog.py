from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class AccessibleWordListDialog(QDialog):
    def __init__(self, parent, theme, font_family, font_size):
        super().__init__(parent)
        self.setWindowTitle("Manage Word Lists")
        self.theme = theme
        self.font = QFont(font_family, font_size)
        self.setup_ui()
        self.apply_theme(theme)
        self.setModal(True)
        self.resize(400, 500)  # Set a reasonable default size

    def setup_ui(self):
        layout = QVBoxLayout()

        # Instructions label
        instructions = QLabel("Add custom words to use in the game.\nWords will be automatically graded by complexity.")
        instructions.setFont(self.font)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)

        # Word list with grade level indicators
        self.list_widget = QListWidget()
        self.list_widget.setFont(self.font)
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)

        # Input area
        input_layout = QHBoxLayout()
        
        # Word input
        self.word_input = QLineEdit()
        self.word_input.setFont(self.font)
        self.word_input.setPlaceholderText("Enter a word")
        reg_ex = QRegularExpression("[A-Za-z]+")
        validator = QRegularExpressionValidator(reg_ex)
        self.word_input.setValidator(validator)
        
        # Grade level selection
        self.grade_label = QLabel("Grade Level:")
        self.grade_label.setFont(self.font)
        self.grade_combo = QComboBox()
        self.grade_combo.setFont(self.font)
        self.grade_combo.addItems(['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        
        input_layout.addWidget(self.word_input, 2)  # Give more space to word input
        input_layout.addWidget(self.grade_label, 1)
        input_layout.addWidget(self.grade_combo, 1)
        layout.addLayout(input_layout)

        # Button area
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Word")
        self.add_button.setFont(self.font)
        self.add_button.setDefault(True)  # Make this the default button when Enter is pressed
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setFont(self.font)
        
        self.close_button = QPushButton("Close")
        self.close_button.setFont(self.font)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)

        # Connect Enter key in word_input to add_button
        self.word_input.returnPressed.connect(self.add_button.click)
        
        self.setLayout(layout)

    def apply_theme(self, theme):
        # Apply theme to dialog and all its widgets
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QListWidget {{
                background-color: {theme['listbox']};
                color: {theme['listbox_text']};
                border: 1px solid {theme['listbox_text']};
                border-radius: 4px;
                padding: 5px;
            }}
            QListWidget::item:alternate {{
                background-color: {theme['background']};
            }}
            QLineEdit {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid {theme['text']};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox {{
                background-color: {theme['dropdown']};
                color: {theme['dropdown_text']};
                border: 1px solid {theme['dropdown_text']};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {theme['button']};
                color: {theme['button_text']};
                border: 1px solid {theme['button_text']};
                border-radius: 7px;
                padding: 8px 15px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_text']};
                color: {theme['button']};
            }}
            QLabel {{
                color: {theme['text']};
                padding: 5px;
            }}
        """)

    def keyPressEvent(self, event):
        # Handle Escape key to close dialog
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)