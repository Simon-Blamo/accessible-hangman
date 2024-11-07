from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from layout_colorwidget import Color
from hangman import Hangman
import sys
# Set up window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman")                      # Sets title of window
        self.hangman_game: Hangman = Hangman()              # Initializes hangman object.
        self.easy_btn: QPushButton = None                   # Easy level button
        self.medium_btn: QPushButton = None                 # Medium level button
        self.hard_btn: QPushButton = None                   # Hard level button
        self.incorrect_guesses_label: QLabel = None
        self.guess_text_box: QLineEdit = None               # text box for users to guess with
        self.keyboard_btns: list[list[QPushButton]] = None  # list of lists contains buttons found on on-screen keyboard
        self.guess_btn: QPushButton = None                  # button that locks in character guess
        self.default_colors: dict[str, str] = {}               # holds default colors of elements to be used later on
        self.game_progress_boxes: list[QLineEdit] = None    # text boxes which showcase the progress of the current word

        # Widgets are essential elements in a UI. Think Buttons, Textboxes, images, etc.

        # Layouts are basically spaces where you can place widgets, and even other layouts.

        ## QVBoxLayout() is a layout object. The V in the name stands for Vertical. When widgets, or layouts are added to the this layout, they are ordered vertically.

        ## QHBoxLayout() is a layout object. The H in the name stands for Horizontal. When widgets, or layouts are added to the this layout, they are ordered horizontally.

        page_layout = QVBoxLayout()                         # layout for entire window app. It's basically a base that contains everything else within the app
        difficulty_btn_layout = QHBoxLayout()               # layout for difficulty buttons
        self.game_progress_layout = QHBoxLayout()           # layout for word progress
        incorrect_guesses_layout = QHBoxLayout()       # layout for incorrect guesses
        image_layout = QHBoxLayout()                        # layout for hangman
        input_layout = QHBoxLayout()                        # layout for guess text box
        keyboard_container_layout = QVBoxLayout()           # layout for beyboards

        keyboard_widget = None
        
        self.stacklayout = QStackedLayout()

        page_layout.addLayout(difficulty_btn_layout)        # adding to layout
        page_layout.addLayout(incorrect_guesses_layout)
        page_layout.addLayout(image_layout)
        page_layout.addLayout(self.game_progress_layout)
        page_layout.addLayout(input_layout)
        page_layout.addLayout(keyboard_container_layout)
        page_layout.addLayout(self.stacklayout)

        self.init_difficulty_btns(difficulty_btn_layout)    # creating/rendering buttons
        self.init_incorrect_guesses_widget(incorrect_guesses_layout)
        self.init_hangman_image(image_layout)               # creating/rendering image
        self.init_guess_text_box(input_layout)    # creating/rendering text_box

        keyboard_widget, self.keyboard_btns = self.init_keyboard_widget()       # creating/rendering keyboard buttons and keyboard
        self.get_default_disabled_colors()
        keyboard_container_layout.addWidget(keyboard_widget, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def init_incorrect_guesses_widget(self, incorrect_guesses_layout):
        incorrect_guesses_label = QLabel("Wrong Guesses:  ")
        incorrect_guesses_label.setFixedWidth(400)
        self.incorrect_guesses_label = incorrect_guesses_label
        incorrect_guesses_layout.addWidget(incorrect_guesses_label)

    def init_hangman_image(self, image_layout):
        label = QLabel(self)
        pixmap = QPixmap('./assets/stick.png').scaled(128, 192)
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        image_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

    def init_guess_text_box(self, input_layout):
        self.guess_text_box = QLineEdit()
        self.guess_text_box.setMaxLength(1)

        font_metrics =  self.guess_text_box.fontMetrics()
        width = font_metrics.horizontalAdvance('MM')

        reg_ex = QRegularExpression('[A-Za-z]{1}')
        validator = QRegularExpressionValidator(reg_ex)

        self.guess_text_box.setValidator(validator)
        self.guess_text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guess_text_box.setFixedWidth(width + 10)
        self.guess_text_box.textChanged.connect(self.has_char_been_used)

        self.disable_textbox(self.guess_text_box)
        input_layout.addWidget(self.guess_text_box)
    
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
        keyboard_row_4_btns.append(btn)
        btn.pressed.connect(lambda:self.process_guess(self.guess_text_box.text()))
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
    

    ### HELPER METHODS FOR ELEMENTS WITHIN APP WINDOW ###

    ## incorrect guesses label element
    def update_incorrect_guesses_label(self):
        label = "Wrong Guesses:  "
        incorrect_chars = ""
        for char in self.hangman_game.incorrect_char_guesses:
            incorrect_chars += char + "  "
        self.incorrect_guesses_label.setText(label + incorrect_chars)

    ## text box
    def disable_textbox(self, text_box):
        text_box.setDisabled(True)

    def enable_textbox(self, text_box):
        text_box.setDisabled(False)

    def has_char_been_used(self):
        char_in_text_box = self.guess_text_box.text().upper()
        if char_in_text_box in self.hangman_game.correct_char_guesses or char_in_text_box in self.hangman_game.incorrect_char_guesses:
            self.guess_btn.setDisabled(True)
        elif self.hangman_game.is_the_game_over == False:
            self.guess_btn.setDisabled(False)

    def clear_text_box(self):
        self.guess_text_box.setText("")
    
    ## keyboard
    def disable_keyboard(self, keyboard_btns):
        for keyboard_row in keyboard_btns:
            for btn in keyboard_row:
                self.disable_keyboard_btn(btn)

    def enable_keyboard(self, keyboard_btns):
        for keyboard_row in keyboard_btns:
            for btn in keyboard_row:
                btn.setDisabled(False)

    def disable_keyboard_btn(self, keyboard_btn):
        keyboard_btn.setDisabled(True)

    def find_keyboard_btn(self, keyboard_btn_text):
        for row in self.keyboard_btns:
            for keyboard_btn in row:
                if keyboard_btn.text() == keyboard_btn_text:
                    return keyboard_btn

    def get_default_disabled_colors(self):
        self.default_colors["disabled_btn_background"] = 'WhiteSmoke'
        self.default_colors["disabled_btn_text"] = 'LightGrey'

    def reset_keyboard_btn_colors(self):
        disabled_btn_background_color = self.default_colors['disabled_btn_background']
        disabled_btn_text_color = self.default_colors['disabled_btn_text']
        for row in self.keyboard_btns:
            for key in row:
                focus_color = '#80bfff'
                hover_color = '#cce7ff'
                stylesCSS = "QPushButton:disabled {{ background-color: {}; color: {}; }} QPushButton:hover {{background-color: {};}} QPushButton:focus {{background-color: {};}}".format(disabled_btn_background_color, disabled_btn_text_color, hover_color, focus_color)
                key.setStyleSheet(stylesCSS)

    def change_keyboard_btn_color_based_on_guess(self, keyboard_btn, the_guess_was_correct):
        background_color = None
        text_color = "white"
        if the_guess_was_correct:
            background_color = "green"
        else:
            background_color = "red"
        stylesCSS = "QPushButton:disabled {{ background-color: {}; color: {}; }}".format(background_color, text_color)
        keyboard_btn.setStyleSheet(stylesCSS)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.focusWidget() == self.guess_text_box or (isinstance(self.focusWidget(), QPushButton) and self.focusWidget().text() == self.guess_text_box.text()):
                input_text = self.guess_text_box.text()
                self.process_guess(input_text.upper())
            else:
                input_text = self.guess_text_box.text()
                self.process_guess(input_text.upper())
                self.focusWidget().click()

        super().keyPressEvent(event)


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
    
    ### END OF HELPER METHODS FOR ELEMENTS WITHIN APP WINDOW ###



    ### METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###

    def start_game(self, difficulty):
        self.hangman_game.reset_hangman()
        self.reset_keyboard_btn_colors()
        self.hangman_game.set_current_word(difficulty)
        self.update_incorrect_guesses_label()
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
        if input == '' or input == ' ':
            return
        the_guess_was_correct = self.hangman_game.process_guess(input)
        btn_pressed = self.find_keyboard_btn(input)
        self.disable_keyboard_btn(btn_pressed)
        self.change_keyboard_btn_color_based_on_guess(btn_pressed, the_guess_was_correct)
        if the_guess_was_correct:
            self.update_game_progress_widget(False)
        if self.hangman_game.is_the_game_over:
            self.disable_keyboard(self.keyboard_btns)
            self.disable_textbox(self.guess_text_box)
            #self.reset_keyboard_btn_colors()
            self.get_default_disabled_colors()
        self.update_incorrect_guesses_label()
        self.clear_text_box()

    ### END OF METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()