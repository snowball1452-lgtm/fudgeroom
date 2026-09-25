"""Chat rollup stub — spec §3.2 step 3.

Chat is a rate problem, not a comprehension problem. R0 simulates chat on
stdin (one message per line) to prove the rollup shape the Voice will read.
Twitch/YouTube/Discord connectors land per spec §3.3.
"""

import json
import re
import sys
import time
from collections import Counter, deque

WINDOW = 10.0  # rollup window seconds
QUESTION_RE = re.compile(r"\?|how do|what('s| is)|where|when|why", re.I)


class Rollup:
    def __init__(self, window: float = WINDOW) -> None:
        self.window = window
        self.buf: deque = deque()  # (t_stream, text)

    def add(self, t_stream: float, text: str) -> None:
        self.buf.append((t_stream, text))
        self._trim(t_stream)

    def _trim(self, now: float) -> None:
        while self.buf and now - self.buf[0][0] > self.window:
            self.buf.popleft()

    def summarize(self, now: float) -> dict:
        self._trim(now)
        msgs = [t for _, t in self.buf]
        words = Counter(w.lower() for m in msgs for w in m.split() if len(w) > 3)
        return {
            "type": "chat.rollup",
            "n": len(msgs),
            "top_terms": [w for w, _ in words.most_common(5)],
            "questions": sum(1 for m in msgs if QUESTION_RE.search(m)),
            "recent": msgs[-3:],
        }


def main() -> None:
    rollup = Rollup()
    t = 0.0
    for line in sys.stdin:
        t += 0.5  # sim clock until StreamClock is wired through the bus
        rollup.add(t, line.strip())
        print(json.dumps(rollup.summarize(t)), flush=True)


if __name__ == "__main__":
    main()
