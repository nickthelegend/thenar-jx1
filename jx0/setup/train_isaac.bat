@echo off

rem ============================================================================================================

rem  JX0 - train the whole-body walking policy in Isaac Lab, export it and test it in MuJoCo.

rem    jx0\setup\train_isaac.bat [iterations] [robots]          default 3000 iterations, 4096 robots

rem  The policy: 17 joint corrections (all STS3215 servos) at 50 Hz from 176 observations (3 frames of history);

rem  task file jx0\rl\config\jx0_walk17.yaml. Needs jx0\setup\setup_isaac.bat first.

rem  Result: jx0\rl\policies\jx0_walk17_isaac\ (policy.onnx, policy.pt, policy_io.yaml, sim2sim.json = test results)

rem ============================================================================================================

setlocal EnableExtensions EnableDelayedExpansion

pushd "%~dp0..\.."

set "REPO=%CD%"

set "ISAAC=%REPO%\.isaac"

set "LAB=%ISAAC%\IsaacLab"

set "ITERS=%~1"

if "%ITERS%"=="" set ITERS=3000

set "ENVS=%~2"

if "%ENVS%"=="" set ENVS=4096

if not exist "%ISAAC%\eula_accepted.txt" (echo Run jx0\setup\setup_isaac.bat first. & popd & exit /b 1)

call "%ISAAC%\env_isaaclab\Scripts\activate.bat" || (popd & exit /b 1)

set OMNI_KIT_ACCEPT_EULA=YES

set "JX_TASK_CONFIG=jx0/rl/config/jx0_walk17.yaml"



echo == training %ITERS% iterations with %ENVS% robots (started %TIME%)

call "%LAB%\isaaclab.bat" -p "%REPO%\simulation\isaac\isaaclab\scripts\train.py" --task Isaac-Velocity-Flat-JX0-Full-v0 --headless --num_envs %ENVS% --max_iterations %ITERS%

if errorlevel 1 (echo Training stopped with an error. & popd & exit /b 1)

echo == training finished %TIME%



rem ---- the newest checkpoint of the newest run

for /f "delims=" %%c in ('python "%REPO%\jx0\setup\latest_checkpoint.py" jx0_full17') do set "CKPT=%%c"

if not defined CKPT (echo No checkpoint found. & popd & exit /b 1)

echo == checkpoint %CKPT%



set "OUT=%REPO%\jx0\rl\policies\jx0_walk17_isaac"

python "%REPO%\simulation\isaac\isaaclab\scripts\export_offline.py" --checkpoint "%CKPT%" --out "%OUT%" || (popd & exit /b 1)



echo == testing on the verified MuJoCo model: speeds, pushes, 60 s endurance, latency

python "%REPO%\jx0\rl\sim2sim_jx0.py" --policy "%OUT%"

python "%REPO%\jx0\rl\sim2sim_jx0.py" --policy "%OUT%" --video "%OUT%\endurance.mp4"

echo == clearance: the policy's poses on the real parts (the MuJoCo model has no leg-on-leg contact)

python "%REPO%\jx0\rl\policy_clearance.py" --policy "%OUT%"

echo.

echo == done: %OUT%   (watch it live: python jx0\rl\play_jx0.py --policy "%OUT%")

popd

exit /b 0

