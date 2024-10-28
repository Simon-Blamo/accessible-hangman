import random
import os
import re
def clear_terminal():
  if os.name == 'nt':
    os.system("cls")
  else:
    os.system("clear")

def prompt():
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
3 difficulties levels.
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
    return return_word

def init_default_progress(word):
    return_str = "  "
    for char in word:
        return_str += "_  "
    return return_str

## Need to do.
def update_player_progress(player_progress, word):
    pass

## Need to finish.
def game_loop(word):
    num_of_fails = 0
    player_progress = init_default_progress(word)
    while num_of_fails < 6:
        print(player_progress)
        user_guess = input()
        if(user_guess.lower() == 'exit'):
            exit()
        if not re.match("^[A-Za-z]{1}$", user_guess):
            print("Please limit the input only one alphabetic character.")
            continue
        if user_guess in word:
            pass

def game():
    clear_terminal()
    difficulty = prompt()
    word = select_word(difficulty)
    game_loop(word)

game()