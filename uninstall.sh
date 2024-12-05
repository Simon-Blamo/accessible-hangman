platform_name=$(python mac_machine_checker.py)
if [ "$platform_name" == "win32" ]; then
  source "C:/ProgramData/anaconda3/etc/profile.d/conda.sh"
fi
conda deactivate
conda remove -n FINAL --all
