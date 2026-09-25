# ADR-0003: One t_stream Clock Domain

**Status:** Accepted (spec v0.1.0, §7.1)

## Context

Cross-feed reasoning (what did the streamer see, say, and hear at moment X)
fails on wall-clock skew between glasses, capture rig, chat APIs, and TTS.

## Decision

All feeds normalize to one monotonic stream clock, `t_stream`, anchored at
stream start (see `common/clock.py`). Every graph event carries `t_stream`;
MeshOS event order is causal order. Wall-clock mapping is recorded
(`t_wall`) but never used for cross-feed reasoning — only for VOD mapping.

## Consequences

- "The whole stack in sync" (spec §7.3) becomes a query, not a
  re-transcription project.
- Perception, voice, and clip-cutting all reason in the same domain.
- Reconnects (glasses drops, RTSP re-anchor) need a policy for gaps —
  tracked as open question 1 in the spec.
