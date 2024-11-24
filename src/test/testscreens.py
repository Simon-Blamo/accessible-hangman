from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from layout_colorwidget import Color
from hangman import Hangman
import sys

# Switch to Main Screen
class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Hangman!")
        button = QPushButton("End Screen")
        button.clicked.connect(self.go_to_end)
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)

    def go_to_end(self):
        self.parent().setCurrentIndex(1)  # Switch to End Screen
    
# Set up ending screen
class EndScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("End Screen!")
        button = QPushButton("Play Again")
        button.clicked.connect(self.go_to_main)
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)
    
    def go_to_main(self):
        self.parent().setCurrentIndex(0)  # Switch to Main Screen

# Set up main window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman")    
        
        # Create stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()

        # Create screens
        self.main_screen = MainScreen()
        self.end_screen = EndScreen()

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.end_screen)

        # Set the initial screen
        self.stacked_widget.setCurrentIndex(0)  # Start on Screen 1

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

    ### END OF METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()