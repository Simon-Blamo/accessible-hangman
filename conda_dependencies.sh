# Platform-specific steps for macOS
platform_name=$(python ./src/mac_machine_checker.py)
if [ "$platform_name" == "darwin" ]; then
    brew install portaudio
fi
platform_name=$(py ./src/mac_machine_checker.py)
if [ "$platform_name" == "darwin" ]; then
    brew install portaudio
fi
platform_name=$(python3 ./src/mac_machine_checker.py)
if [ "$platform_name" == "darwin" ]; then
    brew install portaudio
fi

# Install necessary dependencies
pip install pyttsx3
pip install SpeechRecognition

# Install additional packages
pip install pyaudio
pip install PyQt6
pip install nltk
