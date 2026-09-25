# ADR-0004: Fog of War — Knowledge Sheets, the Director, and Silence by Default

**Status:** Accepted (v0.1.0, extends spec §3, §4, §8)

## Context

Radio cohosts can be fully pre-programmed: the timeline is known before air.
Games are a fog of war. Moments are emergent, state is partially observable,
and the latency budget (<800 ms, spec §7.2) forbids heavyweight live reasoning
over raw game state. A wrong advisory mid-firefight costs trust that a
silent moment never does.

## Decision

Split knowing from relevance. Never reason inside the fog.

1. **Play sheets carry the knowledge** (built and taste-verified off air).
   The Voice does not need to understand the game; it says checked facts in
   Frank's diction. Sheets are game-agnostic: same format for a Warzone map,
   a repair manual, a speedrun route.
2. **The Knower carries the watching**: a compact rolling state summary plus
   a confidence value per perception event. It does not interpret — it
   estimates.
3. **The Director carries the when** (`agents/voice/director.py`): tag-match
   perception events to sheet facts, enforce cooldown, enforce separation
   (no fact reused within the repeat window), gate on confidence. Selection,
   not generation.
4. **Silence is the default state.** Below the confidence floor, or when
   everything matching is on cooldown, the correct output is nothing.
5. **The session digest closes the loop**: post-session t_stream replay
   (spec §7.3) reconciles advice against outcomes; verified observations
   merge back into the sheet. The fog burns off session over session.

## Consequences

- The live loop is a lookup, so cheap models are safe for it (spec §8) and
  the latency budget is achievable.
- "Frank doesn't know things" becomes a feature: he only says what the
  sheet vouches for. Hallucination is structurally starved, not prompted away.
- Sheet authorship is an offline, taste-gated workflow — same machinery as
  the rest of the Factory.
- Open question: how confidence is calibrated for the Knower's placeholder
  perception pass; R1 work.
