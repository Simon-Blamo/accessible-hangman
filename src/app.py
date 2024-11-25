from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from hangman import Hangman
from theme import Theme
from audio_accessibility import AudioAccessibility
from pathlib import Path
import sys
import queue
import threading

# Switch to Main Screen
class MainScreen(QWidget):
    def __init__(self, main_window, end_screen, hangman_game, audio_accessibility, thread_event):
        super().__init__()
        self.main_window = main_window
        self.end_screen = end_screen
        self.hangman_game: Hangman = hangman_game              # Initializes hangman object.
        self.audio_accessibility = audio_accessibility
        self.thread_event = thread_event
 
        # Initialize font settings
        self.current_font_family = "Arial"
        self.current_font_size = 12

        page_layout = QVBoxLayout()                         # layout for entire window app. It's basically a base that contains everything else within the app

        # attribute that stores key elements
        self.menu_bar = None
        self.current_theme = Theme.LIGHT_MODE
        self.easy_btn: QPushButton = None                   # Easy level button
        self.medium_btn: QPushButton = None                 # Medium level button
        self.hard_btn: QPushButton = None                   # Hard level button
        self.incorrect_guesses_label: QLabel = None
        self.guess_text_box: QLineEdit = None               # text box for users to guess with
        self.keyboard_btns: list[list[QPushButton]] = None  # list of lists contains buttons found on on-screen keyboard
        self.guess_btn: QPushButton = None                  # button that locks in character guess
        self.default_colors: dict[str, str] = {}            # holds default colors of elements to be used later on
        self.game_progress_boxes: list[QLineEdit] = None    # text boxes which showcase the progress of the current word

        # Set element layouts
        difficulty_btn_layout = QHBoxLayout()               # layout for difficulty buttons
        self.game_progress_layout = QHBoxLayout()           # layout for word progress
        incorrect_guesses_layout = QHBoxLayout()       # layout for incorrect guesses
        image_layout = QHBoxLayout()                        # layout for hangman
        input_layout = QHBoxLayout()                        # layout for guess text box
        keyboard_container_layout = QVBoxLayout()           # layout for keyboard
        keyboard_widget = None
        self.stacklayout = QStackedLayout()


        # Add element's layouts to page layout
        self.create_menu_bar(page_layout)                   
        page_layout.addLayout(difficulty_btn_layout)
        page_layout.addLayout(incorrect_guesses_layout)
        page_layout.addLayout(image_layout)
        page_layout.addLayout(self.game_progress_layout)
        page_layout.addLayout(input_layout)
        page_layout.addLayout(keyboard_container_layout)
        page_layout.addLayout(self.stacklayout)
        
        
        # Creates additional elements
        self.init_difficulty_btns(difficulty_btn_layout)    # creating/rendering buttons
        self.init_incorrect_guesses_widget(incorrect_guesses_layout)
        self.init_hangman_image(image_layout)               # creating/rendering image
        self.init_guess_text_box(input_layout)              # creating/rendering text_box

        # Create keyboard widget
        keyboard_widget, self.keyboard_btns = self.init_keyboard_widget()       # creating/rendering keyboard buttons and keyboard
        self.get_default_disabled_colors()
        keyboard_container_layout.addWidget(keyboard_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set layout
        self.setLayout(page_layout)
        self.apply_theme(self.current_theme)
        self.set_tab_order()
        
    ### METHODS TO INITIALIZE ELEMENTS WITHIN APP WINDOW ###
    # Creates menu bar
    def create_menu_bar(self, page_layout):
        self.menu_bar = QMenuBar(self)
        self.init_font_menu()
        self.init_theme_menu()
        self.init_sound_menu()
        self.init_other_menu()
        page_layout.setMenuBar(self.menu_bar)
    
    # Creates font menu options
    def init_font_menu(self):
        # Font Settings Menu
        font_setting_menu = QMenu("Font Settings", self)
        self.menu_bar.addMenu(font_setting_menu)
        
        # Font Family Submenu
        font_family_menu = QMenu("Font Family", self)
        font_setting_menu.addMenu(font_family_menu)
        
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
        font_setting_menu.addMenu(font_size_menu)
        
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
    
    # Creates theme menu options    
    def init_theme_menu(self):
        # Theme Settings Menu
        theme_menu = self.menu_bar.addMenu("Theme Settings")
        themes_action_menus = QMenu("Themes", self)
        theme_menu.addMenu(themes_action_menus)
        
        themes_groups = QActionGroup(self)
        themes_groups.setExclusive(True)

        for theme in Theme.Themes:
            theme_name = theme["label"]
            action = QAction(theme_name, self, checkable=True)
            themes_groups.addAction(action)
            if theme_name == self.current_theme:
                action.setChecked(True)
            action.triggered.connect(lambda checked, t=theme: self.apply_theme(t))
            theme = self.current_theme
            themes_groups.addAction(action)
            themes_action_menus.addAction(action)

    def init_sound_menu(self):
        sound_menu = QMenu("Sound Settings \U0001F3A4", self)
        self.menu_bar.addMenu(sound_menu)
    
        sound_action = QAction("Voice Input ON", self, checkable=True)
        sound_action.setChecked(True)  # Start with sound on by default
        sound_action.triggered.connect(self.audio_accessibility.update_voice_input_settings)
        sound_menu.addAction(sound_action)
    
    def init_other_menu(self):
        other_menu = QMenu("Other Settings", self)
        self.menu_bar.addMenu(other_menu)
        
        help_action = QAction("Help...", self)
        help_action.triggered.connect(self.display_help_dialog_box)
        other_menu.addAction(help_action) 
        
    def display_help_dialog_box(self):
        was_voice_input_active = self.main_window.audio_accessibility.voice_input_turned_on
        
        if was_voice_input_active:
            self.main_window.audio_accessibility.pause_voice_input()  # Pause if already active

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Help")
        
        help_text = """
        <p><strong>Objective:</strong> Guess the hidden word one letter at a time. You have a limited number of incorrect guesses before the game ends.</p>
    
        <h3>Basic Gameplay:</h3>
        <ul>
            <li>Use the on-screen keyboard or type letters to make guesses.</li>
            <li>Correct guesses will reveal the letters in the word.</li>
            <li>Incorrect guesses will be tracked, and the hangman drawing will progress.</li>
        </ul>
    
        <h3>Speech Commands:</h3>
        <ul>
            <li><strong>"START GAME"</strong>: Start a new game.</li>
            <li><strong>"START GAME EASY"</strong>: Start a new game in Easy mode.</li>
            <li><strong>"START GAME MEDIUM"</strong>: Start a new game in Medium mode.</li>
            <li><strong>"START GAME HARD"</strong>: Start a new game in Hard mode.</li>
            <li><strong>"EXIT", "QUIT", or "QUIT GAME"</strong>: Exit the game.</li>
            <li><strong>"LIST INCORRECT GUESSES"</strong>: Hear the letters you have guessed incorrectly.</li>
            <li><strong>"LIST INCORRECT CHARACTERS"</strong>: Alternate command for incorrect guesses.</li>
            <li><strong>"LIST CORRECT LETTERS"</strong>: Hear the letters you have guessed correctly.</li>
            <li><strong>"HANGMAN STATUS"</strong>: Hear the current status of the hangman drawing.</li>
            <li><strong>"WORD STATUS"</strong>: Hear the current state of the hidden word.</li>
            <li><strong>"PLAY AGAIN"</strong>: Restart the game after it ends.</li>
            <li><strong>"GUESS _"</strong>: Guess a specific letter (e.g., GUESS A)</li>
        </ul>
    
        <h3>Settings:</h3>
        <p>Use the <strong>Theme Settings</strong> menu to change the game's color theme for accessibility.<br>
        Use the <strong>Font Settings</strong> menu to adjust the font style and size.</p>

        """
    
        dlg.setTextFormat(Qt.TextFormat.RichText)  # Enables rich text formatting
        dlg.setText(help_text)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Ok:
            print("Help dialog closed")
        if was_voice_input_active:
            self.main_window.audio_accessibility.resume_voice_input()  # Resume if it was active

    # Intializes & checks for level difficulty
    def init_difficulty_btns(self, difficulty_btn_layout):
        font = QFont(self.current_font_family, self.current_font_size)
        
        # Easy difficulty
        btn = QPushButton("Easy")
        btn.setFont(font)
        btn.pressed.connect(lambda:self.start_game(0))
        self.easy_btn = btn
        difficulty_btn_layout.addWidget(btn)

        # Med difficulty
        btn = QPushButton("Medium")
        btn.setFont(font)
        btn.pressed.connect(lambda:self.start_game(1))
        self.medium_btn = btn
        difficulty_btn_layout.addWidget(btn)

        # Hard difficulty
        btn = QPushButton("Hard")
        btn.setFont(font)
        btn.pressed.connect(lambda:self.start_game(2))
        self.hard_btn = btn
        difficulty_btn_layout.addWidget(btn)

    # Lists letters gussed incorrectly
    def init_incorrect_guesses_widget(self, incorrect_guesses_layout):
        font = QFont(self.current_font_family, self.current_font_size)
        font.setBold(True)
        incorrect_guesses_label = QLabel("Wrong Guesses:  ")
        incorrect_guesses_label.setFixedWidth(500)
        incorrect_guesses_label.setFont(font)
        self.incorrect_guesses_label = incorrect_guesses_label
        incorrect_guesses_layout.addWidget(incorrect_guesses_label)

    # Sets up first hangman image
    def init_hangman_image(self, image_layout):
        self.label = QLabel(self)
        self.pixmap = QPixmap('../assets/sticks/Hangman0.png').scaled(128, 192)
        self.label.setPixmap(self.pixmap)
        self.resize(self.pixmap.width(), self.pixmap.height())
        image_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Updates hangman image when guess incorrectly
    def update_hangman_image(self):
        num_wrong_guesses = self.hangman_game.number_of_wrong_guesses
        pixmap_path = f'../assets/sticks/Hangman{num_wrong_guesses}.png'
        self.pixmap = QPixmap(pixmap_path).scaled(128, 192)
        self.label.setPixmap(self.pixmap)

    # Sets up text box showing current selected letter
    def init_guess_text_box(self, input_layout):
        self.guess_text_box = QLineEdit()
       
        # Bolded text to read better
        font = QFont(self.current_font_family, self.current_font_size)
        font.setBold(True)
        self.guess_text_box.setFont(font)
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
    
    # Sets up keyboard widget
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
        self.btns_array = []
        
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

        self.btns_array.append(keyboard_row_1_btns)
        self.btns_array.append(keyboard_row_2_btns)
        self.btns_array.append(keyboard_row_3_btns)
        self.btns_array.append(keyboard_row_4_btns)

        self.disable_keyboard(self.btns_array)

        keyboard_layout.addLayout(keyboard_row_1_layout)
        keyboard_layout.addLayout(keyboard_row_2_layout)
        keyboard_layout.addLayout(keyboard_row_3_layout)
        keyboard_layout.addLayout(keyboard_row_4_layout)
        keyboard_widget.setLayout(keyboard_layout)
        keyboard_widget.setFixedWidth(500)

        return [keyboard_widget, self.btns_array]
    ### END OF METHODS TO INITIALIZE ELEMENTS WITHIN APP WINDOW ###
    

    ### HELPER METHODS FOR ELEMENTS WITHIN APP WINDOW ###
    
    ## incorrect guesses label element
    def update_incorrect_guesses_label(self):
        label = "Wrong Guesses:  "
        incorrect_chars = ""
        for char in self.hangman_game.incorrect_char_guesses:
            incorrect_chars += char + "  "
        self.incorrect_guesses_label.setText(label + incorrect_chars)

    ##theme customization

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
        self.apply_theme(self.current_theme)

    def change_keyboard_btn_color_based_on_guess(self, keyboard_btn, the_guess_was_correct):
        new_background = self.current_theme["correct_bg"] if the_guess_was_correct else self.current_theme["incorrect_bg"]
        buttonStyle = f"QPushButton{{background-color: {self.current_theme['button']};color: {self.current_theme['button_text']}; border: 1px solid {self.current_theme['button_text']}; border-radius: 7px; padding: 3px 7px;}} QPushButton:disabled {{background-color: {new_background}; color: {self.current_theme['disabled_btn_text']}; border: 1px solid {self.current_theme['disabled_btn_text']}; border-radius: 7px;}}"
        keyboard_btn.setStyleSheet(buttonStyle)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.focusWidget() == self.guess_text_box or (isinstance(self.focusWidget(), QPushButton) and self.focusWidget().text() == self.guess_text_box.text()):
                self.main_window.reset_timer_signal.emit()
                input_text = self.guess_text_box.text()
                self.process_guess(input_text.upper())
            else:
                self.main_window.reset_timer_signal.emit()
                self.focusWidget().click()

        super().keyPressEvent(event)

    ## text box and keyboard
    def input_character_in_text_box(self, char, text_box):
        self.main_window.reset_timer_signal.emit()
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

    # Starts game by setting up hangman
    def start_game(self, difficulty):
        self.hangman_game.reset_hangman()
        self.reset_keyboard_btn_colors()
        self.hangman_game.set_current_word(difficulty)
        self.update_incorrect_guesses_label()
        self.update_hangman_image()
        print(self.hangman_game.get_current_word())
        self.enable_keyboard(self.keyboard_btns)
        self.enable_textbox(self.guess_text_box)
        self.update_game_progress_widget(True)
        self.audio_accessibility.update_game_is_ongoing(True)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    # Updates word progress as user guesses
    def update_game_progress_widget(self, new_game):
        if self.hangman_game.current_word != None:
            if new_game:
                self.clear_layout(self.game_progress_layout)
                self.game_progress_boxes = []
                for char in self.hangman_game.current_word:
                    text_box = QLineEdit()
                    text_box.setMaxLength(1)
                    theme = self.current_theme
                    text_box.setStyleSheet(f"color: {theme['guess_text']}; background-color: {theme['guess_background']};")

                    # Bolded text to read better
                    font = QFont(self.current_font_family, self.current_font_size)
                    font.setBold(True)
                    text_box.setFont(font)

                    # Centered text
                    text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Set shape & size
                    font_metrics = text_box.fontMetrics()
                    width = font_metrics.horizontalAdvance('MM')
                    text_box.setFixedWidth(width + 10)
            
                    self.disable_textbox(text_box)
                    self.game_progress_boxes.append(text_box)
                    self.game_progress_layout.addWidget(text_box)
            else:
                self.set_game_progress_widget()
    
    # Sets values of game progress boxes based on current word progress
    def set_game_progress_widget(self):
        if len(self.hangman_game.current_word_progress) == 0:
            for index, progress_box in enumerate(self.game_progress_boxes):
                progress_box.setText('')
        else:
            for index, progress_box in enumerate(self.game_progress_boxes):
                progress_box.setText(self.hangman_game.current_word_progress[index])
    
    # Handles guessed letter
    def process_guess(self, input):
        if input == '' or input == ' ':
            return
        the_guess_was_correct = self.hangman_game.process_guess(input)
        self.thread_event.set()
        btn_pressed = self.find_keyboard_btn(input)
        self.disable_keyboard_btn(btn_pressed)
        self.change_keyboard_btn_color_based_on_guess(btn_pressed, the_guess_was_correct)
        if the_guess_was_correct:
            self.update_game_progress_widget(False)
        else:
            self.update_hangman_image()    

        if self.hangman_game.is_the_game_over:
            self.audio_accessibility.update_game_is_ongoing(False)
            self.disable_keyboard(self.keyboard_btns)
            self.disable_textbox(self.guess_text_box)
            #self.reset_keyboard_btn_colors()
            self.get_default_disabled_colors()

            # Wait before going to next screen to see hangman image & word progress update
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self.go_to_end)
            timer.start(3000) # 3 secs
        self.update_incorrect_guesses_label()
        self.clear_text_box()

    ## Switches to end screen & resets mainscreen
    def go_to_end(self):
        self.parent().setCurrentIndex(1)  # Switch to End Screen
        self.reset_mainscreen()

    ## Resets mainscreen before new game
    def reset_mainscreen(self):
        self.hangman_game.reset_hangman()
        self.update_hangman_image()
        self.disable_keyboard(self.btns_array)
        self.reset_keyboard_btn_colors()
        self.update_incorrect_guesses_label()
        self.set_game_progress_widget()
        
        # Hides the progress boxes before selecting new level
        for box in self.game_progress_boxes:
            box.hide()
        
    ### END OF METHODS RELATED TO EXECUTION OF THE HANGMAN GAME ###


    ### ACCESSIBILITY METHODS ###
    
    ## Theme customization
    # Apply similar styles to other widgets as needed (like keyboard buttons and progress boxes)
    def apply_theme(self, theme):
        self.main_window.reset_timer_signal.emit()
        self.current_theme = theme
        self.main_window.apply_background(theme["background"])
        self.end_screen.apply_theme(theme)
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text']};")
        
        # button styles
        button_style = f"""
        QPushButton {{
            background-color: {theme['button']}; 
            color: {theme['button_text']}; 
            border: 1px solid {theme['button_border']}; 
            border-radius: 7px; 
            padding: 3px 7px;
        }} 
        QPushButton:disabled {{
            background-color: {theme['disabled_btn_background']}; 
            color: {theme['disabled_btn_text']}; 
            border: 1px solid {theme['button_border']}; 
            border-radius: 7px;
        }}
        QPushButton:hover {{
            background-color: {theme['button_hover']};
            color: {theme['button_hover_text']};
        }}
        """
        
        self.easy_btn.setStyleSheet(button_style)
        self.medium_btn.setStyleSheet(button_style)
        self.hard_btn.setStyleSheet(button_style)
        self.incorrect_guesses_label.setStyleSheet(f"color: {theme['text']};")

        # text box styles
        self.guess_text_box.setStyleSheet(f"color: {theme['guess_text']}; background-color: {theme['guess_background']};")
        if self.game_progress_boxes:
            theme = self.current_theme
            for box in self.game_progress_boxes:
                box.setStyleSheet(f"color: {theme['guess_text']}; background-color: {theme['guess_background']};")

        for row in self.keyboard_btns:
            for btn in row:
                if self.hangman_game.is_the_game_over != None and not btn.isEnabled():
                    if btn.text() in self.hangman_game.correct_char_guesses or btn.text() in self.hangman_game.incorrect_char_guesses:
                        if btn.text() in self.hangman_game.correct_char_guesses:
                            self.change_keyboard_btn_color_based_on_guess(btn, True)
                        else:
                            self.change_keyboard_btn_color_based_on_guess(btn, False) 
                else:
                    btn.setStyleSheet(button_style)

    def change_font_family(self, font_family):
        self.current_font_family = font_family
        self.update_fonts()

    def change_font_size(self, size):
        self.current_font_size = size
        self.update_fonts()

    # Your existing methods remain the same...
    # When creating new widgets, add the current font:
    def update_fonts(self):
        self.main_window.reset_timer_signal.emit()
        new_font = QFont(self.current_font_family, self.current_font_size)
        
        # Update difficulty buttons
        if self.easy_btn:
            self.easy_btn.setFont(new_font)
        if self.medium_btn:
            self.medium_btn.setFont(new_font)
        if self.hard_btn:
            self.hard_btn.setFont(new_font)

        # Update incorrect gueses label
        if self.incorrect_guesses_label:
            self.incorrect_guesses_label.setFont(new_font)
        
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

    ### END OF ACCESSIBILITY METHODS ###
    
