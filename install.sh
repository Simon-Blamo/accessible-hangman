platform_name=$(python mac_machine_checker.py)
if [ "$platform_name" == "win32" ]; then
    source "C:/ProgramData/anaconda3/etc/profile.d/conda.sh"
elif [ "$platform_name" == "darwin" ]; then
    # Ensure conda is initialized for macOS
    source "$(conda info --base)/etc/profile.d/conda.sh"
fi
conda create -n FINAL python=3.9
