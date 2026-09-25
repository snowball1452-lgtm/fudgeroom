# ADR-0002: MediaMTX Is the Single Media Router

**Status:** Accepted (spec v0.1.0, §6)

## Context

Feeds: glasses RTSP, game capture, OBS program, inner-voice TTS, recording
tap. Latency budgets differ per path (inner loop <800 ms; audience path may
eat RTMP's seconds). A bespoke capture layer per consumer would make the
latency budget unmeasurable.

## Decision

All media flows through MediaMTX. Every stream in the house is addressable as
a path (`/glasses`, `/game`, `/program`, `/inner`). Nothing captures
directly; everything subscribes. Inner voice rides MediaMTX's built-in WebRTC
(WHEP); the audience path rides RTMP through OBS and may lag.

## Consequences

- The latency budget (spec §7.2) is measurable per hop.
- Re-routing a consumer means changing a path, not rewriting capture code.
- WebRTC for the ear (not RTMP) is the difference between a voice in your
  head and a voice two seconds behind your eyes.
- Encryption is off for R0 LAN-only; tighten at R1.
