from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from layout_colorwidget import Color
from hangman import Hangman
import sys

# Set up ending screen

class EndScreen(QWwidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("This is Screen 1")
        button = QPushButton("Go to Screen 2")
        button.clicked.connect(self.go_to_screen_2)
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)
    
    def go_to_main(self):
        self.parent().setCurrentIndex(1)  # Switch to Main Screen

class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("This is Screen 2")
        button = QPushButton("Go to Screen 1")
        button.clicked.connect(self.go_to_screen_1)
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)

    def go_to_end(self):
        self.parent().setCurrentIndex(0)  # Switch to End Screen
    
# Set up main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman")    
        
        # Create stacked widget to switch between screens
        self.stack_widget = QStackedWidget()

        # Create screens
        self.main_screen = MainScreen()
        self.end_screen = EndScreen()

        # Add Screens to stacked layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        
        set.setLayout(main_layout)

    ### END OF METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()