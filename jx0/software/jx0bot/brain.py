"""JX0's conversation brain: Claude over the Anthropic Python SDK, streamed sentence by sentence to the voice.

- Model: claude-opus-5 (override with JX0_MODEL), low effort for short spoken replies.
- Streaming: text deltas are cut into sentences and handed to `on_sentence` as soon as each one ends, so the robot
  starts speaking while the rest of the reply is still being generated.
- Robot actions are client tools (wave, nod, walk, turn, look). Inputs stream eagerly, so every input is validated
  here before the action runs; a turn cut off by max_tokens or a refusal never runs its tools.
- Refusal fallbacks are enabled server-side (`fallbacks: "default"`), so a declined request is retried on the model
  Anthropic recommends instead of coming back empty.
Credentials: ANTHROPIC_API_KEY (or an `ant auth login` profile) on the Pi.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Callable

import anthropic

MODEL = os.environ.get("JX0_MODEL", "claude-opus-5")
MAX_TOKENS = 8000            # replies are 1-3 spoken sentences; this leaves room for adaptive thinking
MAX_HISTORY_TURNS = 20       # keep the conversation short: older turns are dropped in user/assistant pairs

SYSTEM_PROMPT = """You are JX0, a small walking humanoid robot (about 45 cm tall) built by a student in India from \
3D-printed parts and hobby servos. You talk out loud through a small speaker, so:
- Answer in one to three short spoken sentences. No lists, no markdown, no emoji, no URLs.
- Be warm, curious and a little playful. You are proud of being a home-built robot and happy to explain how you work.
- You can move. Use the tools when the user asks you to, or when a small gesture fits (a wave hello, a nod). Walking \
is slow and wobbly: at most 10 steps per request, and only when asked.
- If you are unsure what the user said, ask them to repeat it."""

SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

TOOLS = [
    {"name": "wave", "description": "Wave one arm, e.g. to greet someone or say goodbye.", "eager_input_streaming": True,
     "input_schema": {"type": "object", "properties": {"arm": {"type": "string", "enum": ["left", "right"]}},
                      "required": ["arm"], "additionalProperties": False}},
    {"name": "nod", "description": "Nod the head yes, or shake it no.", "eager_input_streaming": True,
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["yes", "no"]}},
                      "required": ["kind"], "additionalProperties": False}},
    {"name": "walk", "description": "Walk forward or backward a number of steps (slow, about 4 cm per step).",
     "eager_input_streaming": True,
     "input_schema": {"type": "object", "properties": {
         "steps": {"type": "integer", "minimum": 1, "maximum": 10},
         "direction": {"type": "string", "enum": ["forward", "backward"]}},
         "required": ["steps", "direction"], "additionalProperties": False}},
    {"name": "turn", "description": "Turn in place by an angle in degrees (positive = left).", "eager_input_streaming": True,
     "input_schema": {"type": "object", "properties": {"degrees": {"type": "integer", "minimum": -180, "maximum": 180}},
                      "required": ["degrees"], "additionalProperties": False}},
    {"name": "look", "description": "Turn the head to look left, right or straight ahead.", "eager_input_streaming": True,
     "input_schema": {"type": "object", "properties": {"direction": {"type": "string", "enum": ["left", "right", "center"]}},
                      "required": ["direction"], "additionalProperties": False}},
]
_SCHEMAS = {t["name"]: t["input_schema"] for t in TOOLS}


def validate(name: str, args) -> str | None:
    """Check a streamed tool input against its schema (the server does not validate eagerly streamed inputs).
    Returns None when valid, otherwise the reason."""
    schema = _SCHEMAS.get(name)
    if schema is None:
        return f"unknown tool {name!r}"
    if not isinstance(args, dict):
        return "input is not an object"
    props = schema["properties"]
    for key in schema["required"]:
        if key not in args:
            return f"missing {key!r}"
    for key, value in args.items():
        spec = props.get(key)
        if spec is None:
            return f"unexpected field {key!r}"
        if "enum" in spec and value not in spec["enum"]:
            return f"{key} must be one of {spec['enum']}"
        if spec["type"] == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return f"{key} must be an integer"
            if not spec.get("minimum", value) <= value <= spec.get("maximum", value):
                return f"{key} out of range"
        if spec["type"] == "string" and not isinstance(value, str):
            return f"{key} must be a string"
    return None


@dataclass
class Brain:
    """One conversation. `act(name, args) -> str` runs a robot action and returns a short result for the model."""
    act: Callable[[str, dict], str]
    on_sentence: Callable[[str], None]
    client: anthropic.Anthropic = field(default_factory=anthropic.Anthropic)
    messages: list = field(default_factory=list)

    def _trim(self):
        # drop the oldest user/assistant pairs, but never split a tool_use from its tool_result
        while len(self.messages) > 2 * MAX_HISTORY_TURNS:
            del self.messages[:2]
            while self.messages and (self.messages[0]["role"] != "user" or _has_tool_result(self.messages[0])):
                del self.messages[0]

    def _stream_turn(self):
        """One model call; speaks sentences as they complete. Returns the final message."""
        buf = ""
        with self.client.beta.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=self.messages,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            for event in stream:
                if event.type == "text":
                    buf += event.text
                    parts = SENTENCE_END.split(buf)
                    for sentence in parts[:-1]:
                        if sentence.strip():
                            self.on_sentence(sentence.strip())
                    buf = parts[-1]
            final = stream.get_final_message()
        if buf.strip() and final.stop_reason != "refusal":
            self.on_sentence(buf.strip())
        return final

    def reply(self, user_text: str, max_tool_rounds: int = 4) -> None:
        """Handle one thing the user said: stream the spoken reply and run any requested actions."""
        self.messages.append({"role": "user", "content": user_text})
        json_retries = 0
        for _ in range(max_tool_rounds + 1):
            try:
                final = self._stream_turn()
            except ValueError:
                # a streamed tool input the SDK could not parse at all: re-issue the turn (bounded)
                json_retries += 1
                if json_retries > 2:
                    self.on_sentence("Sorry, I got my wires crossed. Could you say that again?")
                    self.messages.pop()
                    return
                continue
            json_retries = 0
            self.messages.append({"role": "assistant", "content": final.content})
            if final.stop_reason == "refusal":
                self.on_sentence("I'd rather not do that one.")
                break
            tool_uses = [b for b in final.content if b.type == "tool_use"]
            if not tool_uses:
                break
            if final.stop_reason == "max_tokens":   # a truncated tool input parses as a partial object: never run it
                results = [{"type": "tool_result", "tool_use_id": b.id, "is_error": True,
                            "content": "input was cut off; not executed"} for b in tool_uses]
            else:
                results = []
                for b in tool_uses:
                    problem = validate(b.name, b.input)
                    if problem:
                        results.append({"type": "tool_result", "tool_use_id": b.id, "is_error": True,
                                        "content": json.dumps({"INVALID_JSON": problem})})
                        continue
                    try:
                        results.append({"type": "tool_result", "tool_use_id": b.id, "content": self.act(b.name, b.input)})
                    except Exception as exc:  # a failed action (servo fault, fall) goes back to the model as an error
                        results.append({"type": "tool_result", "tool_use_id": b.id, "is_error": True, "content": str(exc)})
            self.messages.append({"role": "user", "content": results})   # all results of this turn in one message
        self._trim()


def _has_tool_result(msg) -> bool:
    content = msg.get("content")
    return isinstance(content, list) and any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content)


if __name__ == "__main__":   # text-only test on a PC: type to JX0, it prints what it would say and do
    def act(name, args):
        print(f"  [action] {name} {args}")
        return "done"

    brain = Brain(act=act, on_sentence=lambda s: print(f"JX0: {s}"))
    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if line:
            brain.reply(line)
