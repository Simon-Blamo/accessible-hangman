from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtTextToSpeech import QTextToSpeech
from audio_accessibility import AudioAccessibility
from pathlib import Path
import sys
import queue
import threading

from hangman import Hangman
from theme import Theme
from word_grade_classifier import WordGradeClassifier
from accessible_word_list_dialog import AccessibleWordListDialog
from word_lists import WordLists

# Command List Screen - lists all commands for reference
class CommandScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Command List")
        self.setGeometry(100,100,450,550)
        self.title_label = QLabel("Speech Commands")
        self.title_label.setStyleSheet("font-weight: bold;")
        self.commands_list = QTextEdit()
        self.commands_list.setReadOnly(True)
        self.commands_list.setHtml("""
            <b>Starting Game Commands</b><br>
            "START GAME"<br>
            "EASY"<br>
            "MEDIUM"<br>
            "HARD"<br>
                                   
            <br><b>Game Features</b><br>
            "LETTER _"<br>
            "NUMBER OF CHANCES LEFT"<br>
            "LIST INCORRECT LETTERS/CHARACTERS"<br>
            "LIST CORRECT LETTERS/CHARACTERS"<br>
            "HANGMAN STATUS"<br>
            "WORD STATUS"<br>
                                   
            <br><b>Customization</b><br>
            <b>Themes:</b> <br>
            1. "COLOR THEME" <br>
            2. "LIGHT", "DARK", "CONTRAST", "BLUE", "YELLOW",
            "RED", "GREEN", "MONOCHROMATIC"<br><br>
            
            <b>Font Families:</b> <br>
            1. "FONT FAMILY" <br>
            2. "ARIAL", "ARIEL", "COMIC", "OPEN", "DYSELXIC"<br><br>
            
            <b>Font Sizes:</b> <br>                       
            1. "FONT SIZE" <br>
            2. "8", "10", "12", "14", "16", "18", "20"<br>
                                   
            <br><b>Help Commands</b><br>
            "HELP OBJECTIVE"<br>
            "HELP GAMEPLAY"<br>
            "HELP LIST COMMANDS"<br>
            "HELP DIFFICULTY LEVELS"<br>   
            "HELP SETTINGS"<br>                     
                                   
            <br><b>Other Commands</b><br>
            "PLAY AGAIN" Restart the game after it ends<br>
            "EXIT", "QUIT", "QUIT GAME" Exit the game<br>
        """)
        self.commands_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout = QVBoxLayout()
        title_layout = QVBoxLayout()
        title_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_group = QGroupBox()
        title_group.setObjectName("title_group")
        title_group.setStyleSheet("""
            QGroupBox#title_group {
                border: 2px solid black; /* Black border */
                border-radius: 5px;     /* Rounded corners */
                margin-top: 10px;       /* Space for the title */
            }
        """)
        title_group.setLayout(title_layout)

        command_layout = QVBoxLayout()
        command_layout.addWidget(self.commands_list)
        command_group = QGroupBox("Command List")
        command_group.setObjectName("command_group")
        command_group.setStyleSheet("""
            QGroupBox#command_group {
                font-weight: bold;     /* Bold text */
                border: 2px solid black; /* Black border */
                border-radius: 5px;     /* Rounded corners */
                margin-top: 10px;       /* Space for the title */
            }
            QGroupBox#command_group::title {
                subcontrol-origin: margin;
                subcontrol-position: top center; /* Center the title */
                padding: 0 3px;                  /* Add padding around the title */
                color: black;                    /* Black text for the title */
            }
        """)
        command_group.setLayout(command_layout)
        
        layout.addWidget(title_group)
        layout.addWidget(command_group)
        self.setLayout(layout)
        
    def apply_theme(self, theme):
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text']};")

    def apply_font(self, font):
        title_font = QFont(font.family(), font.pointSize() + 4)
        self.title_label.setFont(title_font)

        group_font = QFont(font.family(), font.pointSize() + 2)
        self.findChild(QGroupBox, "command_group").setFont(group_font)

        self.commands_list.setFont(font)

