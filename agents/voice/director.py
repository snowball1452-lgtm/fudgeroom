"""The Director (ADR-0004): decides WHEN the Voice speaks in the fog.

Pure selection, no generation. For each perception event the Director
returns one of:

  speak — a matching, verified, off-cooldown sheet fact (returns diction)
  hold  — silence: confidence below floor, cooldown active, everything
          matching is in the repeat window, or nothing matches

Silence is the default state. A wrong advisory mid-firefight costs trust;
a silent moment costs nothing.
"""

from dataclasses import dataclass


@dataclass
class Decision:
    action: str            # "speak" | "hold"
    fact_id: str | None = None
    line: str | None = None
    reason: str = ""


class Director:
    def __init__(self, sheet: dict):
        self.sheet = sheet
        p = sheet["policies"]
        self.min_gap = p.get("min_gap_s", 45.0)
        self.repeat_window = p.get("repeat_window_s", 3600.0)
        self.confidence_floor = p.get("confidence_floor", 0.6)
        self._last_speak: float | None = None
        self._used: dict[str, float] = {}   # fact_id -> t_stream last used

    def decide(self, event: dict) -> Decision:
        t = event.get("t_stream", 0.0)
        conf = event.get("confidence", 1.0)

        if conf < self.confidence_floor:
            return Decision("hold", reason=f"confidence {conf:.2f} below floor")
        if self._last_speak is not None and t - self._last_speak < self.min_gap:
            return Decision("hold", reason="cooldown")

        tags = set(event.get("tags", []))
        for fact in self.sheet["facts"]:
            if not tags & set(fact.get("tags", [])):
                continue
            if t - self._used.get(fact["id"], -1e12) < self.repeat_window:
                continue
            self._used[fact["id"]] = t
            self._last_speak = t
            return Decision(
                "speak", fact_id=fact["id"], line=fact["diction"]["inner"],
                reason="tag match, off cooldown",
            )
        return Decision("hold", reason="no fresh matching fact")
