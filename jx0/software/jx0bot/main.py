"""JX0 main program: listen -> think (Claude) -> speak and move.

On the robot (Raspberry Pi 4):   python -m jx0bot.main
On a PC, with the simulated body: python -m jx0bot.main --sim --text      (type instead of talking; MuJoCo viewer opens)
Hold the push-to-talk button (or say "hey robot"), speak, release; JX0 answers out loud and moves when asked.
"""
from __future__ import annotations

import argparse
import threading

from .brain import Brain
from .robot import REST_ARMS, HardwareIO, Robot, SimIO, load_config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true", help="simulated body (MuJoCo) instead of the servos")
    ap.add_argument("--text", action="store_true", help="type to JX0 instead of using the microphone")
    ap.add_argument("--no-viewer", action="store_true")
    ap.add_argument("--no-face", action="store_true")
    a = ap.parse_args()
    cfg = load_config()

    io = SimIO(cfg, viewer=not a.no_viewer) if a.sim else HardwareIO(cfg)
    robot = Robot(io, cfg)
    if a.sim:
        io.settle({**robot.stand_pose, **REST_ARMS})
    robot.stand()

    face = None
    if not a.no_face:
        from .face import Face
        face = Face(cfg["face"], backend="none" if a.sim else cfg["face"]["backend"])
        face.start()

    if a.text:
        speak = print_and_say(face)
    else:
        from .voice import Speaker
        speaker = Speaker(on_level=face.mouth if face else None)
        speak = speaker.say

    def act(name, args):
        if face:
            face.set_mood("happy" if name == "wave" else "busy")
        try:
            return robot.act(name, args)
        finally:
            if face:
                face.set_mood("idle")

    brain = Brain(act=act, on_sentence=speak)
    speak("Hi, I am J X zero. Ask me anything, or tell me to wave or walk.")

    if a.text:
        while True:
            try:
                line = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if line:
                brain.reply(line)
    else:
        from gpiozero import Button
        from .voice import Listener
        listener = Listener()
        button = Button(cfg["voice"]["talk_button_gpio"], pull_up=True)
        while True:
            rest = listener.wait_for_wake(button)
            if face:
                face.set_mood("listening")
            text = rest or listener.listen(timeout_s=8.0)
            if face:
                face.set_mood("idle")
            if text:
                print(f"heard: {text}")
                brain.reply(text)
    io.close()


def print_and_say(face):
    """Text mode: print the reply, and try to speak it too when a TTS engine is available."""
    import queue
    try:
        from .voice import Speaker
        sp = Speaker(on_level=face.mouth if face else None)
    except Exception:
        sp = None
    q: queue.Queue = queue.Queue()

    def worker():                                      # one sentence at a time, in order
        while True:
            sp.say(q.get())

    if sp is not None:
        threading.Thread(target=worker, daemon=True).start()

    def say(s):
        print(f"JX0: {s}")
        if sp is not None:
            q.put(s)
    return say


if __name__ == "__main__":
    main()
