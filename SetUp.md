# Set Up Accessible-Hangman

## Prerequisites
- [Python](https://www.python.org/): most recent version
- [Anaconda](https://www.anaconda.com/): most recent version
- [Git bash](https://git-scm.com/downloads)

## Getting Started

### Configuring Git Bash to Recognize Anaconda
1. Set up conda in Git Bash. Navigate to **conda.sh** in file explorer *(the default location is C:\ProgramData\anaconda3\etc\profile.d)*.
2. Open the directory in the Git Bash terminal with the context menu.
![Image](https://github.com/Simon-Blamo/accessible-hangman/blob/main/assets/000.png)
3. Run the following command in the terminal: `echo ". ${PWD}/conda.sh" >> ~/.bashrc`
4. Reopen Git Bash. The command, `conda`, should be recognized now.

### Setting up python environment for executable
1. Clone repository: `git clone https://github.com/Simon-Blamo/accessible-hangman.git`. 
2. Open git bash terminal.
3. Run the command, `sh install.sh`, in the terminal.
5. Run the command, `conda activate FINAL`, to load virtual environment.
6. Run the command, `sh conda_dependencies.sh`, to install the required python packages.
7. Go to main branch: ```git checkout main```
8. Run the command, `python app.py` to run the game!

### Deleting this project's virtual environment
1. Run the command, `sh uninstall.sh`, in the terminal.
