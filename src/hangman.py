import random
from pathlib import Path

class Hangman():
    # intializes hangman data
    def __init__(self):
        self.num_of_chances: int = 11
        self.number_of_wrong_guesses: int = 0
        self.is_the_game_over: bool = None
        self.did_you_win: bool = None
        self.was_last_guess_correct: bool = None
        self.current_word: str = None
        self.correct_char_guesses: list[str] = []
        self.incorrect_char_guesses: list[str] = []
        self.current_word_progress: list[str] = []
        self.chars_positions_in_word_dict: dict[str, list[int]] = {}
        
        # Add these new attributes
        self.default_word_list = []  # Store default words from difficulty files
        self.word_list = []  # Current active word list
        self.load_default_words()  # Load default words

    # Sets words for difficulties: easy, medium, hard
    def load_default_words(self):
        """Load default words from difficulty files"""
        try:
            easy_words = []
            med_words = []
            hard_words = []
            
            # Load easy words
            with Path('../assets/words/easyWords.txt').open("r") as f:
                easy_words = [line.strip().upper() for line in f]
            
            # Load medium words
            with Path('../assets/words/medWords.txt').open("r") as f:
                med_words = [line.strip().upper() for line in f]
            
            # Load hard words
            with Path('../assets/words/hardWords.txt').open("r") as f:
                hard_words = [line.strip().upper() for line in f]
            
            self.default_word_list = {
                0: easy_words,
                1: med_words,
                2: hard_words
            }
        except Exception as e:
            print(f"Error loading default words: {e}")
            self.default_word_list = {0: [], 1: [], 2: []}

    
    def reset_word_list(self):
        """Reset to using the default word lists"""
        self.word_list = []  # Clear current word list
        self.current_word = None
        print("Reset to default word lists")

    def set_word_list(self, words: list[str]):
        """Set the word list for grade-based gameplay"""
        self.word_list = [word.upper().strip() for word in words]
        print(f"Set new word list with {len(self.word_list)} words")
        # Don't select a word here - wait for set_current_word or game start

    def set_current_word(self, difficulty: int):
        """Set current word based on difficulty or current word list"""
        if self.word_list:  # If we have a custom word list (grade mode)
            self.current_word = random.choice(self.word_list)
        else:  # Use default difficulty word lists
            if difficulty in self.default_word_list and self.default_word_list[difficulty]:
                self.current_word = random.choice(self.default_word_list[difficulty])
            else:
                print(f"Warning: No words available for difficulty {difficulty}")
                return

        self.current_word = self.current_word.upper().strip()
        self.update_current_word_progress()
        self.update_chars_positions_dict()
        print(f"Set current word to: {self.current_word}")

    # Gets the current word being guessed
    def get_current_word(self):
        return self.current_word
    
    '''
    Method updates the class attribute dictionary(map). The map has a key-value pair where the key is type of str (yet all keys are just a single char) that points to a list. That list contains all the positions where that char can be found within the word.
    '''
    def update_chars_positions_dict(self):
        for index, char in enumerate(self.current_word):
            if char not in self.chars_positions_in_word_dict:
                self.chars_positions_in_word_dict[char] = []
            self.chars_positions_in_word_dict[char].append(index)
    
    '''
    Method updates the current word progress

        1. If the game has just started or no correct guesses have been made, the object will be rendered as a blank slate with no characters.

        2. If the user has guessed characters correctly, the current word progress object fills in the positions where those correct characters are found.
    '''
    def update_current_word_progress(self):
        current_char_positions_array = None
        if self.current_word_progress == []:
            for char in self.current_word:
                self.current_word_progress.append(" ")
        else:
            for char in self.correct_char_guesses:
                current_char_positions_array = self.chars_positions_in_word_dict[char]
                for position in current_char_positions_array:
                    self.current_word_progress[position] = char

    # checks if the entire word was guessed by checking if all the characters where found
    def all_chars_found(self):
        for char in self.current_word:
            if char not in self.correct_char_guesses:
                return False
        return True

    '''
    Method to check status of game
    
    Returns two element array:
        First Element tells program if game reached a end state.
        Second Element is either False (player lost), True (player won), or None (Game is not over yet).
    '''
    def check_game_status(self):
        if self.num_of_chances == 0:
            return [True, False]
        elif self.all_chars_found():
            return [True, True]
        else:
            return [False, None]
        

    '''
    Method processes the input from user. 
    
    Returns whether the guess was correct or not, while updating the game status.
    '''
    def process_guess(self, input: str):
        return_value = None
        if input == '' or input == ' ':
            return
        if input.upper() in self.get_current_word():
            if input.upper() not in self.correct_char_guesses:
                self.correct_char_guesses.append(input.upper())
                self.update_current_word_progress()
            return_value = True
        else:
            if input.upper() not in self.incorrect_char_guesses:
                self.incorrect_char_guesses.append(input.upper())
                self.number_of_wrong_guesses += 1
                self.num_of_chances -= 1
            return_value = False

        self.is_the_game_over = self.check_game_status()[0]
        if self.is_the_game_over:
            self.did_you_win = self.check_game_status()[1]
        self.was_last_guess_correct = return_value
        return return_value

    # Method resets the hangman_game object to initial state. Used after the game is over.
    def reset_hangman(self):
        self.num_of_chances = 11 
        self.number_of_wrong_guesses = 0
        self.is_the_game_over = None
        self.did_you_win = None
        self.was_last_guess_correct = None
        self.current_word = None
        self.correct_char_guesses = []
        self.incorrect_char_guesses = []
        self.current_word_progress = []
        self.chars_positions_in_word_dict = {}