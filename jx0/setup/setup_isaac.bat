@echo off

rem ============================================================================================================

rem  JX0 - one-time setup of Isaac Sim 5.1 + Isaac Lab 2.3.2 for training the JX0 walking policy (Windows 10/11).

rem  Run from anywhere:   jx0\setup\setup_isaac.bat

rem  Needs: an NVIDIA RTX GPU (8 GB+ VRAM; 24 GB is plenty), a recent NVIDIA driver, git, ~60 GB free disk,

rem         internet. Everything goes into <repo>\.isaac (git ignores it); nothing else on the PC is changed.

rem  Then train with:     jx0\setup\train_isaac.bat

rem ============================================================================================================

setlocal EnableExtensions EnableDelayedExpansion

pushd "%~dp0..\.."

set "REPO=%CD%"

set "ISAAC=%REPO%\.isaac"

set "VENV=%ISAAC%\env_isaaclab"

set "LAB=%ISAAC%\IsaacLab"

echo.

echo == JX0 Isaac Lab setup in %ISAAC%



rem ---- 1. the machine

where git >nul 2>&1 || (echo [x] git is not installed: https://git-scm.com/download/win & goto :fail)

nvidia-smi >nul 2>&1 || (echo [x] nvidia-smi not found: install the NVIDIA driver first & goto :fail)

for /f "tokens=*" %%g in ('nvidia-smi --query-gpu^=name^,memory.total^,driver_version --format^=csv^,noheader') do echo [ok] GPU: %%g

py -3.11 --version >nul 2>&1

if errorlevel 1 (

  echo [!] Python 3.11 is needed ^(Isaac Sim 5.x runs on Python 3.11 only^).

  set /p ANS="    Install Python 3.11 now with winget? [Y/N] "

  if /I not "!ANS!"=="Y" (echo     Install it from https://www.python.org/downloads/release/python-3119/ and run this again. & goto :fail)

  winget install -e --id Python.Python.3.11 || goto :fail

  py -3.11 --version >nul 2>&1 || (echo [x] Python 3.11 still not found - open a new terminal and run this again & goto :fail)

)

for /f "tokens=*" %%v in ('py -3.11 --version') do echo [ok] %%v

reg query "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled 2>nul | find "0x1" >nul

if errorlevel 1 echo [!] Windows long paths are off: if pip fails with a path error, enable them ^(admin^): https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation



rem ---- 2. the Python environment

if not exist "%ISAAC%" mkdir "%ISAAC%"

if not exist "%VENV%\Scripts\python.exe" (

  echo == creating %VENV%

  py -3.11 -m venv "%VENV%" || goto :fail

)

call "%VENV%\Scripts\activate.bat" || goto :fail

python -m pip install --upgrade pip || goto :fail



rem ---- 3. Isaac Sim 5.1 (pip) and PyTorch 2.7 (CUDA 12.8) - Isaac Lab 2.3's documented versions

echo == installing Isaac Sim 5.1.0 (several GB, 10-30 min)

pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com || goto :fail

pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128 || goto :fail



rem ---- 4. Isaac Lab 2.3.2 + rsl_rl

if not exist "%LAB%\isaaclab.bat" (

  echo == cloning Isaac Lab v2.3.2

  git clone --branch v2.3.2 --depth 1 https://github.com/isaac-sim/IsaacLab.git "%LAB%" || goto :fail

)

call "%LAB%\isaaclab.bat" --install rsl_rl || goto :fail



rem ---- 5. what the export and the MuJoCo test suite need

pip install mujoco onnx onnxruntime onnxscript pyyaml pillow || goto :fail



rem ---- 6. the NVIDIA Omniverse licence (Isaac Sim will not start without it)

if not exist "%ISAAC%\eula_accepted.txt" (

  echo.

  echo Isaac Sim asks you to accept the NVIDIA Omniverse License Agreement:

  echo   https://docs.isaacsim.omniverse.nvidia.com/latest/common/NVIDIA_Omniverse_License_Agreement.html

  set /p EULA="Type YES to accept it: "

  if /I not "!EULA!"=="YES" (echo Not accepted - Isaac Sim cannot run. & goto :fail)

  echo accepted %DATE% %TIME% > "%ISAAC%\eula_accepted.txt"

)

set OMNI_KIT_ACCEPT_EULA=YES



rem ---- 7. a smoke test: 2 training iterations, 64 robots (the first start downloads extensions: ~10 min)

echo == smoke test: 2 iterations of Isaac-Velocity-Flat-JX0-Full-v0

set "JX_TASK_CONFIG=jx0/rl/config/jx0_walk17.yaml"

call "%LAB%\isaaclab.bat" -p "%REPO%\simulation\isaac\isaaclab\scripts\train.py" --task Isaac-Velocity-Flat-JX0-Full-v0 --headless --num_envs 64 --max_iterations 2 || goto :fail



echo.

echo == SETUP DONE. Train with:  jx0\setup\train_isaac.bat

popd

exit /b 0



:fail

echo.

echo == SETUP STOPPED (see the message above). Fix it and run jx0\setup\setup_isaac.bat again - finished steps are skipped.

popd

exit /b 1

