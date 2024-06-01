#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import random
import sqlite3
from tabulate import tabulate

# Images to be displayed for the hangman game
HANGMAN_PICS_8 = ['''
  +---+
      |
      |
      |
     ===''', '''
  +---+
  O   |
      |
      |
     ===''', '''
  +---+
  O   |
  |   |
      |
     ===''', '''
  +---+
  O   |
 /|   |
      |
     ===''', '''
  +---+
  O   |
 /|\  |
      |
     ===''', '''
  +---+
  O   |
 /|\  |
 /    |
     ===''', '''
  +---+
  O   |
 /|\  |
 / \  |
     ===''', '''
  +---+
 [O   |
 /|\  |
 / \  |
     ===''', '''
  +---+
 [O]  |
 /|\  |
 / \  |
     ===''']  

HANGMAN_PICS_6 = HANGMAN_PICS_8[2:]

# Sets of the words given for the task
WORDS = {
    'Animals': 'ant baboon badger bat bear beaver camel cat clam cobra'.split(),
    'Shapes': 'square triangle rectangle circle ellipse rhombus trapezoid'.split(),
    'Places': 'Cairo London Paris Baghdad Istanbul Riyadh'.split()
}

# Setting up a database to store the records for the Hall of Fame
def setup_database():
    
    #Connect to the database 'hangman.db', creates it if it doesn't already exist
    conn = sqlite3.connect('hangman.db') 
    
    #Create a cursor to execute SQL commands
    cursor = conn.cursor()
    
    #Create a table named 'HallOfFame' if it doesn't exist using SQl command
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS HallOfFame (
            PlayerName TEXT,
            Level TEXT,
            RemainingLives INTEGER
        )
    ''')
    
    #Commit to the save the changes made to the database
    conn.commit()
    
    #Close the connection to save resources
    conn.close()

# Function to add or update the Hall of Fame
def update_hall_of_fame(player_name, level, remaining_lives):
    
    #Connect to the database
    conn = sqlite3.connect('hangman.db')
    
    #Create the cursor
    cursor = conn.cursor()
    
    #Select the record with the highest value for RemainingLives, one for each difficulty
    cursor.execute('''
        SELECT RemainingLives FROM HallOfFame
        WHERE Level = ?
        ORDER BY RemainingLives DESC
        LIMIT 1
    ''', (level,))
    
    #Fetch the result for the query
    record = cursor.fetchone()
    
    #Check if there is no existing record or if the new record is better and delete the previous record to replace it with the better one
    if not record or remaining_lives > record[0]:
        cursor.execute('''
            DELETE FROM HallOfFame WHERE Level = ?
        ''', (level,))
        cursor.execute('''
            INSERT INTO HallOfFame (PlayerName, Level, RemainingLives)
            VALUES (?, ?, ?)
        ''', (player_name, level, remaining_lives))
        conn.commit()
    
    #Close to save resources
    conn.close()

# Function to display the Hall of Fame
def display_hall_of_fame():
    
    conn = sqlite3.connect('hangman.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM HallOfFame ORDER BY Level')
    records = cursor.fetchall()
    conn.close()
    
    #Using the tabulate library print the records in a tabular format
    print(tabulate(records, headers=["Player Name", "Level", "Remaining Lives"], tablefmt="grid"))

# Function to print the introductory menu of the game
def print_intro_menu(player_name):
    print(tabulate([[f"Hi {player_name}.", "Welcome to HANGMAN"],
                    ["PLAY THE GAME", "1"],
                    ["Hall of fame", "2"],
                    ["About the game", "3"],
                    ["EXIT", "4"]],
                   tablefmt="grid"))

# Function to printhe level selection menu
def print_level_menu():
    print(tabulate([["Select the Level of Challenge"],
                    ["Easy level", "1"],
                    ["Moderate level", "2"],
                    ["Hard level", "3"]],
                   tablefmt="grid"))

# Function to print the word selection menu
def print_word_set_menu():
    print(tabulate([["SELECT FROM THE FOLLOWING SETS OF SECRET WORDS"],
                    ["Animals", "1"],
                    ["Shapes", "2"],
                    ["Places", "3"]],
                   tablefmt="grid"))

# Function to display details about the game(Help menu)
def print_about():
    print(tabulate([["ABOUT THE GAME"],
                    ["Easy: The user will be given the chance to select the list from which the random word will be selected (Animals, Shapes, Places). This will make it easier to guess the secret word. Also, the number of trials will be increased from 6 to 8."],
                    ["Moderate: Similar to Easy, the user will be given the chance to select the set from which the random word will be selected (Animals, Shapes, Places), but the number of trials will be reduced to 6. The last two graphics will not be used or displayed."],
                    ["Hard: The code will randomly select a set of words. From this set, the code will randomly select a word. The user will have no clue on the secret word. Also, the number of trials will remain at 6."]],
                   tablefmt="grid"))

# Get player's choice with valid input only
def get_player_choice(options):
    choice = input("> ")
    while choice not in options:
        print("Invalid choice, please try again.")
        choice = input("> ")
    return choice

# Main game function
def play_game(player_name, level, word_set=None):
    
    #Set the number of attempts for the modes
    attempts = 8 if level == 'Easy' else 6
    #Select the required set of pictures as per user's choice
    hangman_pics = HANGMAN_PICS_8 if level == 'Easy' else HANGMAN_PICS_6

    #Randomize the set for hard difficulty
    if level == 'Hard':
        category = random.choice(list(WORDS.keys()))
    else:
        category = word_set
    
    secret_word = random.choice(WORDS[category]).upper()
    guessed_letters = []
    correct_letters = []

    #Check number of attempts left
    while attempts > 0:
        #Print the hangman pics based on the attempts left
        print(hangman_pics[8 - attempts] if level == 'Easy' else hangman_pics[6 - attempts])  # Adjust index to be within the valid range
        
        #Print the letters guessed by the user
        print("Guessed letters: " + " ".join(guessed_letters))
        
        #Print the letters guessed correctly in the word
        print(" ".join([letter if letter in correct_letters else "_" for letter in secret_word]))

        #Take the input for the guess
        guess = input("Guess a letter: ").upper()
        
        #Validate the guesses
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        if guess in guessed_letters:
            print("You have already guessed that letter. Choose again.")
            continue
    
        #Maintain all the letters guessed by the user 
        guessed_letters.append(guess)
        
        #Validate the word formed 
        if guess in secret_word:
            correct_letters.append(guess)
            if all(letter in correct_letters for letter in secret_word):
                print("Congratulations! You've guessed the word:", secret_word)
                update_hall_of_fame(player_name, level, attempts)
                break
        else:
            attempts -= 1
            print(f"Wrong guess! {attempts} attempts remaining.")

    #End the game if attempts exceeded
    if attempts == 0:
        print(hangman_pics[-1])
        print("Sorry, you have run out of attempts. The word was:", secret_word)

# Main function
def main():
    #Set up the database for the game
    setup_database()

    print("Welcome to HANGMAN!")
    player_name = input("Please enter your name: ")

    #Loop to run the game and take the choices from the user accordingly
    while True:
        print_intro_menu(player_name)
        choice = get_player_choice(['1', '2', '3', '4'])

        if choice == '1':
            print_level_menu()
            level_choice = get_player_choice(['1', '2', '3'])
            levels = { '1': 'Easy', '2': 'Moderate', '3': 'Hard' }
            level = levels[level_choice]

            if level in ['Easy', 'Moderate']:
                print_word_set_menu()
                word_set_choice = get_player_choice(['1', '2', '3'])
                word_sets = { '1': 'Animals', '2': 'Shapes', '3': 'Places' }
                word_set = word_sets[word_set_choice]
            else:
                word_set = None

            play_game(player_name, level, word_set)

        elif choice == '2':
            display_hall_of_fame()

        elif choice == '3':
            print_about()

        elif choice == '4':
            print("Thank you for playing HANGMAN!")
            break

if __name__ == "__main__":
    main()


# In[ ]:




