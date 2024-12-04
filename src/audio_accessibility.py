from PyQt6.QtCore import *
from hangman import Hangman
import threading
import time
import speech_recognition as sr
import pyttsx3
import difflib

# Handles audio acessibility: listens for voice commands and narrates audio feedback during gameplay
class AudioAccessibility(QObject):
    #region INITIALIZATION - sets up class
    start_game_signal = pyqtSignal(int)                         # signal to tell main window to start the hangman game.
    quit_game_signal  = pyqtSignal()                            # signal to tell main window to quit the process.
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
        self.start_game_signal.connect(self.main_window.start_game_from_audio)
        self.thread_event = thread_event
        self.voice_input_thread = None
        self.stop_listening_event = threading.Event()
        pass
    
    # function adds the main screen object as a attribute to audio accessibility class
    def setMS(self, main_screen):
        from app import MainScreen #prevents ciruclar dependency
        self.main_screen: MainScreen = main_screen
        self.init_commands()
    #endregion

    #region AUDIO INTERACTION - sets up listener & narrator
    # Narrates game - audio feeback
    def speak(self, words, time_to_sleep_before_speaking=None):
        if time_to_sleep_before_speaking is not None:
            time.sleep(time_to_sleep_before_speaking)
        self.engine.say(words)
        self.engine.runAndWait()


    # Listen for audio input
    def listen(self):
        with self.mic:
            print("Listening... ")
            audio = self.recognizer.listen(self.mic)
            response = self.recognizer.recognize_google(audio).upper()
            self.main_window.reset_timer_signal.emit()
            print("Finished listening.")
            print(f"response: {response}")
            print()
            print()
        return response
    #endregion
    
    #region VOICE COMMAND LISTENER - handles listener for user voice commands
    # function acts a thread to always to work in the background. responsible for listening to voice commands.
    def voice_input_listener(self):
        while not self.stop_listening_event.is_set():
            if self.voice_input_turned_on:
                try:
                    voice_input = self.listen().upper()
                    input_words = voice_input.split(' ')
                    recognized = False

                    # Checks if command exists in the voice input
                    if not recognized:
                        for word in input_words:
                            # Check if game already started and continues if true
                            if word == "START" and self.game_is_ongoing:
                                continue
                            if word in self.commands:
                                action = self.commands[word]
                                action()
                                recognized = True
                                break

                    if not recognized:
                        print("Command not recognized")
                        self.speak("Command not recognized")
                except sr.UnknownValueError:
                    if self.voice_input_turned_on:
                        self.main_window.reset_timer_signal.emit()
                        print("Could not understand audio")
                        self.speak("Could not understand audio, please try again.")
                except:
                    print("An error occurred when attempting to listen to input. Process will continue to work as normal.")
                    self.speak("An error occurred when attempting to listen to input. Process will continue to work as normal.")

    # function turns voice input on/off
    def update_voice_input_settings(self):
        self.voice_input_turned_on = not self.voice_input_turned_on
        self.speak("Voice input has been turned off!") if self.voice_input_turned_on == False else self.speak("Voice input has been turned on!")

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
        self.stop_listening_event.set()
        if self.voice_input_thread and self.voice_input_thread.is_alive():
            self.voice_input_thread.join(timeout=2)
    #endregion

    #region USER NOTIFICATIONS - narrates specific feedback during gameplay so user understand what's going on# application greeting function
    def application_greeting(self):
        if self.voice_input_turned_on:
            self.speak("Application started. Hangman window launched.", 2)
            while True:
                self.speak("Would you like to have the voice input listener turned on? Say 'affirmative' to have the application begin with voice inputs. Say 'negative', if you would like the application to run without the commands.")

                response = self.listen()
                if response == "AFFIRMATIVE":
                    self.speak("Voice inputs has been turned on. You can change this anytime, within the settings menu.")
                    break
                elif response == "NEGATIVE":
                    self.speak("Voice inputs has been turned off. You can change this anytime, within the settings menu.")
                    break
                else:
                    self.speak("Response not recognized. Please try again.")


        
    # function to inform user that game hasn't begun.
    def inform_user_game_has_not_started(self):
        if self.voice_input_turned_on:
            self.speak("Command cannot be executed as a game of hangman is currently not being played. If you wish to start, please say 'Start Game' or select the one of the difficulty button showcased on the screen.")

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
                response = self.listen().upper()
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
                self.speak("You've have guessed no incorrect letters so far.")
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
                self.speak("You've have guessed no correct letters so far.")
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
            self.speak(f"The current word is {length_of_word} letters long. Here's is current progress with the selected word.")
            if num_of_correct_guesses == 0:
                self.speak("You have guessed no correct letters. All positions are blank currently.")
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
    
    # function to inform user of num of chances left.
    def list_chances(self):
        if self.game_is_ongoing != True:
            self.inform_user_game_has_not_started()
        else:
            statement = f"You have {self.hangman_game.num_of_chances} chances left to guess incorrectly."
            self.speak(statement)
    #endregion

    #region GAME ENGINE - handles voice input to start game & process letters guessed
    # function to start game via voice command
    def start_game(self, choice=None):
        if self.voice_input_turned_on:
            if choice != None:
                if choice == -1 and self.game_is_ongoing:
                    self.speak("This command is unavailable! The game is still on-going!")
                elif choice == -1:
                    self.start_game()
                else:
                    self.start_game_signal.emit(choice)
            else:
                while True:
                    self.speak("Which difficulty level would you like to play on? There are three difficulties: Easy. Medium. And hard. You can also cancel this action at any time, by stating 'CANCEL'.")
                    response = self.listen().upper()  
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
            "WORD": self.say_word_status,
            "PLAY": lambda: self.start_game(-1),
            "CHANCE": self.list_chances,
            "CHANCES": self.list_chances
        }
        
        # adding letters as recognizable guess commands.
        self.commands.update({chr(i): lambda char=chr(i): self.handle_letter_guess(char) for i in range(65, 91)})
        self.commands.update({f"LETTER {chr(i)}": lambda char=chr(i): self.handle_letter_guess(char) for i in range(65, 91)})

    
    # function to handle voice guess
    def handle_letter_guess(self, char):
        if self.game_is_ongoing == False or self.game_is_ongoing == None:
            self.inform_user_game_has_not_started()
        else:
            if char in self.hangman_game.correct_char_guesses:
                self.speak(f"You've already guess the letter {char} correctly. Please guess a different letter.")
            elif char in self.hangman_game.incorrect_char_guesses:
                self.speak(f"You've already guess the letter {char} incorrectly. Please guess a different letter.")
            else:
                while True:
                    self.speak(f"Did you say the letter {char}? If so, say confirm to confirm your guess, or cancel to cancel this guess.")
                    response = self.listen().upper()
                    if difflib.SequenceMatcher(None, 'CONFIRM', response).ratio() == 1:
                        self.input_queue.put(char)
                        self.thread_event.wait(4)
                        if self.hangman_game.was_last_guess_correct:
                            self.speak(f"Your guess was correct! {char} was in the word!")
                        else:
                            self.speak(f"Your guess was incorrect! {char} was not in the word!")
                        self.speak(f"You have {self.hangman_game.num_of_chances} chances left to guess incorrectly.")
                        return
                    elif difflib.SequenceMatcher(None, 'CANCEL', response).ratio() == 1:
                        self.speak("Your guess has been cancelled!")
                        return
                    else:
                        self.speak("Response not recognized. Please try again.")

    # function updates game status
    def update_game_is_ongoing(self, new_status):
        self.game_is_ongoing = new_status
    #endregion