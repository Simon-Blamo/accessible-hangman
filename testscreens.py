import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QPushButton, QLabel

class Screen1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("This is Screen 1")
        button = QPushButton("Go to Screen 2")
        button.clicked.connect(self.go_to_screen_2)
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)
    
    def go_to_screen_2(self):
        self.parent().setCurrentIndex(1)  # Switch to Screen 2

class Screen2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("This is Screen 2")
        button = QPushButton("Go to Screen 1")
        button.clicked.connect(self.go_to_screen_1)
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)

    def go_to_screen_1(self):
        self.parent().setCurrentIndex(0)  # Switch to Screen 1

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Switcher Example")
        self.setGeometry(100, 100, 400, 300)

        # Create stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()

        # Create the individual screens
        self.screen1 = Screen1()
        self.screen2 = Screen2()

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.screen1)
        self.stacked_widget.addWidget(self.screen2)

        # Set the initial screen
        self.stacked_widget.setCurrentIndex(0)  # Start on Screen 1

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
