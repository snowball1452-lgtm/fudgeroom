# ADR-0001: The Two-Voice Split

**Status:** Accepted (spec v0.1.0, §4.1)

## Context

The cohost needs to talk to two audiences with opposite latency and persona
requirements: the streamer (private, <800 ms, taste-gated only) and the
audience (public, seconds are fine, full persona). The obvious design is two
separate agents with two personas.

## Decision

One persona, two output planes, generated in **one inference pass** with
plane-labeled outputs. Inner plane and broadcast plane share the same context
and read of the room; they differ in diction level and routing.

## Consequences

- Prevents the classic failure mode where the private agent tells the
  streamer something the public agent contradicts seconds later.
- The broadcast plane's TTS text is written to MeshOS as the authoritative
  public utterance (no re-transcription drift, spec §7.3).
- Inner voice audio is never recorded and never leaves the WebRTC path.
- The Ratatouille constraint (advisory-to-the-hands-in-motion, spec-level) is
  enforced on the inner plane's diction: one breath, coach, don't narrate.
