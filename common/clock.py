"""t_stream clock domain — spec §7.1.

All feeds normalize to one monotonic stream clock anchored at stream start.
Wall clock is recorded but never used for cross-feed reasoning.
"""

import time
from dataclasses import dataclass, field


@dataclass
class StreamClock:
    """Monotonic stream clock. One instance per live session."""

    anchor_wall: float = field(default_factory=time.time)
    _t: float = 0.0  # monotonic seconds since anchor

    def now(self) -> float:
        return time.monotonic() - self._anchor_mono()

    def _anchor_mono(self) -> float:
        # cache the monotonic anchor; wall anchor kept for VOD mapping only
        a = getattr(self, "_mono", None)
        if a is None:
            a = time.monotonic()
            object.__setattr__(self, "_mono", a)
        return a

    def stamp_event(self, event: dict) -> dict:
        """Return event with t_stream and wall mapping attached."""
        t = self.now()
        return {
            **event,
            "t_stream": round(t, 3),
            "t_wall": round(time.time(), 3),
        }
