source "C:/ProgramData/anaconda3/etc/profile.d/conda.sh"
conda create -n FINAL python=3.9
conda activate FINAL

pip install pyttsx3
pip install SpeechRecognition
platform_name=$(python mac_machine_checker.py)
echo $platform_name
if [ "$platform_name" == "darwin" ]; then
    brew install portaudio
fi
pip install pyaudio
pip install PyQt6