import random

class Hangman():
    def __init__(self):
        self.number_of_wrong_guesses = 0
        self.is_the_game_over = False
        self.did_you_win = None
        self.current_word = None
        self.correct_char_guesses = []
        self.incorrect_char_guesses = []
        self.current_word_progress = []
        self.chars_positions_in_word_dict = {}
        
    '''
    3 difficulty levels.
    0 = Easy
    1 = Medium
    2 = Hard
    '''
    def set_current_word(self, difficulty):
        list_of_words = []
        chosen_word = None
        if difficulty == 0:
            with open("easyWords.txt", "r") as f:
                for line in f:
                    list_of_words.append(line)
            chosen_word = random.choice(list_of_words)
        elif difficulty == 1:
            with open("medWords.txt", "r") as f:
                for line in f:
                    list_of_words.append(line)
            chosen_word = random.choice(list_of_words)
        elif difficulty == 2:
            with open("hardWords.txt", "r") as f:
                for line in f:
                    list_of_words.append(line)
            chosen_word = random.choice(list_of_words)
        self.current_word = chosen_word.upper().strip()
        self.update_current_word_progress()
        self.update_chars_positions_dict()

    def get_current_word(self):
        return self.current_word
    
    def update_chars_positions_dict(self):
        for index, char in enumerate(self.current_word):
            if char not in self.chars_positions_in_word_dict:
                self.chars_positions_in_word_dict[char] = []
            self.chars_positions_in_word_dict[char].append(index)
    
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

    # Function to check status of game
    # Returns two element array:
    ## First Element tells program if game reached a end state.
    ## Second Element is either False (player lost), True (player won), or None (Game is not over yet).
    def check_game_status(self):
        if self.number_of_wrong_guesses >= 6:
            return [True, False]
        elif self.all_chars_found():
            return [True, True]
        else:
            return [False, None]
        
    def process_guess(self, input):
        return_value = None
        if input.upper() in self.get_current_word():
            self.correct_char_guesses.append(input.upper())
            self.update_current_word_progress()
            return_value = True
        else:
            self.number_of_wrong_guesses += 1
            if input.upper() not in self.incorrect_char_guesses:
                self.incorrect_char_guesses.append(input.upper())
            return_value = False

        self.is_the_game_over = self.check_game_status()[0]
        if self.is_the_game_over:
            self.did_you_win = self.check_game_status()[1]
        return return_value
            


    def reset_hangman(self):
        self.number_of_wrong_guesses = 0
        self.is_the_game_over = False
        self.did_you_win = None
        self.current_word = None
        self.correct_char_guesses = []
        self.incorrect_char_guesses = []
        self.current_word_progress = []
        self.chars_positions_in_word_dict = {}

    def game_loop(word):
        num_of_wrong_guesses = 0
        chances_left = 6
        correct_chars_guessed = []
        incorrect_chars_guessed = []
        game_is_over = None
        player_progress = update_player_progress(correct_chars_guessed, word)
        while True:
            print(player_progress)
            game_is_over = is_game_over(num_of_wrong_guesses, correct_chars_guessed, word)
            if game_is_over[0]:
                if game_is_over[1]:
                    print("You've won!")
                else:
                    print("You've lost :(")
                    print("The word was " + word + "!")
                exit()
            print("Chances left: " + str(chances_left))
            showcase_wrong_guesses(incorrect_chars_guessed)
            user_guess = input("Guess: ")
            if(user_guess.lower() == 'exit'):
                exit()
            if not re.match("^[A-Za-z]{1}$", user_guess):
                print("Please limit the input to only one alphabetic character.")
                continue
            if user_guess in word:
                correct_chars_guessed.append(user_guess)
            else:
                if user_guess not in incorrect_chars_guessed:
                    incorrect_chars_guessed.append(user_guess)
                    num_of_wrong_guesses += 1
                    chances_left -= 1
            player_progress = update_player_progress(correct_chars_guessed, word)





# game()