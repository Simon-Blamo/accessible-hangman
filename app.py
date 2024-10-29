from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from layout_colorwidget import Color
from hangman import *
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman")
        keyboard_row_1_chars = 'qwertyuiop'
        keyboard_row_2_chars = 'asdfghjkl'
        keyboard_row_3_chars = 'zxcvbnm'
        

        pagelayout = QVBoxLayout()
        button_layout = QHBoxLayout()
        image_layout = QHBoxLayout()
        input_layout = QHBoxLayout()
        keyboard_layout = QVBoxLayout()
        keyboard_container_layout = QVBoxLayout()
        keyboard_row_1_layout = QHBoxLayout()
        keyboard_row_2_layout = QHBoxLayout()
        keyboard_row_3_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(image_layout)
        pagelayout.addLayout(input_layout)
        pagelayout.addLayout(keyboard_container_layout)
        pagelayout.addLayout(self.stacklayout)

        label = QLabel(self)
        pixmap = QPixmap('./assests/stick.png').scaled(128, 192)
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        image_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        edit = QLineEdit()
        input_layout.addWidget(edit)

        for char in keyboard_row_1_chars:
            btn = QPushButton(char.upper())
            keyboard_row_1_layout.addWidget(btn)
        
        for char in keyboard_row_2_chars:
            btn = QPushButton(char.upper())
            keyboard_row_2_layout.addWidget(btn)

        for char in keyboard_row_3_chars:
            btn = QPushButton(char.upper())
            keyboard_row_3_layout.addWidget(btn)

        keyboard_layout.addLayout(keyboard_row_1_layout)
        keyboard_layout.addLayout(keyboard_row_2_layout)
        keyboard_layout.addLayout(keyboard_row_3_layout)
        keyboard_widget = QWidget()
        keyboard_widget.setLayout(keyboard_layout)
        keyboard_widget.setFixedWidth(400)
        keyboard_container_layout.addWidget(keyboard_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        ## Code that will be used a reference to achieve a future goal.
        btn = QPushButton("Easy")
        # btn.pressed.connect(self.activate_tab_1)
        button_layout.addWidget(btn)
        # self.stacklayout.addWidget(Color("red"))

        btn = QPushButton("Medium")
        # btn.pressed.connect(self.activate_tab_2)
        button_layout.addWidget(btn)
        # self.stacklayout.addWidget(Color("green"))

        btn = QPushButton("Hard")
        # btn.pressed.connect(self.activate_tab_3)
        button_layout.addWidget(btn)
        # self.stacklayout.addWidget(Color("yellow"))

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def activate_tab_1(self):
        self.stacklayout.setCurrentIndex(0)

    def activate_tab_2(self):
        self.stacklayout.setCurrentIndex(1)

    def activate_tab_3(self):
        self.stacklayout.setCurrentIndex(2)
       
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()