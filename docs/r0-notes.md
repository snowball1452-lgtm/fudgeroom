# R0 Notes — Real vs Stub (honest status)

R0 exists to prove the inner loop and measure it, not to be smart.

| Piece | Status |
|---|---|
| MediaMTX topology (`infra/`) | real config, drop-in |
| t_stream clock (`common/clock.py`) | real |
| Ingest (`agents/knower/ingest.py`) | real ffmpeg tap; semantic perception is a placeholder label pass |
| Inner voice composer (`agents/voice/inner.py`) | real loop, placeholder diction policy |
| TTS (`agents/voice/tts.py`) | interface + sine-tone stub; wire VoxCPM/OmniRoute at R1 |
| Chat rollup (`agents/knower/rollup.py`) | real logic, stdin sim input |
| Latency harness (`tools/latency_harness.py`) | measures decide loop; TTS first-byte hook lands R1 |
| Chat connectors | stub (registry contract in `connectors/README.md`) |
| Foreman | not started (R2/R3, scope in `agents/foreman/README.md`) |

## Next steps

1. Point `tts.py` at VoxCPM via OmniRoute.
2. Replace placeholder perception with a vision model on sampled frames.
3. Instrument TTS first-byte in the latency harness; tune to the 800 ms
   target (spec §7.2).
