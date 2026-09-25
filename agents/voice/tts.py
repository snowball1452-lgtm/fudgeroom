"""TTS adapter — spec §4.2.

Interface for streaming TTS (VoxCPM / VibeVoice-class via OmniRoute).
R0 ships a stub that synthesizes a placeholder tone so the WebRTC earpiece
path is exercisable end-to-end. Swap `synthesize_to_rtsp` internals; keep
the signature — the first-byte latency of this function is the inner-loop
budget (spec §7.2), so it must stream, never batch.
"""

import subprocess

MTX = "rtsp://localhost:8554"


def synthesize_to_rtsp(text: str, path: str = "inner") -> None:
    """Speak `text` to MediaMTX at /path.

    Real implementation (R1):
        tokens = omniroute.stream("tts-model", text)
        pipe PCM chunks into an RTSP publish as they arrive.

    R0 stub: a short sine tone per utterance, so the earpiece path works.
    """
    duration = min(0.3 + 0.05 * len(text), 2.5)
    subprocess.run(
        [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"sine=frequency=660:duration={duration:.2f}",
            "-c:a", "aac",
            "-f", "rtsp",
            f"{MTX}/{path}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _ = text  # diction arrives with the real TTS engine
