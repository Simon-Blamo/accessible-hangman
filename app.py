from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtTextToSpeech import QTextToSpeech
from layout_colorwidget import Color
from hangman import Hangman
import nltk
nltk.download('words')
nltk.download('cmudict')
from nltk.corpus import words as nltk_words
from nltk.corpus import cmudict
import sys
import json
import re
import string
from typing import Dict, List

# Enhanced Theme class to include accessibility features for new UI elements
class Theme:
    CONTRAST = {
        "background": "white", 
        "text": "black", 
        "button": "white", 
        "button_text": "black",
        "dropdown": "white",
        "dropdown_text": "black",
        "dialog": "white",
        "dialog_text": "black",
        "listbox": "white",
        "listbox_text": "black",
        "menu": "white",
        "menu_text": "black",
        "grade_indicator": "black",
        "label": "Black & White Contrast ⚫⚪"
    }
    
    BLUE_YELLOW = {
        "background": "#FFFFE0", 
        "text": "black", 
        "button": "blue", 
        "button_text": "white",
        "dropdown": "#FFFFE0",
        "dropdown_text": "black",
        "dialog": "#FFFFE0",
        "dialog_text": "black",
        "listbox": "#FFFFE0",
        "listbox_text": "black",
        "menu": "#FFFFE0",
        "menu_text": "black",
        "grade_indicator": "blue",
        "label": "Blue-Yellow Color Blindness 🔵🟡"
    }
    
    RED_GREEN = {
        "background": "#E0FFFF", 
        "text": "black", 
        "button": "blue", 
        "button_text": "white",
        "dropdown": "#E0FFFF",
        "dropdown_text": "black",
        "dialog": "#E0FFFF",
        "dialog_text": "black",
        "listbox": "#E0FFFF",
        "listbox_text": "black",
        "menu": "#E0FFFF",
        "menu_text": "black",
        "grade_indicator": "blue",
        "label": "Red-Green Color Blindness 🔴🟢"
    }
    
    MONOCHROMATIC = {
        "background": "grey", 
        "text": "black", 
        "button": "darkgrey", 
        "button_text": "black",
        "dropdown": "lightgrey",
        "dropdown_text": "black",
        "dialog": "grey",
        "dialog_text": "black",
        "listbox": "lightgrey",
        "listbox_text": "black",
        "menu": "darkgrey",
        "menu_text": "black",
        "grade_indicator": "darkgrey",
        "label": "Monochromatic 🌑"
    }
    
    DARK_MODE = {
        "background": "#3A3A3A", 
        "text": "white", 
        "button": "#3C3C3C", 
        "button_text": "white",
        "dropdown": "#2C2C2C",
        "dropdown_text": "white",
        "dialog": "#3A3A3A",
        "dialog_text": "white",
        "listbox": "#2C2C2C",
        "listbox_text": "white",
        "menu": "#2C2C2C",
        "menu_text": "white",
        "grade_indicator": "#4C4C4C",
        "label": "Dark Mode (Default) 🌙"
    }

