from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from layout_colorwidget import Color
from hangman import Hangman
import sys

# yollooooooooooooooooooooooooooooooooooooooooo

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman")
        self.hangman_game: Hangman = Hangman()
        self.easy_btn: QPushButton = None
        self.medium_btn: QPushButton = None
        self.hard_btn: QPushButton = None
        self.guess_text_box: QLineEdit = None
        self.keyboard_btns: List[List[QPushButton]] = None
        self.guess_btn: QPushButton = None
        self.game_progress_boxes: List[QLineEdit] = None
        

        page_layout = QVBoxLayout()
        difficulty_btn_layout = QHBoxLayout()
        self.game_progress_layout = QHBoxLayout()
        image_layout = QHBoxLayout()
        input_layout = QHBoxLayout()
        keyboard_container_layout = QVBoxLayout()

        keyboard_widget = None
        
        self.stacklayout = QStackedLayout()

        page_layout.addLayout(difficulty_btn_layout)
        page_layout.addLayout(image_layout)
        page_layout.addLayout(self.game_progress_layout)
        page_layout.addLayout(input_layout)
        page_layout.addLayout(keyboard_container_layout)
        page_layout.addLayout(self.stacklayout)

        self.init_difficulty_btns(difficulty_btn_layout)
        self.init_hangman_image(image_layout)

        self.guess_text_box = self.init_guess_text_box()
        input_layout.addWidget(self.guess_text_box)

        keyboard_widget, self.keyboard_btns = self.init_keyboard_widget()
        keyboard_container_layout.addWidget(keyboard_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        ## Code that will be used a reference to achieve a future goal.
        
        # self.stacklayout.addWidget(Color("yellow"))

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)
        self.set_tab_order()

    ### METHODS TO INITIALIZE ELEMENTS WITHIN APP WINDOW ###

    def init_difficulty_btns(self, difficulty_btn_layout):
        btn = QPushButton("Easy")
        btn.pressed.connect(lambda:self.start_game(0))
        self.easy_btn = btn
        difficulty_btn_layout.addWidget(btn)

        btn = QPushButton("Medium")
        btn.pressed.connect(lambda:self.start_game(1))
        self.medium_btn = btn
        difficulty_btn_layout.addWidget(btn)

        btn = QPushButton("Hard")
        btn.pressed.connect(lambda:self.start_game(2))
        self.hard_btn = btn
        difficulty_btn_layout.addWidget(btn)

    def init_hangman_image(self, image_layout):
        label = QLabel(self)
        pixmap = QPixmap('./assests/stick.png').scaled(128, 192)
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        image_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

    def init_guess_text_box(self):
        text_box = QLineEdit()
        text_box.setMaxLength(1)

        font_metrics = text_box.fontMetrics()
        width = font_metrics.horizontalAdvance('MM')

        reg_ex = QRegularExpression('[A-Za-z]{1}')
        validator = QRegularExpressionValidator(reg_ex)

        text_box.setValidator(validator)
        text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_box.setFixedWidth(width + 10)

        self.disable_textbox(text_box)
        return text_box
    
    def init_keyboard_widget(self):
        keyboard_layout = QVBoxLayout()
        keyboard_row_1_layout = QHBoxLayout()
        keyboard_row_2_layout = QHBoxLayout()
        keyboard_row_3_layout = QHBoxLayout()
        keyboard_row_4_layout = QHBoxLayout()
        keyboard_widget = QWidget()

        keyboard_row_1_chars = list('ABCDEFGHIJ')
        keyboard_row_2_chars = list('KLMNOPQRS')
        keyboard_row_3_chars = list('TUVWXYZ')
        keyboard_row_3_chars.append('\u232B') # erase to left unicode
        keyboard_row_4_word = 'GUESS'

        keyboard_row_1_btns = []
        keyboard_row_2_btns = []
        keyboard_row_3_btns = []
        keyboard_row_4_btns = []
        btns_array = []
        

        for char in keyboard_row_1_chars:
            btn = QPushButton(char)
            keyboard_row_1_btns.append(btn)
            btn.pressed.connect(lambda char=char:self.input_character_in_text_box(char, self.guess_text_box))
            keyboard_row_1_layout.addWidget(btn)
        
        for char in keyboard_row_2_chars:
            btn = QPushButton(char)
            keyboard_row_2_btns.append(btn)
            btn.pressed.connect(lambda char=char:self.input_character_in_text_box(char, self.guess_text_box))
            keyboard_row_2_layout.addWidget(btn)

        for char in keyboard_row_3_chars:
            btn = QPushButton(char)
            keyboard_row_3_btns.append(btn)
            btn.pressed.connect(lambda char=char:self.input_character_in_text_box(char, self.guess_text_box))
            keyboard_row_3_layout.addWidget(btn)

        btn = QPushButton(keyboard_row_4_word)
        btn.pressed.connect(lambda:self.process_guess(self.guess_text_box.text()))
        keyboard_row_4_btns.append(btn)
        keyboard_row_4_layout.addWidget(btn)
        self.guess_btn = btn

        btns_array.append(keyboard_row_1_btns)
        btns_array.append(keyboard_row_2_btns)
        btns_array.append(keyboard_row_3_btns)
        btns_array.append(keyboard_row_4_btns)

        self.disable_keyboard(btns_array)

        keyboard_layout.addLayout(keyboard_row_1_layout)
        keyboard_layout.addLayout(keyboard_row_2_layout)
        keyboard_layout.addLayout(keyboard_row_3_layout)
        keyboard_layout.addLayout(keyboard_row_4_layout)
        keyboard_widget.setLayout(keyboard_layout)
        keyboard_widget.setFixedWidth(400)

        return [keyboard_widget, btns_array]

    ### END OF METHODS TO INITIALIZE ELEMENTS WITHIN APP WINDOW ###
    def activate_tab_1(self):
        self.stacklayout.setCurrentIndex(0)

    def activate_tab_2(self):
        self.stacklayout.setCurrentIndex(1)

    def activate_tab_3(self):
        self.stacklayout.setCurrentIndex(2)
    
    ### HELPER METHODS FOR ELEMENTS WITHIN APP WINDOW ###

    ## text box
    def disable_textbox(self, text_box):
        text_box.setDisabled(True)

    def enable_textbox(self, text_box):
        text_box.setDisabled(False)
    
    ## keyboard
    def disable_keyboard(self, keyboard_btns):
        for keyboard_row in keyboard_btns:
            for btn in keyboard_row:
                btn.setDisabled(True)

    def enable_keyboard(self, keyboard_btns):
        for keyboard_row in keyboard_btns:
            for btn in keyboard_row:
                btn.setDisabled(False)

    ## text box and keyboard
    def input_character_in_text_box(self, char, text_box):
        backspace = '\u232B'
        if char != backspace:
            text_box.setText(char)
        else:
            text_box.clear()
    
    ## tabbing order
    def set_tab_order(self):
        self.setTabOrder(self.easy_btn, self.medium_btn)
        self.setTabOrder(self.medium_btn, self.hard_btn)
        self.setTabOrder(self.hard_btn, self.guess_text_box)
        self.setTabOrder(self.guess_text_box, self.guess_btn)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.focusWidget() == self.guess_text_box:
                input_text = self.guess_text_box.text()
                self.process_guess(input_text)
            else:
                self.focusWidget().click()

        # Call the base class method to ensure normal event processing
        super().keyPressEvent(event)

    ### END OF HELPER METHODS FOR ELEMENTS WITHIN APP WINDOW ###

    ### METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###

    def start_game(self, difficulty):
        self.hangman_game.reset_hangman()
        self.hangman_game.set_current_word(difficulty)
        print(self.hangman_game.get_current_word())
        self.enable_keyboard(self.keyboard_btns)
        self.enable_textbox(self.guess_text_box)
        self.update_game_progress_widget(True)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    def update_game_progress_widget(self, new_game):
        if self.hangman_game.current_word != None:
            if new_game:
                self.clear_layout(self.game_progress_layout)
                self.game_progress_boxes = []
                for char in self.hangman_game.current_word:
                    text_box = QLineEdit()
                    text_box.setMaxLength(1)

                    font_metrics = text_box.fontMetrics()
                    width = font_metrics.horizontalAdvance('MM')
                    text_box.setFixedWidth(width + 10)

                    self.disable_textbox(text_box)
                    self.game_progress_boxes.append(text_box)
                    self.game_progress_layout.addWidget(text_box)
            else:
                for index, progress_box in enumerate(self.game_progress_boxes):
                    progress_box.setText(self.hangman_game.current_word_progress[index])
    
    def process_guess(self, input):
        the_was_guess_correct = self.hangman_game.process_guess(input)
        if the_was_guess_correct:
            self.update_game_progress_widget(False)
        if self.hangman_game.is_the_game_over:
            self.disable_keyboard(self.keyboard_btns)
            self.disable_textbox(self.guess_text_box)
            print(self.hangman_game.did_you_win)

    ### END OF METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()