# JX0 software setup

JX0's program is `jx0/software/jx0bot`: it listens (Vosk, offline), thinks (Claude, over Wi-Fi), talks (Piper, offline),
shows a face on the round screen, and moves: verified walking gaits with IMU balance, waving, nodding, looking around,
and taking and giving things with its gripper hands.

## Try it on a PC first (no robot needed)

The same program drives the simulated JX0, so you can talk to the robot before you buy anything.

```bash
pip install -r jx0/software/requirements-pc.txt
```

```bash
cd jx0/software && python -m jx0bot.main --sim --text
```

A MuJoCo window opens with JX0 standing. Type things like "wave at me", "walk forward four steps", "take this pen" or
"turn around". You need an Anthropic API key in the environment (`ANTHROPIC_API_KEY`; see "The brain" below).

To render the demo film without a key: `python jx0/sim/demo_jx0.py`.

## On the robot (Raspberry Pi 4)

### 1. System

Flash **Raspberry Pi OS (64-bit, Bookworm)** with Raspberry Pi Imager and set Wi-Fi, a user and SSH in its options.
Then on the Pi:

```bash
sudo raspi-config nonint do_i2c 0 && sudo raspi-config nonint do_spi 0
```

Add to `/boot/firmware/config.txt` (I2S audio for the INMP441 microphone and the MAX98357A amplifier):

```
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard
```

This overlay is the one commonly used for an INMP441 + MAX98357A pair on the Pi's I2S pins. It is **UNVERIFIED on
JX0**: after a reboot, `arecord -l` and `aplay -l` should both list the card. A USB microphone and a USB speaker work as
a fallback with no overlay at all.

```bash
sudo apt install -y git python3-venv espeak-ng libportaudio2 pigpio
```

```bash
sudo systemctl enable --now pigpiod
```

(If `pigpio` is not in your apt sources, build it from its GitHub repository `joan2937/pigpio`.)

### 2. Code and Python packages

```bash
git clone https://github.com/nickthelegend/thenar-jx1.git ~/thenar-jx1
```

```bash
python3 -m venv --system-site-packages ~/jx0env && source ~/jx0env/bin/activate
```

```bash
pip install -r ~/thenar-jx1/jx0/software/requirements-pi.txt
```

### 3. Voice models (offline)

Put both in `jx0/software/jx0bot/models/`:

- Speech recognition: **vosk-model-small-en-us-0.15** (about 40 MB) from the Vosk models page, alphacephei.com/vosk/models.
  Unzip it so the folder is `models/vosk-model-small-en-us-0.15/`.
- Voice: **en_US-lessac-medium** Piper voice (the `.onnx` file and its `.onnx.json`, about 60 MB) from the
  `rhasspy/piper-voices` repository on Hugging Face. Without it JX0 falls back to eSpeak-NG, which works but sounds
  robotic.

### 4. The brain (Claude)

JX0 sends what it hears to Claude and speaks the answer. Create an API key in the Anthropic Console, then on the Pi:

```bash
echo 'export ANTHROPIC_API_KEY=your-key-here' >> ~/.bashrc && source ~/.bashrc
```

Never commit the key to the repository. The model is `claude-opus-5` (set `JX0_MODEL` to use another one). Replies are
kept to one to three spoken sentences, so each answer costs very little.

### 5. Run

```bash
cd ~/thenar-jx1/jx0/software && python -m jx0bot.main
```

Hold the push-to-talk button (or say "hey robot"), speak, and let go. `--text` lets you type instead of talking, which
is handy over SSH. Do the [bring-up](bringup.md) first: the servo IDs, zero pose and directions must be in config.yaml
before the legs are powered.

### 6. Start on boot (optional)

`/etc/systemd/system/jx0.service`:

```ini
[Unit]
Description=JX0 robot
After=network-online.target pigpiod.service

[Service]
User=pi
WorkingDirectory=/home/pi/thenar-jx1/jx0/software
Environment=ANTHROPIC_API_KEY=your-key-here
ExecStart=/home/pi/jx0env/bin/python -m jx0bot.main
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now jx0
```

## What each file does

| File | Job |
|---|---|
| `main.py` | wires everything together: listen, then think, then speak and move |
| `brain.py` | Claude conversation with streaming speech and the robot's tools (wave, nod, walk, turn, look, hand) |
| `voice.py` | Vosk listener (button or wake phrase) and the Piper / eSpeak speaker with mouth-level callback |
| `face.py` | the eyes and mouth on the round screen (idle, listening, busy, happy, talking) and the display self-test |
| `robot.py` | joint I/O for the real robot or the simulation; gait playback with IMU balance; all actions |
| `servo_bus.py` | Feetech STS serial protocol for the ST3215 leg servos |
| `imu.py` | MPU6050 driver with a complementary filter |
| `calibrate.py` | servo IDs, centring, zero pose, joint directions, stiffness check |
| `config.yaml` | servo IDs, directions, zero ticks, GPIO pins, balance gains, display settings |
| `gaits/*.json` | 50 Hz leg trajectories that passed the closed-loop simulation check (`jx0/sim/walk_jx0.py`) |
