﻿# Set Up Accessible-Hangman
## Prerequisites
- [Python](https://www.python.org/): most recent versionc
- [Anaconda](https://www.anaconda.com/)
- [Git bash](https://git-scm.com/downloads)
## Getting Started
### Configuring Git Bash to Recognize Anaconda
1. Set up conda in Git Bash. Navigate to **conda.sh** in file explorer *(the default location is C:\ProgramData\anaconda3\etc\profile.d)*.
2. Open the directory in the Git Bash terminal with the context menu.
![Image](https://github.com/Simon-Blamo/accessible-hangman/blob/main/assets/000.png)
3. Run the following command in the terminal: `echo ". ${PWD}/conda.sh" >> ~/.bashrc`
4. Reopen Git Bash. The command, `conda`, should be recognized now.
### Setting up python environment for executable.
1. Open git bash terminal.
2. Run the command, `sh install.sh`, in the terminal.
3. Run the command, `conda activate FINAL`, to load virtual environment.
4. Run the command, `python app.py` to run the game!
### Deleting this project's virtual environment
1. Run the command, `sh uninstall.sh`, in the terminal.