# Switch to Main Screen
class MainScreen(QWidget):
    #region INTIALIZATION - sets up class
    def __init__(self, main_window, end_screen, hangman_game, audio_accessibility, thread_event):
        super().__init__()
        self.main_window = main_window
        self.end_screen = end_screen
        self.hangman_game: Hangman = hangman_game              # Initializes hangman object.
        self.audio_accessibility = audio_accessibility
        self.thread_event = thread_event
        self.game_mode_menu = None
        self.grade_menu = None
        self.sound_menu_action = None
        self.difficulty_mode_action = None
        self.grade_mode_action = None
        self.grade_level_menu = None
        self.word_lists = WordLists()
        self.speech = QTextToSpeech()
        self.grade_levels = self.word_lists.grade_levels
        self.current_grade = None
        self.learning_mode = False
 
        # Initialize font settings
        self.current_font_family = "Arial"
        self.current_font_size = 12

        # attribute that stores key elements
        self.menu_bar = None
        self.current_theme = Theme.LIGHT_MODE
        self.easy_btn: QPushButton = None                   # Easy level button
        self.medium_btn: QPushButton = None                 # Medium level button
        self.hard_btn: QPushButton = None                   # Hard level button
        self.incorrect_guesses_label: QLabel = None         # lists incorrect guesses
        self.num_chances_label: QLabel = None               # states how many chances left
        self.guess_text_box: QLineEdit = None               # text box for users to guess with
        self.keyboard_btns: list[list[QPushButton]] = None  # list of lists contains buttons found on on-screen keyboard
        self.guess_btn: QPushButton = None                  # button that locks in character guess
        self.default_colors: dict[str, str] = {}            # holds default colors of elements to be used later on
        self.game_progress_boxes: list[QLineEdit] = None    # text boxes which showcase the progress of the current word

        # Set element layouts
        page_layout = QVBoxLayout()                         # layout for entire window app. It's basically a base that contains everything else within the app
        difficulty_btn_layout = QHBoxLayout()               # layout for difficulty buttons
        self.game_progress_layout = QHBoxLayout()           # layout for word progress
        incorrect_guesses_layout = QHBoxLayout()            # layout for incorrect guesses
        num_chances_layout  = QHBoxLayout()                 # layout for number of chances
        image_layout = QHBoxLayout()                        # layout for hangman
        input_layout = QHBoxLayout()                        # layout for guess text box
        keyboard_container_layout = QVBoxLayout()           # layout for keyboard
        keyboard_widget = None
        self.stacklayout = QStackedLayout()

        # Add element's layouts to page layout
        self.create_menu_bar(page_layout)                   
        page_layout.addLayout(difficulty_btn_layout)
        page_layout.addLayout(incorrect_guesses_layout)
        page_layout.addLayout(num_chances_layout)
        page_layout.addLayout(image_layout)
        page_layout.addLayout(self.game_progress_layout)
        page_layout.addLayout(input_layout)
        page_layout.addLayout(keyboard_container_layout)
        page_layout.addLayout(self.stacklayout)
        
        # Creates additional elements
        self.init_difficulty_btns(difficulty_btn_layout)    # creating/rendering buttons
        self.init_incorrect_guesses_widget(incorrect_guesses_layout)
        self.init_num_chances_widget(num_chances_layout)
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
    #endregion
    
    #region MENU BAR
    def create_menu_bar(self, page_layout): # Creates menu bar
        self.menu_bar = QMenuBar(self)
        self.init_command_menu()
        self.init_game_mode_menu()
        self.init_grade_level_menu()
        self.init_learning_menu()
        self.init_word_menu()
        self.init_settings_menu()
        self.init_help_menu()
        page_layout.setMenuBar(self.menu_bar)

    def init_command_menu(self):
        command_menu = QMenu("Commands", self)
        self.menu_bar.addMenu(command_menu)

        open_command_list_action = QAction("Open Command List", self)
        self.command_window = CommandScreen() #creates command screen
        open_command_list_action.triggered.connect(self.open_command_list)
        command_menu.addAction(open_command_list_action)
        
    def open_command_list(self):
        self.command_window.show()

    def init_game_mode_menu(self): # Creates game mode options
        # Game Mode Menu
        self.game_mode_menu = QMenu("Game Mode", self)
        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)
        self.menu_bar.addMenu(self.game_mode_menu)  # Add the menu to the menu bar
        
        # Create and add difficulty mode action
        self.difficulty_mode = QAction("Difficulty Mode", self, checkable=True)
        self.difficulty_mode.setChecked(True)
        self.difficulty_mode.triggered.connect(lambda checked: self.change_game_mode("difficulty"))
        mode_group.addAction(self.difficulty_mode)
        self.game_mode_menu.addAction(self.difficulty_mode)  # Add action to the menu, not to itself
        
        # Create and add grade mode action
        self.grade_mode = QAction("Grade Level Mode", self, checkable=True)
        self.grade_mode.triggered.connect(lambda checked: self.change_game_mode("grade"))
        mode_group.addAction(self.grade_mode)
        self.game_mode_menu.addAction(self.grade_mode)  # Add action to the menu

    def init_grade_level_menu(self): # Creates grade level menu options
        # Grade Level Menu (initially disabled)
        self.grade_level_menu = QMenu("Grade Level", self)
        self.menu_bar.addMenu(self.grade_level_menu)
        grade_group = QActionGroup(self)
        grade_group.setExclusive(True)
        
        grades = ['K'] + [str(i) for i in range(1, 13)]
        for grade in grades:
            action = QAction(f"Grade {grade}", self, checkable=True)
            if grade == self.current_grade:
                action.setChecked(True)
            action.triggered.connect(lambda checked, g=grade: self.change_grade_level(g))
            grade_group.addAction(action)
            self.grade_level_menu.addAction(action)    

    def init_learning_menu(self): # Creates learning mode menu options
        # Learning Mode Menu
        learning_menu = QMenu("Learning Menu", self)
        self.menu_bar.addMenu(learning_menu)
        self.learning_mode_action = QAction("Enable Learning Mode", self, checkable=True)
        self.learning_mode_action.triggered.connect(self.toggle_learning_mode)
        learning_menu.addAction(self.learning_mode_action)
    
    def init_word_menu(self): # Creates custom word list menu options
        # Word Lists Menu
        word_list_menu = QMenu("Word Lists", self)
        self.menu_bar.addMenu(word_list_menu)
        manage_words_action = QAction("Manage Custom Words", self)
        manage_words_action.triggered.connect(self.show_word_list_dialog)
        word_list_menu.addAction(manage_words_action)

    def init_settings_menu(self):
        settings_menu = QMenu("Settings", self)
        self.menu_bar.addMenu(settings_menu)
        
        # Creates individual menus
        self.init_sound_menu(settings_menu)
        self.init_font_menu(settings_menu)
        self.init_theme_menu(settings_menu)

    def init_font_menu(self, settings_menu): # Creates font menu options
        # Font Settings Menu
        font_setting_menu = QMenu("Font Settings", self)
        settings_menu.addMenu(font_setting_menu)
        
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

        # set fonts in command window
        new_font = QFont(self.current_font_family, self.current_font_size)
        self.command_window.apply_font(new_font)

    def init_theme_menu(self, settings_menu): # Creates theme menu options
        # Theme Menu
        themes_menu = QMenu("Themes", self)
        settings_menu.addMenu(themes_menu)
        
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
            themes_menu.addAction(action)

    def init_sound_menu(self, settings_menu): # Creates sound menu option
        sound_menu = QMenu("Sound Settings \U0001F3A4", self)
        settings_menu.addMenu(sound_menu)
    
        sound_action = QAction("Voice Input ON", self, checkable=True)
        sound_action.setChecked(True)  # Start with sound on by default
        sound_action.triggered.connect(self.audio_accessibility.update_voice_input_settings)
        self.sound_menu_action = sound_action
        sound_menu.addAction(sound_action)
    
    def init_help_menu(self): # Creates help meny options
        other_menu = QMenu("Help", self)
        self.menu_bar.addMenu(other_menu)
        
        help_action = QAction("General Overview", self)
        help_action.triggered.connect(self.display_help_dialog_box)
        other_menu.addAction(help_action) 

    def display_help_dialog_box(self): # Creates general overview guide
        was_voice_input_active = self.main_window.audio_accessibility.voice_input_turned_on
        if was_voice_input_active:
            self.main_window.audio_accessibility.pause_voice_input()  # Pause if already active

        dlg = QDialog(self)
        dlg.setWindowTitle("Help")
        dlg.setMinimumSize(600, 700)

        # main layout for the dialog
        layout = QVBoxLayout(dlg)

        # scrollable area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)  # Add spacing between sections

       # add help sections to the scroll content
        sections = [
            ("Objective", "Guess the hidden word one letter at a time. You have a limited number of incorrect guesses before the game ends."),
            ("Basic Gameplay", """
            <ul>
                <li>You can use the on-screen keyboard, voice input, or type letters to make guesses.</li>
                <li>Correct guesses will reveal the letters in the word.</li>
                <li>Incorrect guesses will be tracked, and the hangman drawing will progress.</li>
            </ul>
            """),
            ("Speech Commands", """
            <ul>
                <li><strong>START GAME:</strong> Start a new game.</li>
                <li><strong>START GAME EASY:</strong> Start a new game in Easy mode.</li>
                <li><strong>START GAME MEDIUM :</strong> Start a new game in Medium mode.</li>
                <li><strong>START GAME HARD :</strong> Start a new game in Hard mode.</li>
                <li>
                    <strong>CHANGE THEME:</strong> Adjust the display settings by choosing one of the following themes:
                    <div style="margin-left: 20px;">
                        <div><strong>LIGHT MODE:</strong> For brighter lighting</div>
                        <div><strong>DARK MODE:</strong> For lower lighting</div>
                        <div><strong>CCONTRAST MODE:</strong> Black and White </div>
                        <div><strong>BLUE AND YELLOW MODE:</strong> For users with Tritanomaly & Tritanopia</div>
                        <div><strong>RED AND GREEN MODE:</strong> For users with Protanomaly, Protanopia & Deuteranopia </div>
                        <div><strong>MONOCHROMATIC MODE:</strong> For users with complete color blindness</div>
                    </div>
                </li>
                <li>
                    <strong>CHANGE FONT FAMILY:</strong> Adjust the text appearance by choosing one of the following font styles:
                    <div style="margin-left: 20px;">
                        <div><strong>ARIAL</strong></div>
                        <div><strong>COMIC SANS</strong></div>
                        <div><strong>OPENDYSLEXIC</strong></div>
                    </div>
                </li>
                <li>
                    <strong>CHANGE FONT SIZE:</strong> Adjust the text size for better readability by choosing one of the following options:
                    <div style="margin-left: 20px;">
                        <div><strong>8</strong></div>
                        <div><strong>10</strong></div>
                        <div><strong>12</strong></div>
                        <div><strong>14</strong></div>
                        <div><strong>16</strong></div>
                        <div><strong>18</strong></div>
                        <div><strong>20</strong></div>
                    </div>
                </li>
                <li><strong>EXIT or QUIT:</strong> Exit the game.</li>
                <li><strong>LIST INCORRECT GUESSES:</strong> Hear the letters you have guessed incorrectly.</li>
                <li><strong>LIST CORRECT LETTERS:</strong> Hear the letters you have guessed correctly.</li>
                <li><strong>HANGMAN STATUS:</strong> Hear the current status of the hangman drawing.</li>
                <li><strong>WORD STATUS:</strong> Hear the current state of the hidden word.</li>
                <li><strong>PLAY AGAIN:</strong> Restart the game after it ends.</li>
                <li><strong>GUESS _:</strong> Guess a specific letter, for example, ' '"Guess A".</li>
                <li><strong>HELP OBJECTIVE:</strong> Learn about the game's main goal and how to succeed.</li>
                <li><strong>HELP GAMEPLAY:</strong> Get a detailed explanation of how to play the game.</li>
                <li><strong>HELP LIST COMMANDS:</strong> Discover all available voice commands for smoother gameplay.</li>
                <li><strong>HELP DIFFICULTY LEVELS:</strong> Understand the different difficulty levels and their grade-based word selections.</li>
                <li><strong>HELP SETTINGS:</strong> Explore customization options for themes, fonts, and accessibility settings.</li>

            </ul>
            """),
            ("Difficulty Levels", """
            <p><strong>Difficulty Mode:</strong> Select a difficulty level (Easy, Medium, Hard) to play with words tailored to that level.</p>

            <p>The difficulty levels correspond to the following grade levels:</p>
            <ul>
                <li><strong>Easy:</strong> Kindergarten to Grade 4 words.</li>
                <li><strong>Medium:</strong> Grade 5 to Grade 8 words.</li>
                <li><strong>Hard:</strong> Grade 9 to Grade 12 words.</li>
            </ul>
            <p><strong>Grade Levels:</strong> Choose a grade level (K-12) to play with words suited to that level</p>
            <p><strong>Learning Mode:</strong> Enhance your learning experience by hearing letters and their associated words as you choose them.</p>
            """),
            ("Settings", """
            <p>Customize your gameplay experience:</p>
            <ul>
                <li><strong>Word Lists:</strong> Create custom word lists for the game, with each word graded based on its complexity.</li>
                <li><strong>Sound Settings:</strong> Turn Voice Input On/Off for accessibility.</li>
                <li><strong>Theme Settings:</strong> Change the game's color theme for accessibility.</li>
                <li><strong>Font Settings:</strong> Adjust the font style and size.</li>
            </ul>
            """),
        ]
        for title, content in sections:
            self.add_help_section(scroll_layout, title, content)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dlg.accept)
        layout.addWidget(close_button)
        dlg.setLayout(layout)
        dlg.exec()

        if was_voice_input_active:
            self.main_window.audio_accessibility.resume_voice_input()  # Resume if it was active

    def add_help_section(self, layout, title, content):
        # create a button to act as a section header
        section_button = QPushButton(title)
        section_button.setCheckable(True)
        section_button.setStyleSheet("""
            QPushButton {
                border: 3px solid #444; 
                font-weight: bold; 
                text-align: center;
                padding: 8px;
                font-size: 15px;
            }
            QPushButton:checked {
            }
        """)
        #create collapsible frame for the content
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame.setFrameShadow(QFrame.Shadow.Plain)
        frame.setStyleSheet(" border: 1px solid #ccc; padding: 7px;")
        frame.setVisible(False)

        # add content to the frame
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(10, 5, 10, 5)

        label = QLabel(content)
        label.setWordWrap(True)
        frame_layout.addWidget(label)
        frame.setLayout(frame_layout)

        # toggle visibility of the frame when the button is clicked
        section_button.toggled.connect(frame.setVisible)

        # add button and frame to the layout
        layout.addWidget(section_button)
        layout.addWidget(frame)

    def change_grade_level(self, grade):
        """Change the current grade level and update word list."""
        self.current_grade = grade
        if self.game_mode == "grade":
            # Set grade text first so it's available for all conditions
            grade_text = "Kindergarten" if grade == 'K' else f"Grade {grade}"
            
            # Get words for the selected grade
            words = list(self.word_lists.get_words_by_grade(grade))
            
            if words:
                # Update the hangman game's word list
                self.hangman_game.set_word_list(words)
                # Show feedback
                QMessageBox.information(self, "Grade Level Changed", 
                    f"Changed to {grade_text} words\nWord list size: {len(words)} words")
                # Start a new game with the updated word list
                self.start_game(0)
            else:
                QMessageBox.warning(self, "No Words Available", 
                    f"No words available for {grade_text}. Please select a different grade level.")
    
    def change_game_mode(self, mode):
        """Switch between difficulty-based and grade-based modes."""
        print(f"Changing game mode to: {mode}")  # Debug print
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
            self.grade_level_menu.setEnabled(False)
            # Reset to default word list
            self.hangman_game.reset_word_list()
        else:  # grade mode
            print("Entering grade mode")  # Debug print
            # Hide difficulty buttons, show grade selector
            self.easy_btn.hide()
            self.medium_btn.hide()
            self.hard_btn.hide()
            # Enable grade menu actions
            self.grade_level_menu.setEnabled(True)
            # Set initial grade if none selected
            if self.current_grade is None:
                print("Setting initial grade to K")  # Debug print
                self.change_grade_level('K')

    def change_grade_level(self, grade):
        """Change the current grade level and update word list."""
        print(f"Attempting to change to grade level: {grade}")  # Debug print
        
        # Always define grade_text at the start
        grade_text = "Kindergarten" if grade == 'K' else f"Grade {grade}"
        print(f"Grade text set to: {grade_text}")  # Debug print
        
        # Set the current grade
        self.current_grade = grade
        
        # Check if we're in grade mode
        if getattr(self, 'game_mode', None) != "grade":
            print("Not in grade mode, ignoring grade change")  # Debug print
            return
        
        try:
            # Get words for the selected grade
            words = list(self.word_lists.get_words_by_grade(grade))
            print(f"Found {len(words)} words for {grade_text}")  # Debug print
            
            if words:
                print(f"Sample words: {words[:5]}")  # Debug print first 5 words
                # Update the hangman game's word list
                self.hangman_game.set_word_list(words)
                # Show feedback
                QMessageBox.information(self, "Grade Level Changed", 
                    f"Changed to {grade_text} words\nWord list size: {len(words)} words")
                # Start a new game with the updated word list
                self.start_game(0)
            else:
                print(f"No words found for {grade_text}")  # Debug print
                QMessageBox.warning(self, "No Words Available", 
                    f"No words available for {grade_text}. Please select a different grade level.")
        except Exception as e:
            print(f"Error changing grade level: {str(e)}")  # Debug print
            QMessageBox.warning(self, "Error", 
                f"An error occurred while changing to {grade_text}. Please try again.")
    #endregion

    #region CREATES & SETS QWIDGETS
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

    # Sets up word list by grade level
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
                lambda: (
                    self.word_lists.remove_custom_word(
                        dialog.list_widget.currentItem().text().split(' (Grade')[0]
                    ),
                    dialog.list_widget.takeItem(dialog.list_widget.row(dialog.list_widget.currentItem()))
                )
            )
            dialog.close_button.clicked.connect(dialog.accept)
            
            dialog.exec()

    def add_custom_word(self, word, grade, list_widget):
        if word:
            self.word_lists.add_custom_word(word)
            item = QListWidgetItem(f"{word} (Grade {grade})")
            list_widget.addItem(item)

    # Lists letters gussed incorrectly
    def init_incorrect_guesses_widget(self, incorrect_guesses_layout):
        font = QFont(self.current_font_family, self.current_font_size)
        font.setBold(True)
        incorrect_guesses_label = QLabel("Wrong Guesses:  ")
        incorrect_guesses_label.setFixedWidth(500)
        incorrect_guesses_label.setFont(font)
        self.incorrect_guesses_label = incorrect_guesses_label
        incorrect_guesses_layout.addWidget(incorrect_guesses_label)

    def init_num_chances_widget(self, num_chances_layout):
        font = QFont(self.current_font_family, self.current_font_size)
        font.setBold(True)
        num_chances_label = QLabel("Chances Left:  ")
        num_chances_label.setFixedWidth(500)
        num_chances_label.setFont(font)
        self.num_chances_label = num_chances_label
        num_chances_layout.addWidget(num_chances_label)

    # Sets up first hangman image
    def init_hangman_image(self, image_layout):
        self.label = QLabel(self)
        self.pixmap = QPixmap('../assets/sticks/default/Hangman0.png').scaled(128, 192)
        self.label.setPixmap(self.pixmap)
        self.resize(self.pixmap.width(), self.pixmap.height())
        image_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

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
        self.guess_text_box.textChanged.connect(self.disable_guess_btn)

        self.disable_textbox(self.guess_text_box, True)
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
            btn.pressed.connect(lambda char=char:self.update_guess_text_box(char, self.guess_text_box))
            keyboard_row_1_layout.addWidget(btn)
        
        for char in keyboard_row_2_chars:
            btn = QPushButton(char)
            keyboard_row_2_btns.append(btn)
            btn.pressed.connect(lambda char=char:self.update_guess_text_box(char, self.guess_text_box))
            keyboard_row_2_layout.addWidget(btn)

        for char in keyboard_row_3_chars:
            btn = QPushButton(char)
            keyboard_row_3_btns.append(btn)
            btn.pressed.connect(lambda char=char:self.update_guess_text_box(char, self.guess_text_box))
            keyboard_row_3_layout.addWidget(btn)

        btn = QPushButton(keyboard_row_4_word)
        keyboard_row_4_btns.append(btn)
        btn.pressed.connect(lambda:self.process_guess(self.guess_text_box.text().upper()))
        keyboard_row_4_layout.addWidget(btn)
        self.guess_btn = btn

        self.btns_array.append(keyboard_row_1_btns)
        self.btns_array.append(keyboard_row_2_btns)
        self.btns_array.append(keyboard_row_3_btns)
        self.btns_array.append(keyboard_row_4_btns)

        self.disable_keyboard(self.btns_array, True)

        keyboard_layout.addLayout(keyboard_row_1_layout)
        keyboard_layout.addLayout(keyboard_row_2_layout)
        keyboard_layout.addLayout(keyboard_row_3_layout)
        keyboard_layout.addLayout(keyboard_row_4_layout)
        keyboard_widget.setLayout(keyboard_layout)
        keyboard_widget.setFixedWidth(500)

        return [keyboard_widget, self.btns_array]
    #endregion
    
    #region UPDATES QWIDGETS - hangman pic & incorrect guess list
    # incorrect guesses label element
    def update_incorrect_guesses_label(self):
        label = "Wrong Guesses:  "
        incorrect_chars = ""
        for char in self.hangman_game.incorrect_char_guesses:
            incorrect_chars += char + "  "
        self.incorrect_guesses_label.setText(label + incorrect_chars)
    
    # number of chances label element
    def update_num_chances_label(self, reset):
        label = "Chances Left:  "
        num_chances = self.hangman_game.num_of_chances
        if num_chances == 11 and reset:
            self.num_chances_label.setText(label)
        else:
            self.num_chances_label.setText(label + str(num_chances))

    # Updates hangman image when guess incorrectly
    def update_hangman_image(self):
        num_wrong_guesses = self.hangman_game.number_of_wrong_guesses
        theme = self.current_theme
        pixmap_path = f'../assets/sticks/default/Hangman{num_wrong_guesses}.png'
        
        # Changes path based on current theme
        if theme["mode"] == "blue_yellow":
            pixmap_path = f'../assets/sticks/blueyellow/Hangman{num_wrong_guesses}.png'
        elif theme["mode"] == "red_green" and num_wrong_guesses > 9:
            pixmap_path = f'../assets/sticks/redgreen/Hangman{num_wrong_guesses}.png'

        self.pixmap = QPixmap(pixmap_path).scaled(128, 192)
        self.label.setPixmap(self.pixmap)
    
    def clear_game_progress_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    #endregion

    #region UPDATES TEXTBOX - disable/enable textbox or guess button
    ## text box
    def disable_textbox(self, text_box, condition):
        text_box.setDisabled(condition)

    def disable_guess_btn(self):
        char_in_text_box = self.guess_text_box.text().upper()
        if char_in_text_box in self.hangman_game.correct_char_guesses or char_in_text_box in self.hangman_game.incorrect_char_guesses:
            self.guess_btn.setDisabled(True)
        elif self.hangman_game.is_the_game_over == False:
            self.guess_btn.setDisabled(False)
    #endregion

    #region KEYBOARD - disable/enable, find button
    def disable_keyboard(self, keyboard_btns, condition):
        for keyboard_row in keyboard_btns:
            for btn in keyboard_row:
                btn.setDisabled(condition)

    def find_keyboard_btn(self, keyboard_btn_text):
        for row in self.keyboard_btns:
            for keyboard_btn in row:
                if keyboard_btn.text() == keyboard_btn_text:
                    return keyboard_btn
    #endregion

    #region SET THEMES - set disabled background & text, reset keyboard colors
    def get_default_disabled_colors(self):
        self.default_colors["disabled_btn_background"] = 'WhiteSmoke'
        self.default_colors["disabled_btn_text"] = 'LightGrey'

    def reset_keyboard_btn_colors(self):
        self.apply_theme(self.current_theme)
    #endregion

    #region KEYBOARD - colors & keypress
    def update_keyboard_btn_color(self, keyboard_btn, the_guess_was_correct):
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
    #endregion
    
    #region TEXTBOX - updates letter in text box based on selected keyboard button
    def update_guess_text_box(self, char, text_box):
        self.main_window.reset_timer_signal.emit()
        backspace = '\u232B'
        if char != backspace:
            text_box.setText(char)
            if self.learning_mode:
                self.speak_letter(char)
        else:
            text_box.clear()
    #endregion
    
    #region DIFFICULTY BUTTONS TAB ORDER
    def set_tab_order(self):
        self.setTabOrder(self.easy_btn, self.medium_btn)
        self.setTabOrder(self.medium_btn, self.hard_btn)
        self.setTabOrder(self.hard_btn, self.guess_text_box)
        self.setTabOrder(self.guess_text_box, self.guess_btn)
    #endregion

    #region GAME EXECUTION/ENGINE - executes hangman game
    # Starts game by setting up hangman
    def start_game(self, difficulty):
        self.hangman_game.reset_hangman()
        self.reset_keyboard_btn_colors()
        self.hangman_game.set_current_word(difficulty)
        self.update_incorrect_guesses_label()
        self.update_num_chances_label(False)
        self.apply_theme(self.current_theme)
        print(self.hangman_game.get_current_word())
        self.disable_keyboard(self.keyboard_btns, False)
        self.disable_textbox(self.guess_text_box, False)
        self.update_game_progress_widget(True)
        self.audio_accessibility.update_game_is_ongoing(True)
    
    # Speaks letters in learning mode
    def speak_letter(self, letter):
        """Speak a letter aloud."""
        if self.learning_mode:
            self.speech.say(letter)
    
    # Speaks learning mode on/off status
    def toggle_learning_mode(self, enabled):
        """Toggle learning mode on/off."""
        self.learning_mode = enabled
        if enabled:
            # Announce that learning mode is enabled
            self.speech.say("Learning mode enabled")
        else:
            self.speech.say("Learning mode disabled")
    
    # Speaks current guessed word in learning mode
    def speak_word(self, word):
            """Speak a word aloud."""
            if self.learning_mode:
                # Small delay before speaking the word
                QTimer.singleShot(500, lambda: self.speech.say(word))
    
    # Updates word progress as user guesses
    def update_game_progress_widget(self, new_game):
        if self.hangman_game.current_word != None:
            if new_game:
                self.clear_game_progress_layout(self.game_progress_layout)
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
            
                    self.disable_textbox(text_box, True)
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
        if self.learning_mode:
            self.speak_letter(input)
        the_guess_was_correct = self.hangman_game.process_guess(input)
        btn_pressed = self.find_keyboard_btn(input)
        btn_pressed.setDisabled(True)
        self.update_keyboard_btn_color(btn_pressed, the_guess_was_correct)
        if the_guess_was_correct:
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
        self.thread_event.set()
        if self.hangman_game.is_the_game_over:
            self.audio_accessibility.update_game_is_ongoing(False)
            self.disable_keyboard(self.keyboard_btns, True)
            self.disable_textbox(self.guess_text_box, True)
            self.get_default_disabled_colors()

            # update endscreen data, fonts, & theme
            font = QFont(self.current_font_family, self.current_font_size)
            self.end_screen.update_end_screen(self.hangman_game, font)
            self.end_screen.apply_theme(self.current_theme)
        
            # Wait before going to next screen to see hangman image & word progress update
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self.go_to_end)
            timer.start(3000) # 3 secs
        self.update_incorrect_guesses_label()
        self.update_num_chances_label(False)
        self.guess_text_box.setText("") #clear textbox

    ## Switches to end screen & resets mainscreen
    def go_to_end(self):
        self.parent().setCurrentIndex(1)  # Switch to End Screen
        self.reset_mainscreen()

    ## Resets mainscreen before new game
    def reset_mainscreen(self):
        self.hangman_game.reset_hangman()
        self.update_hangman_image()
        self.disable_keyboard(self.btns_array, True)
        self.reset_keyboard_btn_colors()
        self.update_incorrect_guesses_label()
        self.update_num_chances_label(True)
        self.set_game_progress_widget()
        
        # Hides the progress boxes before selecting new level
        for box in self.game_progress_boxes:
            box.hide()
    #endregion

    #region THEMES
    # Apply similar styles to other widgets as needed (like keyboard buttons and progress boxes)
    def apply_theme(self, theme):
        self.main_window.reset_timer_signal.emit()
        self.current_theme = theme
        self.main_window.apply_background(theme["background"])
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text']};")
        self.update_hangman_image()

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
        self.num_chances_label.setStyleSheet(f"color: {theme['text']};")

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
                            self.update_keyboard_btn_color(btn, True)
                        else:
                            self.update_keyboard_btn_color(btn, False) 
                else:
                    btn.setStyleSheet(button_style)

        # edit theme for command screen
        self.command_window.apply_theme(self.current_theme)
    #endregion

    #region FONTS
    def change_font_family(self, font_family):
        self.current_font_family = font_family
        self.update_fonts()

    def change_font_size(self, size):
        self.current_font_size = size
        self.update_fonts()

    # Your existing methods remain the same...When creating new widgets, add the current font:
    def update_fonts(self):
        self.main_window.reset_timer_signal.emit()
        new_font = QFont(self.current_font_family, self.current_font_size)
        
        # updates fonts for command window
        self.command_window.apply_font(new_font)
        
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
        
        # Updates number of chances label
        if self.num_chances_label:
            self.num_chances_label.setFont(new_font)

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
    #endregion
    
