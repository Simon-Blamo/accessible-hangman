platform_name=$(python mac_machine_checker.py)

# Ensure conda is initialized correctly for different platforms
if [ "$platform_name" == "win32" ]; then
    source "C:/ProgramData/anaconda3/etc/profile.d/conda.sh"
elif [ "$platform_name" == "darwin" ]; then
    # Ensure conda is initialized for macOS
    source "$(conda info --base)/etc/profile.d/conda.sh"
fi


# Create the environment and activate it
conda create -n FINAL python=3.9 -y

# Use conda activate in the same shell session
# conda activate FINAL

# # Install necessary dependencies
# pip install pyttsx3
# pip install SpeechRecognition

# echo $platform_name

# # Platform-specific steps for macOS
# if [ "$platform_name" == "darwin" ]; then
#     brew install portaudio
# fi

# # Install additional packages
# pip install pyaudio
# pip install PyQt6
# pip install nltk
