"""Knower ingest — spec §3.1/3.2, R0 slice.

Taps MediaMTX paths via ffmpeg, stamps events in the t_stream clock domain,
and writes them to the shared event bus (stdout lines for R0; MeshOS adapter
lands in R2). Perception here is a placeholder label pass — the point of R0
is to prove the LOOP and its latency, not the intelligence.
"""

import json
import subprocess
import sys
from collections import deque

from common.clock import StreamClock

MTX = "rtsp://localhost:8554"

# R0 perceptual cadence: sample the glasses feed this often (seconds).
# Spec §7.2 gives perception a 200ms target / 500ms ceiling; we sample
# coarser than that in R0 because the placeholder pass is cheap and the
# voice is what must hit budget.
FRAME_INTERVAL = 1.0


def tap(path: str, clock: StreamClock, bus: deque) -> None:
    """Continuously sample frames/audio from a MediaMTX path into events."""
    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", f"{MTX}/{path}",
        "-vf", f"fps=1/{FRAME_INTERVAL}",
        "-f", "null", "-",   # R0: discard pixels; hook vision model here
        "-progress", "-", "-nostats",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for line in proc.stdout:
        line = line.decode(errors="ignore").strip()
        if line.startswith("frame="):
            ev = {"type": f"perception.sample", "source": path}
            bus.append(clock.stamp_event(ev))
            print(json.dumps(bus[-1]), flush=True)


def main() -> None:
    clock = StreamClock()
    bus: deque = deque(maxlen=4096)
    print(json.dumps({"type": "stream.start", **clock.stamp_event({})}), flush=True)
    try:
        tap("glasses", clock, bus)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