# Set up ending screen
class EndScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        # game info
        self.did_win = None
        self.word = None
        self.chances_left = None
        self.right_num_guesses = None
        self.wrong_num_guess = None
        self.word_guessed = None
        self.correct_letters = None
        self.incorrect_letters = None
        self.last_letter = None

        # Game Objects
        self.msg_label = QLabel("Game Over!")
        self.win_label = QLabel()
        self.word_label = QLabel()
        self.chances_left_label = QLabel()
        self.right_num_guesses_label = QLabel()
        self.wrong_num_guesses_label = QLabel()
        self.word_guessed_label = QLabel()
        self.correct_letters_label = QLabel()
        self.incorrect_letters_label = QLabel()
        self.last_letter_label = QLabel()
        self.play_button = QPushButton("Play Again")
        self.play_button.clicked.connect(self.go_to_main)
        self.game_won = None
        
        # Message layout
        end_layout = QVBoxLayout()
        msg_layout = QVBoxLayout()
        msg_layout.addWidget(self.msg_label, alignment=Qt.AlignmentFlag.AlignCenter)
        msg_group = QGroupBox()
        msg_group.setObjectName("msg_group")
        msg_group.setStyleSheet("""
            QGroupBox#msg_group {
                border: 2px solid black; /* Black border */
                border-radius: 5px;     /* Rounded corners */
                margin-top: 10px;       /* Space for the title */
            }
        """)
        msg_group.setLayout(msg_layout)

        # game info layout
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.win_label, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.word_label)
        info_layout.addWidget(self.word_guessed_label)
        info_layout.addWidget(self.chances_left_label)
        info_layout.addWidget(self.right_num_guesses_label)
        info_layout.addWidget(self.correct_letters_label)
        info_layout.addWidget(self.wrong_num_guesses_label)
        info_layout.addWidget(self.incorrect_letters_label)
        info_layout.addWidget(self.last_letter_label)

        info_group = QGroupBox("Game Summary")
        info_group.setObjectName("game_summary") # sets object name to be found later
        info_group.setStyleSheet("""
            QGroupBox#game_summary {
                border: 2px solid black; /* Black border */
                border-radius: 5px;     /* Rounded corners */
                margin-top: 10px;       /* Space for the title */
            }
            QGroupBox#game_summary::title {
                subcontrol-origin: margin;
                subcontrol-position: top center; /* Center the title */
                padding: 0 3px;                  /* Add padding around the title */
                color: black;                    /* Black text for the title */
            }
        """)
        info_group.setLayout(info_layout)

        # PLay button layout
        play_layout = QHBoxLayout()
        play_layout.addStretch()
        play_layout.addWidget(self.play_button)
        play_layout.addStretch()

        # Combine layouts
        end_layout.addWidget(msg_group)
        end_layout.addWidget(info_group)
        end_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        end_layout.addLayout(play_layout)

        self.setLayout(end_layout)
        self.main_window = main_window

    # updates info to screen
    def update_end_screen(self, game: Hangman, font):
        # set/save data
        self.game_won = game.did_you_win
        self.word = game.current_word
        self.chances_left = game.num_of_chances
        self.right_num_guesses = len(game.correct_char_guesses)
        self.wrong_num_guess = game.number_of_wrong_guesses
        self.word_guessed = " ".join(game.current_word_progress)
        self.correct_letters = " ".join(game.correct_char_guesses)
        self.incorrect_letters = " ".join(game.incorrect_char_guesses)
        self.last_letter = game.was_last_guess_correct

        # update labels
        if self.game_won:
            self.win_label.setText('You Won!')
        else:
            self.win_label.setText('You Lost!')
        self.word_label.setText('<b>Correct Word: </b>' + self.word)
        self.chances_left_label.setText('<b>Chances Left: </b>' + str(self.chances_left))
        self.right_num_guesses_label.setText('<b>Total Number of Correct Guesses: </b>' + str(self.right_num_guesses))
        self.wrong_num_guesses_label.setText('<b>Total Number of Incorrect Guesses: </b>' + str(self.wrong_num_guess))
        self.word_guessed_label.setText('<b>Word Progress: </b>' + self.word_guessed)
        self.correct_letters_label.setText('<b>Correct Letters Guessed: </b>' + self.correct_letters)
        self.incorrect_letters_label.setText('<b>Incorrect Letters Guessed: </b>' + self.incorrect_letters)
        self.last_letter_label.setText('<b> Was last letter correct: </b>' + str(self.last_letter))

        # Set larger font sizes for title/subtitles
        title_font = QFont(font.family(), font.pointSize() + 4)
        self.msg_label.setFont(title_font)
        group_font = QFont(font.family(), font.pointSize() + 2)
        self.findChild(QGroupBox, "game_summary").setFont(group_font)

        for widget in [
            self.win_label, self.word_label, self.right_num_guesses_label, self.wrong_num_guesses_label, self.chances_left_label,
            self.word_guessed_label, self.correct_letters_label, self.incorrect_letters_label, self.play_button, self.last_letter_label
        ]:
            widget.setFont(font)
        
    def go_to_main(self):
        self.main_window.reset_timer_signal.emit()
        self.parent().setCurrentIndex(0)  # Switch to Main Screen
    
    def apply_theme(self, theme):
        self.setStyleSheet(f"background-color: {theme['background']}; color: {theme['text']};")
        win_color = theme["win"] if self.game_won else theme["lose"]
        self.msg_label.setStyleSheet(f"""
            color: {win_color};
            font-weight: bold;     /* Bold text */
        """)
        self.win_label.setStyleSheet(f"""
            color: {win_color};
            font-weight: bold;     /* Bold text */
        """)
        
        # Update button styles, labels, etc.
        button_style = f"""
        QPushButton {{
            background-color: {theme['button']}; 
            color: {theme['button_text']}; 
            border: 1px solid {theme['button_border']}; 
            border-radius: 7px; 
            padding: 5px 10px;
        }}
        QPushButton:hover {{
            background-color: {theme['button_hover']}; 
            color: {theme['button_hover_text']};
        }}
        """
        self.play_button.setStyleSheet(button_style)

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
        if self.audio_accessibility.voice_input_turned_on:
            self.idle_timer.stop()
            threading.Thread(target=self.audio_accessibility.idle_message, daemon=True).start()

    # function to start game via voice command
    @pyqtSlot(int) 
    def start_game_from_audio(self, difficulty_level):
        self.main_screen.start_game(difficulty_level)

    def start_listening(self):
        self.audio_accessibility.start_voice_input_listener()

    # to be ran, when application closes
    def closeEvent(self, event):
        if self.audio_accessibility.voice_input_thread == None:
            exit()
        self.audio_accessibility.stop_voice_input_listener()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    user_choice = window.audio_accessibility.application_greeting()
    if user_choice:
        window.start_listening()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()