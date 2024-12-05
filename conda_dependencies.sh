platform_name=$(python mac_machine_checker.py)

# Install necessary dependencies
pip install pyttsx3
pip install SpeechRecognition

# Platform-specific steps for macOS
if [ "$platform_name" == "darwin" ]; then
    brew install portaudio
fi

# Install additional packages
pip install pyaudio
pip install PyQt6
pip install nltk
