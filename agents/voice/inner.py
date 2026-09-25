"""Inner voice — spec §4.1 inner plane, R0 slice.

Reads perception/chat events from the bus, composes a short advisory line
(Ratatouille rule: advisory-to-the-hands-in-motion, never conversational
theater), and pushes it as TTS audio to MediaMTX /inner.

R0 policy is a placeholder: react to notable events with canned lines.
The policy slot is where the persona object + taste ranking (spec §4.3)
lands in R1.
"""

import json
import subprocess
import sys
from collections import deque

from .tts import synthesize_to_rtsp

# R0 placeholder diction. One breath, no questions, coach-don't-narrate.
LINES = {
    "perception.sample": None,  # too frequent to speak every sample
    "stream.start": "Eyes on. I'm with you.",
    "chat.rollup": "Chat's moving.",  # upgraded when rollup gets terms
}


def compose(event: dict) -> str | None:
    line = LINES.get(event.get("type"))
    if line is None:
        return None
    if event.get("type") == "chat.rollup" and event.get("top_terms"):
        line = f"Heads up, chat's on {event['top_terms'][0]}."
    return line


def main() -> None:
    for raw in sys.stdin:
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        line = compose(event)
        if line:
            print(json.dumps({"type": "voice.inner", "text": line,
                              **event}), flush=True)
            synthesize_to_rtsp(line, path="inner")


if __name__ == "__main__":
    main()
