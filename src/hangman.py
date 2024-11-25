import random
from pathlib import Path

class Hangman():
    def __init__(self):
        self.num_of_chances: int = 11                   # Number of chances given to player for incorrect guesses.
        self.number_of_wrong_guesses: int = 0           # Used to track whether the player loses
        self.is_the_game_over: bool = None              # Informs whether the game is over
        self.did_you_win: bool = None                   # Informs whether the user won.
        self.was_last_guess_correct: bool = None        # Informs whether the last guess by the user was correct.
        self.current_word: str = None                   # Stores current word for current game
        self.correct_char_guesses: list[str] = []       # Stores all correct character guesses from user during a game
        self.incorrect_char_guesses: list[str] = []     # Stores all incorrect character guesses from user during a game
        self.current_word_progress: list[str] = []      # Representation of the word progress made by user; initially a blank slate.
        self.chars_positions_in_word_dict: dict[str, list[int]] = {}    # Has positions of where characters can be found from current word.
        
    '''
    Methods selects word from text files, and sets the class attribute current word for the hangman game.

    There are 3 difficulty levels.
        0 = Easy
        1 = Medium
        2 = Hard
    '''
    def set_current_word(self, difficulty: int):
        file_path = None
        list_of_words = []
        chosen_word = None
        if difficulty == 0:
            file_path = Path('../assets/words/easyWords.txt')
            with file_path.open("r") as f:
                for line in f:
                    list_of_words.append(line)
            chosen_word = random.choice(list_of_words)
        elif difficulty == 1:
            file_path = Path('../assets/words/medWords.txt')
            with file_path.open("r") as f:
                for line in f:
                    list_of_words.append(line)
            chosen_word = random.choice(list_of_words)
        elif difficulty == 2:
            file_path = Path('../assets/words/hardWords.txt')
            with file_path.open("r") as f:
                for line in f:
                    list_of_words.append(line)
            chosen_word = random.choice(list_of_words)
        self.current_word = chosen_word.upper().strip()
        self.update_current_word_progress()
        self.update_chars_positions_dict()

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

    '''
    Method resets the hangman_game object to initial state. Used after the game is over.
    ''' 
    def reset_hangman(self):
        self.num_of_chances: int = 11 
        self.number_of_wrong_guesses = 0
        self.is_the_game_over = None
        self.did_you_win = None
        self.was_last_guess_correct = None
        self.current_word = None
        self.correct_char_guesses = []
        self.incorrect_char_guesses = []
        self.current_word_progress = []
        self.chars_positions_in_word_dict = {}