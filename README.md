# Hangman Project README

This document explains the purpose of each file, how they work together, and how to compile and run the project.

## Directory Structure

### Assets
- **Assets/sticks/...**  
  Contains hangman images used for the visual representation of the game.
  
- **Assets/words/...**  
  Holds all pre-defined word lists used by the game.

### Source Code
- **src/test/**  
  Contains code used exclusively for testing purposes. These files are not part of the program's runtime.

- **src/accessiblewordlistdialog/**  
  Implements the functionality for creating a custom word list through a dedicated window.

- **src/app.py**  
  The main entry point of the program. It manages the main screen, end screen, and command screen functionality.

- **src/hangman.py**  
  Defines the `Hangman` class, which stores hangman game data and handles core hangman logic.

- **src/audio_accessibility.py**  
  Handles all audio-related accessibility features, including voice assistance, input, and feedback.

- **src/theme.py**  
  Contains the `Theme` class, which defines all theme color data for the application.

- **src/word_grade_classifier.py**  
  Generates word lists categorized by grade levels (K-12).

- **src/word_list.py**  
  Allows users to create and manage custom word lists.

### Documentation
- **GitCommands.md**  
  Lists commonly used Git commands for version control.

- **Requirements.md**  
  Details the program's requirements, including dependencies and specifications.

- **SetUp.md**  
  Provides detailed instructions for setting up the program.

### Scripts
- **install.sh**  
  Shell script for setting up the environment. It installs all necessary dependencies and configures the system.

- **uninstall.sh**  
  Shell script for uninstalling the program and cleaning up the environment.

## How the Files Work Together
1. **Assets** provide the resources (images and words) required by the program during execution.
2. **app.py** serves as the central controller, invoking different components as needed:
   - `hangman.py` for game logic.
   - `audio_accessibility.py` for accessibility features.
   - `theme.py` to apply visual styling.
3. **word_list.py** and **word_grade_classifier.py** handle word management.
4. User-created word lists are generated through the `accessiblewordlistdialog` module.
5. Test files in `src/test/` can be used during development to verify functionality.

## How to Compile and Run
### Prerequisites
- Python 3.x installed.
- Necessary dependencies listed in `Requirements.md`.

### Setup
1. Run the setup script to install dependencies:
   ```bash
   ./install.sh