# Set up ending screen
class EndScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("End Screen!")
        button = QPushButton("Play Again")
        button.clicked.connect(self.go_to_main)
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)
        self.main_window = main_window

    def go_to_main(self):
        self.main_window.reset_timer_signal.emit()
        self.parent().setCurrentIndex(0)  # Switch to Main Screen
    
    def apply_theme(self, theme):
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text']};")

# Set up main window
class MainWindow(QWidget):
    reset_timer_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman")
        self.setWindowIcon(QIcon(str(Path("../assets/stick.png").resolve()))) 
        
        # Create stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        
        # Timer to consistently check the input queue
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.process_inputs)
        self.queue_timer.start(100)
        

        # Timer for idle feedback
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.speak_idle_message)
        self.reset_timer_signal.connect(self.reset_idle_timer)
        self.reset_idle_timer()
        
        # worker thread to always listen to input in the background.
        self.voice_input_thread = None
        # threading event to halt voice input thread. helps with overall synchronization.
        hangman_game_process_guess_event = threading.Event()

        
        self.hangman_game = Hangman()
        self.input_queue = queue.Queue()
        self.audio_accessibility = AudioAccessibility(self.hangman_game, self, hangman_game_process_guess_event)
        self.audio_accessibility.quit_game_signal.connect(QApplication.instance().quit)
        
        # Create screens
        self.end_screen = EndScreen(self)
        self.main_screen = MainScreen(
            self, 
            self.end_screen, 
            self.hangman_game, 
            self.audio_accessibility,
            hangman_game_process_guess_event
        )
        self.audio_accessibility.setMS(self.main_screen)

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.end_screen)

        # Set the initial screen
        self.stacked_widget.setCurrentIndex(0)  # Start on Screen 1

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)
    
    def apply_background(self, color):
        self.setStyleSheet(f"background-color: {color};")
    
    # function to process guesses via voice command    
    def process_inputs(self):
        while not self.input_queue.empty():
            guess = self.input_queue.get()
            self.main_screen.process_guess(guess)

    # function to reset the idle timer
    def reset_idle_timer(self):
        self.idle_timer.start(35000)

    # function to speak message when user has been idle
    def speak_idle_message(self):
        self.idle_timer.stop()
        threading.Thread(target=self.audio_accessibility.idle_message, daemon=True).start()

    # function to start game via voice command
    @pyqtSlot(int) 
    def start_game_from_audio(self, difficulty_level):
        self.main_screen.start_game(difficulty_level)
    
    # function to start listening thread
    def start_listening(self):
        self.voice_input_thread = threading.Thread(target=self.audio_accessibility.voice_input_listener, daemon=True)
        self.voice_input_thread.start()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.audio_accessibility.application_greeting()
    window.start_listening()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()