class WordGradeClassifier:
    def __init__(self):
        self.phoneme_dict = cmudict.dict()
        self.words = set(nltk_words.words())
        
        self.grade_levels = {
            'K': [],  # 3-4 letters, simple phonics
            '1': [],  # 4-5 letters, basic sight words
            '2': [],  # 5-6 letters, basic patterns
            '3': [],  # 6-7 letters, compound words
            '4': [],  # 7-8 letters, prefixes/suffixes
            '5': [],  # 8-9 letters, academic words
            '6': [],  # 9-10 letters, complex patterns
            '7': [],  # 10-11 letters, advanced vocabulary
            '8': [],  # 11-12 letters, scientific terms
            '9': [],  # 12-13 letters, specialized vocabulary
            '10': [], # 13-14 letters, advanced academic
            '11': [], # 14-15 letters, technical terms
            '12': []  # 15+ letters, professional vocabulary
        }

    def count_syllables(self, word: str) -> int:
        word = word.lower()
        try:
            return len([ph for ph in self.phoneme_dict[word][0] if ph.strip(string.ascii_letters)])
        except KeyError:
            count = 0
            vowels = 'aeiouy'
            word = word.lower()
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith('e'):
                count -= 1
            if count == 0:
                count += 1
            return count

    def calculate_complexity_score(self, word: str) -> float:
        word = word.lower()
        score = 0.0
        
        length = len(word)
        score += min(length / 3, 5)
        
        syllables = self.count_syllables(word)
        score += syllables * 0.6
        
        patterns = {
            r'([^aeiou]{3,})': 1.0,
            r'(ph|th|ch|sh|wh)': 0.5,
            r'(tion|sion)': 1.0,
            r'(pre|sub|trans)': 0.5,
            r'(ing|ed|ly|er|est)': 0.3,
            r'([^aeiou]y)': 0.3,
            r'([aeiou]{2,})': 0.4,
        }
        
        for pattern, weight in patterns.items():
            if re.search(pattern, word):
                score += weight
                
        return score

    def assign_grade_level(self, word: str) -> str:
        score = self.calculate_complexity_score(word)
        
        thresholds = {
            'K': 2,    '1': 3,    '2': 4,    '3': 5,
            '4': 6,    '5': 7,    '6': 8,    '7': 9,
            '8': 10,   '9': 11,   '10': 12,  '11': 13,
            '12': 14
        }
        
        for grade, threshold in thresholds.items():
            if score <= threshold:
                return grade
        return '12'

    def classify_word_list(self, words: List[str]) -> Dict[str, List[str]]:
        self.grade_levels = {grade: [] for grade in self.grade_levels.keys()}
        
        for word in words:
            word = word.strip().lower()
            if word and word.isalpha():
                grade = self.assign_grade_level(word)
                self.grade_levels[grade].append(word)
        
        return self.grade_levels

    def save_grade_levels(self, filename: str = 'grade_level_words.json'):
        with open(filename, 'w') as file:
            json.dump(self.grade_levels, file, indent=2)

    def load_grade_levels(self, filename: str = 'grade_level_words.json') -> Dict[str, List[str]]:
        try:
            with open(filename, 'r') as file:
                self.grade_levels = json.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found. Creating new classifications...")
            words = list(self.words)[:5000]
            self.classify_word_list(words)
            self.save_grade_levels()
        return self.grade_levels

