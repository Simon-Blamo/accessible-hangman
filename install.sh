platform_name=$(python ./src/mac_machine_checker.py)
if [ "$platform_name" == "win32" ]; then
    source "C:/ProgramData/anaconda3/etc/profile.d/conda.sh"
fi
conda create -n FINAL python=3.9
