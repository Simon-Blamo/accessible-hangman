import random
import os
import re
def clear_terminal():
  if os.name == 'nt':
    os.system("cls")
  else:
    os.system("clear")

def difficulty_prompt():
    return_value = 0
    user_choice_valid = False
    user_choice = input("Welcome to Hangman! Select a difficulty to get started! \nYou have the options of EASY, MEDIUM, or HARD: ")
    while user_choice_valid == False:
        if(user_choice.lower() == 'exit'):
            exit()
        if user_choice.lower() == 'easy':
            user_choice_valid = True
            return_value = 0
        elif user_choice.lower() == 'medium':
            user_choice_valid = True
            return_value = 1
        elif user_choice.lower() == 'hard':
            user_choice_valid = True
            return_value = 2
        else:
            print()
            print("Please enter a valid option.")
            user_choice = input("You have the options of EASY, MEDIUM, or HARD: ")
    
    return return_value

'''
3 difficulty levels.
0 = Easy
1 = Medium
2 = Hard
'''
def select_word(difficulty):
    return_word = None
    list_of_words = []
    if difficulty == 0:
        with open("easyWords.txt", "r") as f:
            for line in f:
                list_of_words.append(line)
        return_word = random.choice(list_of_words)
    elif difficulty == 1:
        with open("medWords.txt", "r") as f:
            for line in f:
                list_of_words.append(line)
        return_word = random.choice(list_of_words)
    elif difficulty == 2:
        with open("hardWords.txt", "r") as f:
            for line in f:
                list_of_words.append(line)
        return_word = random.choice(list_of_words)
    print(return_word)
    return return_word.strip()

def all_chars_found(correct_chars_guessed, word):
    for char in word:
        if char not in correct_chars_guessed:
            return False
    return True

# Function to check status of game
# Returns two element array:
## First Element tells program if game reached a end state.
## Second Element is either False (player lost), True (player won), or None (Game is not over yet).
def is_game_over(num_of_wrong_guess, correct_chars_guessed, word):
    if num_of_wrong_guess >= 6:
        return [True, False]
    elif all_chars_found(correct_chars_guessed, word):
        return [True, True]
    else:
        return [False, None]
    

def update_player_progress(correct_chars_guessed, word):
    return_str = "  "
    print(len(word))
    if len(correct_chars_guessed) == 0:
        for char in word:
            return_str += "_  "
    else:
        for char in word:
            if char in correct_chars_guessed:
                return_str += char + "  "
            else:
                return_str += "_  "
    return return_str
 

## Need to finish.
def game_loop(word):
    num_of_wrong_guesses = 0
    correct_chars_guessed = []
    incorrect_chars_guessed = []
    game_status = None
    player_progress = update_player_progress(correct_chars_guessed, word)
    while True:
        print(player_progress)
        game_status = is_game_over(num_of_wrong_guesses, correct_chars_guessed, word)
        if game_status[0] == True:
            if game_status[1] == True:
                print("You've won!")
            else:
                print("You've lost :(")
            exit()
        user_guess = input()
        if(user_guess.lower() == 'exit'):
            exit()
        if not re.match("^[A-Za-z]{1}$", user_guess):
            print("Please limit the input to only one alphabetic character.")
            continue
        if user_guess in word:
            correct_chars_guessed.append(user_guess)
        else:
            incorrect_chars_guessed.append(user_guess)
            num_of_wrong_guesses += 1
        player_progress = update_player_progress(correct_chars_guessed, word)

def game():
    clear_terminal()
    difficulty = difficulty_prompt()
    word = select_word(difficulty)
    game_loop(word)

game()