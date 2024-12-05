from PyQt6.QtCore import *
from hangman import Hangman
import threading
import time
import speech_recognition as sr
import pyttsx3
import difflib
import threading
import queue
from theme import Theme

# Handles audio acessibility: listens for voice commands and narrates audio feedback during gameplay
class AudioAccessibility(QObject):
    #region INITIALIZATION - sets up class
    start_game_signal = pyqtSignal(int)                         # signal to tell main window to start the hangman game.
    quit_game_signal  = pyqtSignal()                            # signal to tell main window to quit the process.
    apply_theme_signal = pyqtSignal(dict)                       # signal for theme change
    change_font_family_signal = pyqtSignal(str)                 # signal for font family
    change_font_size_signal = pyqtSignal(int)                   # signal for font size
    
    # intializes variables
    def __init__(self, hangman_game, main_window, thread_event):
        super().__init__()
        self.engine = pyttsx3.init()
        self.mic = sr.Microphone()
        self.recognizer = sr.Recognizer()
        self.voice_input_turned_on = True
        self.hangman_game: Hangman = hangman_game
        self.game_is_ongoing = hangman_game.is_the_game_over
        self.main_window = main_window
        self.commands: dict[list] = None
        self.input_queue = main_window.input_queue
        self.speak_queue = queue.Queue()
        self.start_game_signal.connect(self.main_window.start_game_from_audio)
        self.thread_event = thread_event
        
        self.initialize_help_texts() #initalizes the help texts
        
        # sets up threading for listening
        self.voice_input_thread = None
        self.voice_feedback_thread = None
        self.stop_listening_event = threading.Event()

    # function adds the main screen object as a attribute to audio accessibility class
    def setMS(self, main_screen):
        from app import MainScreen #prevents ciruclar dependency
        self.main_screen: MainScreen = main_screen
        self.apply_theme_signal.connect(self.main_screen.apply_theme)                # Connet theme signal
        self.change_font_family_signal.connect(self.main_screen.change_font_family)  # Connect font family signal
        self.change_font_size_signal.connect(self.main_screen.change_font_size)      # Connect font size signal
        self.init_commands() #sets up commands

    #Sets all the text for help feature
    def initialize_help_texts(self):
        self.objective_text = (
            "Objective: Guess the hidden word one letter at a time. "
            "You have a limited number of incorrect guesses before the game ends."
        )
        self.basic_gameplay_text = (
            "Basic Gameplay:\n"
            "Use the on-screen keyboard, voice input, or type letters to make guesses.\n"
            "Correct guesses will reveal the letters in the word.\n"
            "Incorrect guesses will be tracked, and the hangman drawing will progress."
        )
        self.speech_commands_text = (
            "Speech Commands:\n"
            '"START GAME": Start a new game.\n'
            '"START GAME EASY ": Start a new game in Easy mode.\n'
            '"START GAME MEDIUM ": Start a new game in Medium mode.\n'
            '"START GAME HARD ": Start a new game in Hard mode.\n'
            '"Change Theme ": Adjust the display settings by choosing one of the following themes. \n'
            '"Light Mode ": For brighter lighting. \n'
            '"Dark mode ": For lower lighting. \n'
            '"Contrast Mode ": Black and White. \n'
            '"Blue and Yellow Mode ":  For users with Tritanomaly & Tritanopia. \n'
            '"Red and Green Mode ": For users with Protanomaly, Protanopia & Deuteranopia \n'
            '"Monochromatic Mode ": For users with complete color blindness \n'
            '"Change Font Family ": Adjust the text appearance by choosing one of the following font styles: Arial, Comic Sans, and Open Dyslexic \n'
            '"Change Font Size ": Adjust the text size for better readability by choosing one of the following options: 8, 10, 12, 14, 16, 18, and 20 \n'
            '"EXIT or QUIT": Exit the game.\n'
            '"LIST INCORRECT GUESSES": Hear the letters you have guessed incorrectly.\n'
            '"LIST CORRECT LETTERS": Hear the letters you have guessed correctly.\n'
            '"HANGMAN STATUS": Hear the current status of the hangman drawing.\n'
            '"WORD STATUS": Hear the current state of the hidden word.\n'
            '"PLAY AGAIN": Restart the game after it ends.\n'
            '"GUESS _": Guess a specific letter, for example, ' '"Guess A". \n'
            '"HELP OBJECTIVE": Learn about the games main goal and how to succeed. \n'
            '"HELP GAMEPLAY": Get a detailed explanation of how to play the game. \n'
            '"HELP LIST COMMANDS": Discover all available voice commands for smoother gameplay.\n'
            '"HELP DIFFICULTY LEVELS": Understand the different difficulty levels and their grade-based word selections. \n'
            '"HELP SETTINGS": Explore customization options for themes, fonts, and accessibility settings. \n'
            ""
        )
        self.difficulty_levels_text = (
            "Difficulty Mode: Select a difficulty level (Easy, Medium, Hard) to play with words tailored to that level. \n"
            "The difficulty levels correspond to the following grade levels: \n"
            "Easy: Kindergarten to Grade 4 words. \n"
            "Medium: Grade 5 to Grade 8 words. \n"
            "Hard: Grade 9 to Grade 12 words. \n"
            "Grade Levels: Choose a grade level (K through 12) to play with words suited to that level. \n"
            "Learning Mode: Enhance your learning experience by hearing letters and their associated words as you choose them. \n"
        )
        self.settings_text = (
            "Settings:\n"
            "Word Lists: Create custom word lists for the game, with each word graded based on its complexity. \n"
            "Sound Settings: Turn Voice Input On or Off for accessibility."
            "Use the Theme Settings menu to change the game's color theme for accessibility.\n"
            "Use the Font Settings menu to adjust the font style and size."
        )
    #endregion

    #region AUDIO INTERACTION - sets up listener & narrator
    # Narrates game - audio feeback
    def speak(self, words, pause_before_speak=None):
        self.stop_voice_feedback()
        self.start_voice_feedback(words, pause_before_speak)


    # Listen for audio input
    def listen(self):
        response = None
        with self.mic:
            print("Listening... ")
            try:
                audio = self.recognizer.listen(self.mic)
                response = self.recognizer.recognize_google(audio).upper()
                self.main_window.reset_timer_signal.emit()

                print("Finished listening.")
                print(f"response: {response}")
                print()
                print()
            except sr.UnknownValueError:
                if self.voice_input_turned_on:
                    self.main_window.reset_timer_signal.emit()
                    print("Could not understand audio")
                    self.speak("Could not understand audio, please try again.")
            except:
                print("Input listerner error. Process will continue to work as normal.")
                self.speak("Input listerner error. Process will continue to work as normal.")
        return response
    #endregion
    
    #region VOICE COMMAND LISTENER - handles listener for user voice commands
    # function acts a thread to always to work in the background. responsible for listening to voice commands.
    def voice_input_listener(self):
        while not self.stop_listening_event.is_set():
            # checks if accepting voice input
            if self.voice_input_turned_on:
                # splits voice input into individual words
                voice_input = self.listen()
                if voice_input:
                    input_words = voice_input.split(' ')
                    recognized = False

                    # Checks if command exists in the voice input
                    if not recognized:
                        for word in input_words:
                            # Check if game already started and continues if true
                            if word == "START" and self.game_is_ongoing:
                                continue
                            if word in self.commands:
                                # command was found in voice input & performs command action
                                action = self.commands[word]
                                self.main_screen.sound_menu_action.setDisabled(True)
                                action()
                                self.main_screen.sound_menu_action.setDisabled(False)
                                recognized = True
                                break
                    if not recognized:
                        print("Command not recognized")
                        self.speak("Command not recognized")
                

    # function turns voice input on/off
    def update_voice_input_settings(self):
        self.voice_input_turned_on = not self.voice_input_turned_on
        if self.voice_input_turned_on == False:
            self.stop_voice_input_listener()
            self.main_screen.sound_menu_action.setText("Voice Input OFF")
            self.speak("Voice input turned off!") 
        else:
            self.main_screen.sound_menu_action.setText("Voice Input ON")
            self.speak("Voice input has been turned on!")
            self.start_voice_input_listener()

    def pause_voice_input(self): # pauses voice input
        print("Pausing voice input...")
        self.voice_input_turned_on = False

    def resume_voice_input(self): # resumes voice input
        print("Resuming voice input...")
        self.voice_input_turned_on = True

    # start listening thread
    def start_voice_input_listener(self):
        if self.voice_input_thread and self.voice_input_thread.is_alive():
            self.stop_listening_event.set()
            self.voice_input_thread.join(timeout=2)

        self.stop_listening_event.clear()
        self.voice_input_thread = threading.Thread(
            target=self.voice_input_listener, 
            daemon=True
        )
        self.voice_input_thread.start()

    # kills listening thread
    def stop_voice_input_listener(self):
        self.stop_voice_feedback()
        self.stop_listening_event.set()
        if self.voice_input_thread and self.voice_input_thread.is_alive():
            self.voice_input_thread.join(timeout=2)
        print("Listening has stopped.")
    
    def start_voice_feedback(self, words, pause_before_speak = None):
        if pause_before_speak is not None:
            time.sleep(pause_before_speak)
        
        self.engine.say(words)
        self.engine.runAndWait()
        self.stop_voice_feedback()

    def stop_voice_feedback(self):
        if self.voice_feedback_thread and self.voice_feedback_thread.is_alive():
            self.voice_feedback_thread.join(timeout=2)
    #endregion

    #region USER NOTIFICATIONS - narrates specific feedback during gameplay so user understand what's going on# application greeting function
    def application_greeting(self):
        if self.voice_input_turned_on:
            self.speak("Application started. Hangman window launched.", 2)
            while True:
                self.speak("Turn on voice assistant? Say 'confirm' or 'cancel'.")
                response = self.listen()
                if response:
                    if response == "CONFIRM":
                        self.voice_input_turned_on = True
                        self.speak("Voice inputs turned on.")
                        return True
                    elif response == "CANCEL":
                        self.voice_input_turned_on = False
                        self.main_screen.sound_menu_action.setChecked(False)
                        self.main_screen.sound_menu_action.setText("Voice Input OFF")
                        self.speak("Voice inputs turned off.")
                        return False
                    else:
                        self.speak("Response not recognized. Please try again.")
        
    # function to inform user that game hasn't begun.
    def inform_user_game_has_not_started(self):
        if self.voice_input_turned_on:
            self.speak("Please start game before using commands by saying Start Game")

    # function executed when the game is over, and voice input is turned on. 
    def inform_user_of_game_result(self):
        current_word = self.hangman_game.current_word
        if self.voice_input_turned_on:
            if self.hangman_game.did_you_win:
                self.speak(f"Congrats! You've won! The word was {current_word}!")
            else:
                self.speak(f"You've lost! The word was {current_word}!")
    
    # function that play message if user has been idle for a period of time.
    def idle_message(self):
        if self.voice_input_turned_on:
            try:
                if self.game_is_ongoing:
                    self.speak("A hangman game is currently ongoing. You can make a guess at any time.")
                else:
                    self.speak("Say 'Start Game' to get started.")
            except:
                print("An error occurred when attempting to play the idle message.")
    #endregion

    #region VOICE COMMAND ACTIONS - performs actual actions of voice command
    # function to confirm exit.
    def confirm_exit(self):
        if self.voice_input_turned_on:
            while True:
                self.speak("Are you sure you wish to exit the application? Confirm or Cancel?")
                if response:
                    response = self.listen()
                    if difflib.SequenceMatcher(None, 'CONFIRM', response).ratio() == 1:
                        self.speak("Closing Hangman Application.")
                        self.stop_listening_event.set() 
                        self.quit_game_signal.emit()
                    elif difflib.SequenceMatcher(None, 'CANCEL', response).ratio() == 1:
                        self.speak("Process to exit application has been cancelled!")
                        return
                    else:
                        self.speak("Response not recognized. Please try again.")

    # function to list all wrong guesses by user during game
    def list_wrong_guesses(self):
        if self.game_is_ongoing != True:
            self.inform_user_game_has_not_started()
        else:
            num_of_incorrect_guesses = len(self.hangman_game.incorrect_char_guesses)
            if num_of_incorrect_guesses == 0:
                self.speak("No incorrect letters have been guessed yet.")
            else: 
                self.speak(f"You have guessed {num_of_incorrect_guesses} incorrect letter.") if num_of_incorrect_guesses == 1 else self.speak(f"You have guessed {num_of_incorrect_guesses} incorrect letters.")
                for char in self.hangman_game.correct_char_guesses:
                    self.speak(char, 1)

    # function to list all correct guesses by user during game
    def list_correct_guesses(self):
        if self.game_is_ongoing != True:
            self.inform_user_game_has_not_started()
        else:
            num_of_correct_guesses = len(self.hangman_game.correct_char_guesses)
            if num_of_correct_guesses == 0:
                self.speak("No correct letters have been guessed yet.")
            else: 
                self.speak(f"You have guessed {num_of_correct_guesses} correct letter.") if num_of_correct_guesses == 1 else self.speak(f"You have guessed {num_of_correct_guesses} correct letters.")
                for char in self.hangman_game.correct_char_guesses:
                    self.speak(char, 1)
    
    # Describes each hangman image
    def say_hangman_status(self):
        if self.game_is_ongoing != True:
            self.inform_user_game_has_not_started()
        else:
            if self.hangman_game.number_of_wrong_guesses == 0:
                self.speak("Empty gallows with no stick figure.")
            elif self.hangman_game.number_of_wrong_guesses == 1:
                self.speak("Only stick figure's head added")
            elif self.hangman_game.number_of_wrong_guesses == 2:
                self.speak("Stick figure with head and torso")
            elif self.hangman_game.number_of_wrong_guesses == 3:
                self.speak("Stick figure with head, torso, and left arm.")
            elif self.hangman_game.number_of_wrong_guesses == 4:
                self.speak("Stick figure with head, torso, and left and right arm.")
            elif self.hangman_game.number_of_wrong_guesses == 5:
                self.speak("Stick figure with head, torso, left and right arm, and left leg.")
            elif self.hangman_game.number_of_wrong_guesses == 6:
                self.speak("Stick figure with head, torso, left and right arm, left and right leg")
            elif self.hangman_game.number_of_wrong_guesses == 7:
                self.speak("Stick figure with head, torso, left and right arm, left and right leg, and left eye")
            elif self.hangman_game.number_of_wrong_guesses == 8:
                self.speak("Stick figure with head, torso, left and right arm, left and right leg, and left and right eye")
            elif self.hangman_game.number_of_wrong_guesses == 9:
                self.speak("Stick figure with head, torso, left and right arm, left and right leg, left and right eye, and mouth")
            elif self.hangman_game.number_of_wrong_guesses == 10:
                self.speak("Stick figure with head, torso, left and right arm, left and right leg, left and right eye, mouth, and top hat")
    
    # function to inform user of word status.
    def say_word_status(self):
        if self.game_is_ongoing != True:
            self.inform_user_game_has_not_started()
        else:
            length_of_word = len(self.hangman_game.current_word_progress)
            num_of_correct_guesses = len(self.hangman_game.correct_char_guesses)
            self.speak(f"The current word is {length_of_word} letters long.")
            
            if num_of_correct_guesses == 0:
                self.speak("No letters have been guessed yet.")
            else:
                for index, char in enumerate(self.hangman_game.current_word_progress):
                    number_suffix = None
                    if index == 0:
                        number_suffix = "st"
                    elif index == 1:
                        number_suffix = "nd"
                    elif index == 2:
                        number_suffix = "rd"
                    else:
                        number_suffix = "th"
                    
                    if char == " ":
                        self.speak(f"The {index+1}{number_suffix} letter has not been guessed yet.")
                    else:
                        self.speak(f"The {index+1}{number_suffix} letter in the word is {char}.")

    # help command function for the help objective section
    def help_objective(self):
        self.speak(self.objective_text)

    # help command function for the help gameplay section
    def help_gameplay(self):
        self.speak(self.basic_gameplay_text)

    # help command function for the help speech commands section
    def help_speech_commands(self):
        self.speak(self.speech_commands_text)

    # help command function for the help difficulty levels section
    def help_difficulty_levels(self):
        self.speak(self.difficulty_levels_text)
        
    # help command function for the help settings section
    def help_settings(self):
        self.speak(self.settings_text)
    
    #function to apply the selected theme
    def apply_theme_directly(self, theme):
        if self.voice_input_turned_on:
            try:
                theme_label = theme.get("label", "the selected theme")
                self.speak(f"Changing theme to {theme_label}.")
                self.apply_theme_signal.emit(theme)
            except Exception as e:
                print(f"Error applying theme: {e}")

    # function to prompt the user to choose a theme using voice input 
    def prompt_theme(self):
        if self.voice_input_turned_on:
            self.speak("Choose theme. Light mode, dark mode, contrast mode, blue and yellow mode, red and green mode, or monochromatic mode.")
            select_theme = False
            while not select_theme:
                try:
                    response = self.listen().strip()
                    if response:
                        themes = {
                            "LIGHT": Theme.LIGHT_MODE,
                            "DARK": Theme.DARK_MODE,
                            "CONTRAST": Theme.CONTRAST,
                            "BLUE": Theme.BLUE_YELLOW,
                            "YELLOW": Theme.BLUE_YELLOW,
                            "RED": Theme.RED_GREEN,
                            "GREEN": Theme.RED_GREEN,
                            "MONOCHROMATIC": Theme.MONOCHROMATIC
                        }
                        if response in themes:
                            selected_theme = themes[response]
                            self.apply_theme_directly(selected_theme)  
                            select_theme = True
                        else:
                            self.speak("Invalid theme. Please choose a valid option.")
                except Exception as e:
                    print(f"Error during theme prompt: {e}")
                    self.speak("Processing Error, please try again.")

    # function to change the font to the specified font family
    def change_font(self, font_name):
        if self.voice_input_turned_on:
            self.speak(f"Changing font to {font_name}.")
            available_fonts = ["Arial", "Comic Sans MS", "OpenDyslexic"]
            if font_name in available_fonts:
                self.change_font_family_signal.emit(font_name)  # emit font family change signal
            else:
                self.speak(f"Font {font_name} is not available.")
   
    # function to prompt the user to choose a specific font family
    def prompt_font_family(self):
        if self.voice_input_turned_on:
            self.speak("Choose font family. Arial, Comic Sans, or Open Dyslexic.")
            try:
                response = self.listen()
                if response:
                    font_families = {
                        "ARIAL": "Arial",
                        "ARIEL": "Arial",
                        "COMIC": "Comic Sans MS",
                        "OPEN": "OpenDyslexic",
                        "DYSELXIC": "OpenDyslexic"
                    }
                    if response in font_families:
                        selected_font = font_families[response]
                        self.change_font(selected_font)  # call change_font to apply the selected font
                    else:
                        self.speak("Invalid font family. Choose arial, comic sans, or open dyslexic")
            except Exception as e:
                print(f"Error during font family prompt: {e}")
                self.speak("Processing Error, please try again.")

    # function to change the font to the specified size
    def change_font_size(self, size):
        if self.voice_input_turned_on:
            self.speak(f"Changing font size to {size} point.")
            try:
                size = int(size)
                available_sizes = [8, 10, 12, 14, 16, 18, 20]
                if size in available_sizes:
                    self.change_font_size_signal.emit(size)  # emit font size change signal
                else:
                    self.speak(f"Font size {size} not available.")
            except ValueError:
                self.speak("Invalid font size.")

    #function to prompt the user for a specific font size
    def prompt_font_size(self):
        if self.voice_input_turned_on:
            self.speak("Choose font size, 8, 10, 12, 14, 16, 18, or 20")
            try:
                response = self.listen()
                if response: 
                    font_sizes = {
                        "8": 8,
                        "10":10,
                        "12": 12, 
                        "14": 14, 
                        "16":16, 
                        "18":18, 
                        "20":20, 
                    }
                    if response in font_sizes:
                        selected_size = font_sizes[response]
                        self.change_font_size(selected_size)
                    else:
                        self.speak("Invalid font size. Sizes 8, 10, 12, 14, 16, 18, or 20.")
            except Exception as e:
                print(f"Font Size Error: {e}")
                self.speak("Processing Error, please try again.")
  
    # function to inform user of num of chances left.
    def list_chances(self):
        if self.game_is_ongoing != True:
            self.inform_user_game_has_not_started()
        else:
            statement = f"You have {self.hangman_game.num_of_chances} chances left to guess."
            self.speak(statement)
    #endregion

    #region GAME ENGINE - handles voice input to start game & process letters guessed
    # function to start game via voice command
    def start_game(self, choice=None):
        if self.voice_input_turned_on:
            if choice != None:
                if choice == -1 and self.game_is_ongoing:
                    self.speak("Invalid command! Continue game!")
                elif choice == -1:
                    self.start_game()
                else:
                    self.start_game_signal.emit(choice)
            else:
                while True:
                    self.speak("Select a difficulty: Easy. Medium. Or hard. Or say cancel.")
                    response = self.listen()
                    if response: 
                        if difflib.SequenceMatcher(None, 'EASY', response).ratio() == 1:
                            self.speak("Beginning easy hangman session.")
                            self.start_game_signal.emit(0)
                            break
                        elif difflib.SequenceMatcher(None, 'MEDIUM', response).ratio() == 1:
                            self.speak("Beginning medium hangman session.")
                            self.start_game_signal.emit(1)
                            break
                        elif difflib.SequenceMatcher(None, 'HARD', response).ratio() == 1:
                            self.speak("Beginning hard hangman session.")
                            self.start_game_signal.emit(2)
                            break
                        elif difflib.SequenceMatcher(None, 'CANCEL', response).ratio() == 1:
                            self.speak("Process to start game has been cancelled!")
                            return
                        elif difflib.SequenceMatcher(None, 'EXIT', response).ratio() == 1 or difflib.SequenceMatcher(None, 'QUIT', response).ratio() == 1:
                            self.confirm_exit()
                        else:
                            self.speak("Response not recognized. Please try again.")

    # function creates the commands dictionary. dictionary has a key-value pair of strings and functions. when a recognized command is said, the mapped function will be executed.
    def init_commands(self):
        self.commands = {
            "START": self.start_game,
            "EASY": lambda: self.start_game(0),
            "MEDIUM": lambda: self.start_game(1),
            "HARD": lambda: self.start_game(2),
            "EXIT": self.confirm_exit,
            "QUIT": self.confirm_exit,
            "INCORRECT": self.list_wrong_guesses,
            "CORRECT": self.list_correct_guesses,
            "HANGMAN": self.say_hangman_status,
            "CHANCE": self.list_chances,
            "CHANCES": self.list_chances,
            "WORD": self.say_word_status,
            "PLAY": lambda: self.start_game(-1),
            # help commands
            "OBJECTIVE": self.help_objective,
            "GAMEPLAY": self.help_gameplay,
            "COMMANDS": self.help_speech_commands,
            "LEVELS": self.help_difficulty_levels,
            "SETTINGS": self.help_settings,
        }
        # adds the first command level to change the theme, font family, and size
        self.commands.update({"THEME": self.prompt_theme})
        self.commands.update({"FAMILY": self.prompt_font_family})
        self.commands.update({"SIZE": self.prompt_font_size})
        # adding letters as recognizable guess commands.
        self.commands.update({chr(i): lambda char=chr(i): self.handle_letter_guess(char) for i in range(65, 91)})
        self.commands.update({f"LETTER {chr(i)}": lambda char=chr(i): self.handle_letter_guess(char) for i in range(65, 91)})

    
    # function to handle voice guess
    def handle_letter_guess(self, char):
        if self.game_is_ongoing == False or self.game_is_ongoing == None:
            self.inform_user_game_has_not_started()
        else:
            if char in self.hangman_game.correct_char_guesses:
                self.speak(f"You've already guess the letter {char} correctly.")
            elif char in self.hangman_game.incorrect_char_guesses:
                self.speak(f"You've already guess the letter {char} incorrectly.")
            else:
                while True:
                    self.speak(f"Did you say letter {char}? If so, say confirm or cancel.")
                    response = self.listen()
                    if response:
                        if difflib.SequenceMatcher(None, 'CONFIRM', response).ratio() == 1:
                            self.input_queue.put(char)
                            time.sleep(.5)
                            if self.hangman_game.was_last_guess_correct:
                                self.speak(f"Letter {char} was correct!")
                            else:
                                self.speak(f"Letter {char} was incorrect!")
                                self.speak(f"You have {self.hangman_game.num_of_chances} chances left.")
                            return
                        elif difflib.SequenceMatcher(None, 'CANCEL', response).ratio() == 1:
                            self.speak("Guess cancelled!")
                            return
                        else:
                            self.speak("Response not recognized. Please try again.")

    # function updates game status
    def update_game_is_ongoing(self, new_status):
        self.game_is_ongoing = new_status
    #endregion