class WordLists:
    def __init__(self):
        self.classifier = WordGradeClassifier()
        self.grade_levels = {}
        self.custom_words = []
        self.load_or_create_word_lists()
        
    def load_or_create_word_lists(self):
        self.grade_levels = self.classifier.load_grade_levels()
        self.custom_words = self.load_custom_words()

    def add_custom_word(self, word):
        if word not in self.custom_words:
            self.custom_words.append(word)
            grade = self.classifier.assign_grade_level(word)
            self.grade_levels[grade].append(word)
            self.save_custom_words()
            self.classifier.save_grade_levels()

    def remove_custom_word(self, word):
        if word in self.custom_words:
            self.custom_words.remove(word)
            for grade in self.grade_levels:
                if word in self.grade_levels[grade]:
                    self.grade_levels[grade].remove(word)
            self.save_custom_words()
            self.classifier.save_grade_levels()

    def load_custom_words(self):
        try:
            with open('custom_words.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_custom_words(self):
        with open('custom_words.json', 'w') as f:
            json.dump(self.custom_words, f)

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

class MainWindow(QMainWindow):
    def __init__(self):
        self.game_mode = "difficulty"  # or "grade"
        self.word_lists = WordLists()
        self.speech = QTextToSpeech()
        self.current_grade = 'K'
        self.learning_mode = False
        self.current_theme = Theme.CONTRAST
        super().__init__()
        self.setWindowTitle("Hangman")
        self.hangman_game: Hangman = Hangman()
        
        # Initialize font settings
        self.current_font_family = "Arial"
        self.current_font_size = 12
        
        # Create menu bar
        self.create_menu_bar()
        
        # Initalize buttons & elemetns
        self.hangman_game: Hangman = Hangman()              # Initializes hangman object.
        self.easy_btn: QPushButton = None                   # Easy level button
        self.medium_btn: QPushButton = None                 # Medium level button
        self.hard_btn: QPushButton = None                   # Hard level button
        self.guess_text_box: QLineEdit = None               # text box for users to guess with
        self.keyboard_btns: list[list[QPushButton]] = None  # list of lists contains buttons found on on-screen keyboard
        self.guess_btn: QPushButton = None                  # button that locks in character guess
        self.game_progress_boxes: list[QLineEdit] = None    # text boxes which showcase the progress of the current word

        # Widgets are essential elements in a UI. Think Buttons, Textboxes, images, etc.

        # Layout are basically spaces where you can place widgets, and even other layouts.

        ## QVBoxLayout() is a layout object. The V in the name stands for Vertical. When widgets, or layouts are added to the this layout, they are ordered vertically.

        ## QHBoxLayout() is a layout object. The H in the name stands for Horizontal. When widgets, or layouts are added to the this layout, they are ordered horizontally.

        # Set buttons & elements layouts
        page_layout = QVBoxLayout()                         # layout for entire window app. It's basically a base that contains everything else within the app
        difficulty_btn_layout = QHBoxLayout()               # layout for difficulty buttons
        self.game_progress_layout = QHBoxLayout()           # layout for word progress
        image_layout = QHBoxLayout()                        # layout for hangman
        input_layout = QHBoxLayout()                        # layout for guess text box
        keyboard_container_layout = QVBoxLayout()           # layout for beyboard
        keyboard_widget = None
        self.stacklayout = QStackedLayout()
        page_layout.addLayout(difficulty_btn_layout)        # adding to layout
        page_layout.addLayout(image_layout)
        page_layout.addLayout(self.game_progress_layout)
        page_layout.addLayout(input_layout)
        page_layout.addLayout(keyboard_container_layout)
        page_layout.addLayout(self.stacklayout)
        self.init_difficulty_btns(difficulty_btn_layout)    # creating/rendering buttons
        self.init_hangman_image(image_layout)               # creating/rendering image
        self.init_guess_text_box(input_layout)              # creating/rendering text_box

        keyboard_widget, self.keyboard_btns = self.init_keyboard_widget()
        keyboard_container_layout.addWidget(keyboard_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # add theme selection combo box
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Theme") 
        self.theme_combo.addItem(Theme.CONTRAST["label"])
        self.theme_combo.addItem(Theme.BLUE_YELLOW["label"])
        self.theme_combo.addItem(Theme.RED_GREEN["label"])
        self.theme_combo.addItem(Theme.MONOCHROMATIC["label"])
        self.theme_combo.addItem(Theme.DARK_MODE["label"])
        self.theme_combo.setFixedWidth(100)                    # adjust dropdown size
        self.theme_combo.currentIndexChanged.connect(self.on_theme_change)

        difficulty_btn_layout.addWidget(self.theme_combo)     # add the combo box to the layout

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)
        self.set_tab_order()
    def show_word_list_dialog(self):
        dialog = AccessibleWordListDialog(
                self,
                self.current_theme,
                self.current_font_family,
                self.current_font_size
            )
        
        # Load existing words
        for word in self.word_lists.custom_words:
            item = QListWidgetItem(f"{word} (Grade {self.word_lists.classifier.assign_grade_level(word)})")
            dialog.list_widget.addItem(item)
        
        # Connect buttons
        dialog.add_button.clicked.connect(
            lambda: self.add_custom_word(
                dialog.word_input.text(),
                dialog.grade_combo.currentText(),
                dialog.list_widget
            )
        )
        dialog.remove_button.clicked.connect(
            lambda: self.remove_custom_word(dialog.list_widget)
        )
        dialog.close_button.clicked.connect(dialog.accept)
        
        dialog.exec()

    def add_custom_word(self, word, grade, list_widget):
        if word:
            self.word_lists.add_custom_word(word)
            item = QListWidgetItem(f"{word} (Grade {grade})")
            list_widget.addItem(item)
            
    def remove_custom_word(self, list_widget):
        if list_widget.currentItem():
            word = list_widget.currentItem().text().split(' (Grade')[0]
            self.word_lists.remove_custom_word(word)
            list_widget.takeItem(list_widget.row(list_widget.currentItem()))

    # Sets up first hangman image
    def init_hangman_image(self, image_layout):
        self.label = QLabel(self)
        self.pixmap = QPixmap('./assets/sticks/Hangman0.png').scaled(128, 192)
        self.label.setPixmap(self.pixmap)
        self.resize(self.pixmap.width(), self.pixmap.height())
        image_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def change_grade_level(self, grade):
        """Change the current grade level and update word list."""
        self.current_grade = grade
        # Update word list for the game
        if grade in self.word_lists.grade_levels:
            words = self.word_lists.grade_levels[grade]
            self.hangman_game.set_word_list(words)
            # Optional: Show feedback
            grade_text = "Kindergarten" if grade == 'K' else f"Grade {grade}"
            QMessageBox.information(self, "Grade Level Changed", 
            f"Changed to {grade_text} words\nWord list size: {len(words)} words")

    def toggle_learning_mode(self, enabled):
        """Toggle learning mode on/off."""
        self.learning_mode = enabled
        if enabled:
            # Announce that learning mode is enabled
            self.speech.say("Learning mode enabled")
        else:
            self.speech.say("Learning mode disabled")

    def speak_letter(self, letter):
        """Speak a letter aloud."""
        if self.learning_mode:
            self.speech.say(letter)

    def speak_word(self, word):
        """Speak a word aloud."""
        if self.learning_mode:
            # Small delay before speaking the word
            QTimer.singleShot(500, lambda: self.speech.say(word))
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Game Mode Menu
        game_mode_menu = menubar.addMenu("Game Mode")
        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)
        
        difficulty_mode = QAction("Difficulty Mode", self, checkable=True)
        difficulty_mode.setChecked(True)
        difficulty_mode.triggered.connect(lambda: self.change_game_mode("difficulty"))
        mode_group.addAction(difficulty_mode)
        game_mode_menu.addAction(difficulty_mode)
        
        grade_mode = QAction("Grade Level Mode", self, checkable=True)
        grade_mode.triggered.connect(lambda: self.change_game_mode("grade"))
        mode_group.addAction(grade_mode)
        game_mode_menu.addAction(grade_mode)

        # Grade Level Menu (initially disabled)
        self.grade_menu = menubar.addMenu("Grade Level")
        grade_group = QActionGroup(self)
        grade_group.setExclusive(True)
        
        grades = ['K'] + [str(i) for i in range(1, 13)]
        for grade in grades:
            action = QAction(f"Grade {grade}", self, checkable=True)
            if grade == self.current_grade:
                action.setChecked(True)
            action.triggered.connect(lambda checked, g=grade: self.change_grade_level(g))
            grade_group.addAction(action)
            self.grade_menu.addAction(action)
        
        # Initially disable grade menu since we start in difficulty mode
        for action in self.grade_menu.actions():
            action.setEnabled(False)

        # Learning Mode Menu
        learning_menu = menubar.addMenu("Learning Mode")
        self.learning_mode_action = QAction("Enable Learning Mode", self, checkable=True)
        self.learning_mode_action.triggered.connect(self.toggle_learning_mode)
        learning_menu.addAction(self.learning_mode_action)

        # Word Lists Menu
        word_list_menu = menubar.addMenu("Word Lists")
        manage_words_action = QAction("Manage Custom Words", self)
        manage_words_action.triggered.connect(self.show_word_list_dialog)
        word_list_menu.addAction(manage_words_action)
        
        # Font Settings Menu
        font_menu = menubar.addMenu("Font Settings")
        
        # Font Family Submenu
        font_family_menu = QMenu("Font Family", self)
        font_menu.addMenu(font_family_menu)
        
        # Add font options
        fonts = {
            "Arial": "Arial",
            "Comic Sans MS": "Comic Sans MS",
            "OpenDyslexic": "OpenDyslexic"  # You'll need to ensure this font is installed
        }
        
        font_group = QActionGroup(self)
        font_group.setExclusive(True)
        
        for font_name, font_family in fonts.items():
            action = QAction(font_name, self, checkable=True)
            if font_family == self.current_font_family:
                action.setChecked(True)
            action.triggered.connect(lambda checked, f=font_family: self.change_font_family(f))
            font_group.addAction(action)
            font_family_menu.addAction(action)
        
        # Font Size Submenu
        font_size_menu = QMenu("Font Size", self)
        font_menu.addMenu(font_size_menu)
        
        sizes = [8, 10, 12, 14, 16, 18, 20]
        size_group = QActionGroup(self)
        size_group.setExclusive(True)
        
        for size in sizes:
            action = QAction(f"{size}pt", self, checkable=True)
            if size == self.current_font_size:
                action.setChecked(True)
            action.triggered.connect(lambda checked, s=size: self.change_font_size(s))
            size_group.addAction(action)
            font_size_menu.addAction(action)

    def change_font_family(self, font_family):
        self.current_font_family = font_family
        self.update_fonts()

    def change_font_size(self, size):
        self.current_font_size = size
        self.update_fonts()

    def change_game_mode(self, mode):
        """Switch between difficulty-based and grade-based modes."""
        self.game_mode = mode
        if mode == "difficulty":
            # Show difficulty buttons, hide grade selector
            self.easy_btn.setText("Easy")
            self.medium_btn.setText("Medium")
            self.hard_btn.setText("Hard")
            self.easy_btn.show()
            self.medium_btn.show()
            self.hard_btn.show()
            # Disable grade menu
            self.grade_menu.setEnabled(False)
        else:  # grade mode
            # Hide difficulty buttons, show grade selector
            self.easy_btn.hide()
            self.medium_btn.hide()
            self.hard_btn.hide()
            # Enable grade menu actions
            self.grade_menu.setEnabled(True)
            for action in self.grade_menu.actions():
                action.setEnabled(True)

    def change_grade_level(self, grade):
        self.current_grade = grade
        if self.game_mode == "grade":
            words = self.word_lists.grade_levels.get(grade, [])
            if words:
                self.hangman_game.set_word_list(words)
                self.start_game(0)  # Start new game with updated word list

    def update_fonts(self):
        new_font = QFont(self.current_font_family, self.current_font_size)
        
        # Update difficulty buttons
        if self.easy_btn:
            self.easy_btn.setFont(new_font)
        if self.medium_btn:
            self.medium_btn.setFont(new_font)
        if self.hard_btn:
            self.hard_btn.setFont(new_font)
        
        # Update guess text box
        if self.guess_text_box:
            self.guess_text_box.setFont(new_font)
        
        # Update keyboard buttons
        if self.keyboard_btns:
            for row in self.keyboard_btns:
                for btn in row:
                    btn.setFont(new_font)
        
        # Update game progress boxes
        if self.game_progress_boxes:
            for box in self.game_progress_boxes:
                box.setFont(new_font)

        # Update guess button
        if self.guess_btn:
            self.guess_btn.setFont(new_font)
    
    def init_difficulty_btns(self, difficulty_btn_layout):
        font = QFont(self.current_font_family, self.current_font_size)
        
        btn = QPushButton("Easy")
        btn.setFont(font)
        btn.pressed.connect(lambda:self.start_game(0))
        self.easy_btn = btn
        difficulty_btn_layout.addWidget(btn)

        btn = QPushButton("Medium")
        btn.setFont(font)
        btn.pressed.connect(lambda:self.start_game(1))
        self.medium_btn = btn
        difficulty_btn_layout.addWidget(btn)

        btn = QPushButton("Hard")
        btn.setFont(font)
        btn.pressed.connect(lambda:self.start_game(2))
        self.hard_btn = btn
        difficulty_btn_layout.addWidget(btn)

    def update_hangman_image(self):
        wrong_guesses = self.hangman_game.number_of_wrong_guesses
        pixmap_path = f'./assets/sticks/Hangman{wrong_guesses}.png'
        self.pixmap = QPixmap(pixmap_path).scaled(128, 192)
        self.label.setPixmap(self.pixmap)

    def init_guess_text_box(self, input_layout):
        self.guess_text_box = QLineEdit()
        self.guess_text_box.setFont(QFont(self.current_font_family, self.current_font_size))
        self.guess_text_box.setMaxLength(1)

        font_metrics =  self.guess_text_box.fontMetrics()
        width = font_metrics.horizontalAdvance('MM')

        reg_ex = QRegularExpression('[A-Za-z]{1}')
        validator = QRegularExpressionValidator(reg_ex)

        self.guess_text_box.setValidator(validator)
        self.guess_text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guess_text_box.setFixedWidth(width + 10)

        self.disable_textbox( self.guess_text_box)
        input_layout.addWidget( self.guess_text_box)
    
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
    

    ### HELPER METHODS FOR ELEMENTS WITHIN APP WINDOW ###

    ##theme customization

    #m ethod to handle theme changes from combo box
    def on_theme_change(self, index):
        if index == 1:
            self.apply_theme(Theme.CONTRAST)
        elif index == 2:
            self.apply_theme(Theme.BLUE_YELLOW)
        elif index == 3:
            self.apply_theme(Theme.RED_GREEN)
        elif index == 4:
            self.apply_theme(Theme.MONOCHROMATIC)
        elif index == 5:
            self.apply_theme(Theme.DARK_MODE)

    def apply_theme(self, theme):
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text']};")
        
        # button styles
        button_style = f"background-color: {theme['button']}; color: {theme['button_text']}; border: 1px solid {theme['button_text']}; border-radius: 7px; padding: 3px 7px;"
        self.easy_btn.setStyleSheet(button_style)
        self.medium_btn.setStyleSheet(button_style)
        self.hard_btn.setStyleSheet(button_style)
        self.guess_text_box.setStyleSheet(f"color: {theme['text']}; background-color: {theme['background']};")

    
    # Apply similar styles to other widgets as needed (like keyboard buttons and progress boxes)e



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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.focusWidget() == self.guess_text_box:
                input_text = self.guess_text_box.text()
                self.process_guess(input_text)
            else:
                self.focusWidget().click()

        super().keyPressEvent(event)

    ## text box and keyboard and speech
    def input_character_in_text_box(self, char, text_box):
        backspace = '\u232B'
        if char != backspace:
            text_box.setText(char)
            if self.learning_mode:
                self.speak_letter(char)
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
        print(f"Game mode: {self.game_mode}, Grade: {self.current_grade}")  # Debug line
        
        if self.game_mode == "difficulty":
            self.hangman_game.set_current_word(difficulty)
        else:  # grade mode
            words = self.word_lists.grade_levels.get(self.current_grade, [])
            if words:
                self.hangman_game.set_word_list(words)
                self.hangman_game.select_random_word()
            else:
                QMessageBox.warning(self, "No Words Available", 
                    f"No words available for grade {self.current_grade}. Using default words.")
                self.hangman_game.set_current_word(0)
        
        self.update_hangman_image()
        
        if self.learning_mode:
            QTimer.singleShot(500, lambda: self.speech.say(
                f"New game! This word has {len(self.hangman_game.current_word)} letters"))
        
        print(f"Selected word: {self.hangman_game.get_current_word()}")  # Debug line
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
        if not input:
            return
                
        if self.learning_mode:
            self.speak_letter(input)
            
        the_was_guess_correct = self.hangman_game.process_guess(input)
        if the_was_guess_correct:
            self.update_game_progress_widget(False)
            if self.learning_mode:
                self.speech.say("Correct!")
                # Speak word progress with known letters
                progress_word = ''.join(self.hangman_game.current_word_progress).strip()
                if progress_word:
                    QTimer.singleShot(1000, lambda: self.speech.say(progress_word))
        else:
            self.update_hangman_image()
            if self.learning_mode:
                self.speech.say("Try again!")
                
        if self.hangman_game.is_the_game_over:
            self.disable_keyboard(self.keyboard_btns)
            self.disable_textbox(self.guess_text_box)
            if self.learning_mode:
                if self.hangman_game.did_you_win:
                    self.speech.say("Congratulations!")
                    # Speak the complete word
                    QTimer.singleShot(1000, lambda: self.speak_word(self.hangman_game.current_word))
                else:
                    self.speech.say(f"Game Over! The word was {self.hangman_game.current_word}")

    ### END OF METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
