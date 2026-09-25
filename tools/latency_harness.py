"""Latency harness — spec §7.2.

Measures the inner loop end-to-end on the R0 stub pipeline so the budget is
a histogram, not a hope. Stamps three points:

  ingest  — an event enters the bus
  decide  — the Voice has chosen what to say
  first_byte — TTS audio began publishing

Run standalone with simulated events, or pipe real knower output in:

  python -m agents.knower.ingest | python -m tools.latency_harness

Budget (spec §7.2): inner loop < 800 ms target, 1200 ms ceiling.
"""

import sys
import time
from collections import deque

from agents.voice.inner import compose

TARGET_MS = 800
CEILING_MS = 1200


def main() -> None:
    samples = deque(maxlen=512)
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        t_ingest = time.monotonic()
        try:
            import json
            event = json.loads(line)
        except ValueError:
            continue
        line_out = compose(event)
        t_decide = time.monotonic()
        if line_out is None:
            continue
        # TTS stub first byte is sub-ms; real engine streams. We record the
        # compose+dispatch cost and leave a tts_first_byte hook for R1.
        t_first = time.monotonic()
        samples.append((t_decide - t_ingest, t_first - t_ingest))

    if not samples:
        print("no decidable events")
        return
    decide_ms = sorted(s[0] * 1000 for s in samples)
    loop_ms = sorted(s[1] * 1000 for s in samples)

    def pct(v, p):
        return v[min(len(v) - 1, int(len(v) * p))]

    print(f"events: {len(samples)}")
    print(f"decide:  p50={pct(decide_ms,0.5):7.1f}ms  p95={pct(decide_ms,0.95):7.1f}ms")
    print(f"loop:    p50={pct(loop_ms,0.5):7.1f}ms  p95={pct(loop_ms,0.95):7.1f}ms"
          f"  (target {TARGET_MS}ms / ceiling {CEILING_MS}ms)")
    print("note: TTS first-byte not yet instrumented (stub); R1 wires it.")


if __name__ == "__main__":
    main()
