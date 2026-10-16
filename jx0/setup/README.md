# Training JX0 on a lab PC (Isaac Lab)

**What you need:**
- Windows 10/11.
- An NVIDIA RTX GPU with 8 GB or more of VRAM. 24 GB is plenty.
- A recent NVIDIA driver.
- git.
- About 60 GB of free disk.
- An internet connection.

```bat
git clone https://github.com/nickthelegend/thenar-jx1.git
cd thenar-jx1
jx0\setup\setup_isaac.bat
jx0\setup\train_isaac.bat
```

## setup_isaac.bat (once, about 30–60 min, mostly downloads)

1. Checks for the GPU and the driver, git, and Python 3.11. It offers to install Python 3.11 with winget if it's missing.
2. Creates a Python environment in `.isaac\env_isaaclab`. Nothing outside the repo folder is touched.
3. Installs Isaac Sim 5.1.0 from pip and PyTorch 2.7 (CUDA 12.8), the versions Isaac Lab 2.3 documents.
4. Clones Isaac Lab v2.3.2 into `.isaac\IsaacLab` and installs it with rsl_rl.
5. Installs MuJoCo, ONNX and onnxruntime, for the export and the test suite.
6. Asks you to accept NVIDIA's Omniverse licence. Isaac Sim won't start without it, and the answer is saved in `.isaac\eula_accepted.txt`.
7. Runs a 2-iteration trial training. The very first Isaac Sim start downloads its extensions, which takes about 10 min.

If a step fails, fix the cause and run the script again; finished steps are skipped.

## train_isaac.bat [iterations] [robots]

```bat
jx0\setup\train_isaac.bat
```

The defaults are 3000 iterations and 4096 robots. A different run, for example `jx0\setup\train_isaac.bat 5000 8192`:

```bat
jx0\setup\train_isaac.bat 5000 8192
```

It does four things:
1. Trains `Isaac-Velocity-Flat-JX0-Full-v0` headless. Logs go to `simulation\isaac\isaaclab\logs\jx0_full17\<time>\`.
2. Exports the last checkpoint to `jx0\rl\policies\jx0_walk17_isaac\` (`policy.onnx`, `policy.pt`, `policy_io.yaml`).
3. Tests it on the verified MuJoCo model: speeds, pushes, the 60 s endurance run and latency. Results go to `sim2sim.json`, ending in PASS or FAIL.
4. Films the endurance run to `endurance.mp4`.

To watch the policy live and drive it with the keyboard:

```bat
python jx0\rl\play_jx0.py --policy jx0\rl\policies\jx0_walk17_isaac
```

## The policy

| | |
|---|---|
| Rate | 50 Hz |
| Outputs | 17 joint corrections, one per STS3215: target = walking stance + 0.25 × output (rad) |
| Inputs | 176 values: body rotation rate, gravity direction, the 17 joint angles, speeds and last outputs, each over the last 3 control steps (0.06 s); the speed command; the gait clock |
| Task file | `jx0\rl\config\jx0_walk17.yaml`: rewards, randomisation (servo stiffness 0.7–1.3×, latency 2–12 ms, pushes, friction, mass) and PPO |
| Robot | `jx0\description\urdf\jx0.urdf`, checked against the verified model by `jx0\description\check_description.py` |

## What to expect

The same task trained in MuJoCo on the design laptop gave `jx0_walk17_v5`, which passes the whole test suite at iteration 1500 (1024 robots). With 4096 robots, Isaac Lab sees 4× more data per iteration, so 1500–3000 iterations should be plenty. Isaac's physics differs from MuJoCo's, so check the `sim2sim.json` that `train_isaac.bat` writes. If it says FAIL, train longer (`train_isaac.bat 5000`).

## How long training takes (estimate)

One iteration is 4096 robots × 24 steps, about 98,000 simulation steps. Isaac Lab runs legged-robot tasks on one RTX 4090 at roughly 70,000–150,000 steps/s. JX0 is a small robot (17 joints, 18 bodies), so it should be at the fast end of that range. These numbers are estimates: nothing has been run in Isaac Sim here.

| GPU (24 GB) | ~ per iteration | 3000 iterations |
|---|---|---|
| RTX 4090 | 0.7–1.2 s | **35–60 min** |
| RTX 3090 / A5000 | 1.0–1.8 s | **50–90 min** |

Add 3–5 min for the start-up. The first run ever also needs about 10 min of extension downloads, which `setup_isaac.bat` already covers.

For comparison, the same task in MuJoCo on the design laptop (12 CPU threads, RTX 3050) runs at about 18,000 steps/s, so 3000 iterations take about 70 min.
