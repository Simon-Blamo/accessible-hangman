import os
import re
from hangman import Hangman
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

def showcase_wrong_guesses(hangman_game: Hangman):
    print("Wrong guesses: ", end="")
    for char in hangman_game.incorrect_char_guesses:
        print(char+" ", end="")
    print()

def print_player_progress(hangman_game: Hangman):
    player_progress = " "
    if len(hangman_game.correct_char_guesses) == 0:
        for char in hangman_game.current_word:
            player_progress += "_  "
    else:
        for char in hangman_game.current_word_progress:
            if char != " ":
                player_progress += char + "  "
            else:
                player_progress += "_  "
    print(player_progress)

def game_loop(hangman_game: Hangman):
    chances_left = 6
    was_the_guess_correct = None
    invalid_input = None
    while True:
        clear_terminal()
        if invalid_input:
            print("Please limit the input to only one alphabetic character.")
            print()
            invalid_input = False
        print_player_progress(hangman_game)
        showcase_wrong_guesses(hangman_game)
        game_is_over = hangman_game.check_game_status()
        if game_is_over[0]:
            if game_is_over[1]:
                print("You've won!")
            else:
                print("You've lost :(")
                print("The word was " + hangman_game.current_word + "!")
            exit()
        if was_the_guess_correct == False:
            chances_left -= 1
        print("Chances left: " + str(chances_left))
        
        user_guess = input("Guess: ")
        if(user_guess.lower() == 'exit'):
            exit()
        if not re.match("^[A-Za-z]{1}$", user_guess):
            was_the_guess_correct = None
            invalid_input = True
            continue
        was_the_guess_correct = hangman_game.process_guess(user_guess)


def game():
    clear_terminal()
    hangman_game: Hangman = Hangman()
    difficulty = difficulty_prompt()
    hangman_game.set_current_word(difficulty)
    game_loop(hangman_game)

game()