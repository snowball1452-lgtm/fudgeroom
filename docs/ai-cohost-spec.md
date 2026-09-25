# AI Cohost System Specification

## "The Fudge Room" — Three Agents, One Voice In Your Head

**Version:** 0.1.0 (draft)
**Status:** Unimplemented — architecture spec
**Upstream:** Complies with Composition Algebra v2.1.0 (`docs/agent-control/composition-algebra.md`)
**Owner:** Chad Snowball

---

## 1. Purpose & Scope

A live-on-stream AI cohost for video games and content creation, built as three
 cooperating agents working in unison:

- **The Knower** — perception. In the know: game state, chat, room, history.
- **The Voice** — persona. Two mouths: an inner voice only the streamer hears,
  and a broadcast voice the audience hears.
- **The Foreman** — operations. Everything that isn't talking: external model
  agents, desktop CLI agents, post-production, distribution.

Scope covers all video games and all content-creation surfaces around them:
live streaming, chat, clips, social distribution, and build-during-stream tooling.

Out of scope for v0.1: autonomous moderation actions against viewers (flag only),
and any desktop write outside the Golden Ticket kernel constraints.

---

## 2. Agent Topology

```
                 ┌──────────────────────────────────────────┐
                 │                MeshOS graph              │
                 │   (shared, versioned, event-driven)      │
                 └───────▲──────────▲──────────▲────────────┘
                         │          │          │
             writes      │   writes │   writes │
      ┌────────────┐    │   ┌──────┴─────┐    │
      │ THE KNOWER │────┘   │  THE VOICE │────┘
      │ (perception)│       │ (persona)   │
      └─────┬──────┘        └─────┬──────┘
            │ reads               │ speaks
            ▼                     ▼
      ┌─────────────┐      ┌──────────────┐
      │  streams    │      │ inner voice  │──▶ glasses (WebRTC)
      │  (perception)│      │ broadcast   │──▶ OBS program mix
      └─────────────┘      │ TTS + CC     │──▶ captions/transcript
                           └──────────────┘

      ┌──────────────┐
      │ THE FOREMAN  │◀── events from MeshOS ("clip that", schedules)
      │ (operations) │──▶ Muse / Spark / Grok (external agents)
      │              │──▶ Antigravity / Code / Cursor / Claude Code (CLI)
      │              │──▶ Buffer / socials / post-production
      └──────────────┘
```

**Unison contract:** the three agents are peers, not a hierarchy. They share no
direct message bus for state — all coordination flows through the MeshOS graph
(event-driven, per MeshOS semantics). Each agent owns its writes to a disjoint
set of node types (§8) so composition never conflicts. The Knower is not a
leader; it is simply the first in the causal chain of a live moment.

---

## 3. The Knower — Perception

*"The Scouting Room"*

### 3.1 Input feeds

| Feed | Source | Transport | Notes |
|---|---|---|---|
| First-person view | Meta glasses camera | RTSP → MediaMTX | primary peripheral |
| Room audio | Glasses mic | RTSP audio → MediaMTX | streamer's speech |
| Game video/audio | OBS capture | local pipe / MediaMTX | game feed |
| Live chat | Twitch/YouTube/Discord | platform APIs/websockets | see 3.3 |
| Broadcast voice transcript | The Voice's TTS pipeline | internal event | what was said publicly |
| Inner voice log | The Voice's inner channel | internal event | never broadcast |
| Stream program out | OBS RTMP | read-only tap | what the audience actually sees |

### 3.2 Perception pipeline

1. **Ingest** — normalize all feeds to timestamped event stream, single clock
   domain (§7.1).
2. **Compress** — vision frames and audio windows become semantic events
   (entities, actions, game-state deltas), never raw dumps. The Knower writes
   *facts*, not pixels.
3. **Chat shaping** — chat is a rate problem, not a comprehension problem.
   Continuous rollup: trending topics, sentiment, notable messages, questions
   queue, raid/chatter anomalies. The Voice never reads raw chat at scale;
   it reads the rollup.
4. **Moment marking** — the Knower flags candidate moments
   (`moment.candidate` nodes): game events, chat pile-ons, funny speech.
   Inner voice or streamer confirms → `moment.confirmed`, which The Foreman
   consumes post-stream.

### 3.3 Chat connectors

Pluggable connector registry (per Composition Algebra adapter layer). v0.1
targets: Twitch IRC/EventSub, YouTube Live, Discord gateway. Each connector is
an isolated adapter with its own quota, backoff, and taste-gated output.

---

## 4. The Voice — Persona & Speech

*"The Announcer"*

### 4.1 The two-voice split

The core architectural invariant: **the inner voice and the broadcast voice are
the same persona with two output planes, not two personas.**

| | Inner voice | Broadcast voice |
|---|---|---|
| Audience | Streamer only | Everyone |
| Path | MediaMTX WebRTC → glasses | TTS → OBS program mix |
| Latency target | < 500 ms end-to-end | seconds acceptable |
| Persona filter | taste gates only | full persona + taste gates |
| Recorded? | No | Yes — TTS is natively transcribed |
| Enters MeshOS? | Yes, as `voice.inner` events | Yes, as `voice.broadcast` events |

Both planes are generated in one inference pass with plane-labeled outputs —
the same context, the same read of the room, two diction levels. This prevents
the classic failure mode where the "private" agent tells you something the
public agent contradicts two seconds later.

### 4.2 TTS and persona pipeline

- **Persona definition** lives in the graph as a versioned persona object
  (PersonaPlex-style): diction, catchphrases, energy curve, topics to avoid.
- **TTS** via VoxCPM or VibeVoice-class engine, routed through OmniRoute for
  model selection. Broadcast voice is a stable voice identity; inner voice may
  be the same voice, lower-variance settings for speed.
- **Transcription loop:** broadcast TTS text is authoritative — it is written
  to MeshOS as the exact public utterance. This text feeds OBS captions and
   the Knower. No re-transcription drift.
- **The streamer's own speech** is transcribed (glasses mic) so both planes
  know what Chad just said. The cohost responds to the streamer, not just chat.

### 4.3 What the Voice says (and doesn't)

Per the Tasting Room: harm gates fire first, then ranking dimensions
(novelty, playfulness, expected_value) choose among candidate responses.
The Golden Ticket kernel is non-overridable on both planes: the inner voice
is *less* filtered, not *un*filtered.

---

## 5. The Foreman — Operations

*"The Production Floor"*

### 5.1 External model agents

The Foreman holds client adapters for Meta Muse, Google Spark, and Grokbot.
Each is a **capability-scoped tool**, not a peer: The Foreman sends a task
request, receives a result, writes the result to the graph. No external agent
ever writes to MeshOS directly, and none of them speak on stream.

### 5.2 Desktop CLI agents

Targets: Antigravity, Code, Cursor, Claude Code (SDK/CLI).

- All desktop actions go through **The Foreman's hands layer** (Browser Use /
  OpenHands / OpenClaw adapters), never raw shell from the Voice or Knower.
- Every CLI invocation is a Golden Ticket–signed grant with: scope (cwd, repo,
  file globs), expiry, and revocation. Default posture: read/analyze freely,
  write only inside a designated worktree (`foreman/wip/<task-id>`), deploy
  nothing without explicit signed grant.
- Build-during-stream is a first-class use: viewers watch The Foreman build
  game tools live via CLI agents while the Knower narrates.

### 5.3 Post-production & distribution

- **Clip pipeline:** consumes `moment.confirmed` events → cuts clips from the
  OBS RTMP tap / recordings → renders → queues.
- **Buffer connector:** scheduled multi-platform distribution. Buffer writes
  are queued as drafts by default; publish requires taste gate + (v0.1) owner
  confirmation.
- **Session digest:** end-of-stream rollup of the graph slice → stream recap
  asset.

---

## 6. Media Plane

*"The Chocolate River"* (transport layer)

```
Meta glasses ──RTSP──▶ MediaMTX ──┬──▶ Knower (ingest path)
                                 └──▶ WebRTC ◀── inner voice TTS (to streamer)

OBS ◀── game capture, mic, broadcast TTS, captions
OBS ──RTMP──▶ Twitch / YouTube (audience path, 2–6 s latency, fine)
MediaMTX ──HLS/RTSP──▶ recording tap (Foreman's clip source)
```

MediaMTX is the single local media router: every stream in the house is
addressable as a path (`/glasses`, `/game`, `/program`, `/inner`). Nothing
captures directly; everything subscribes. This keeps the latency budget
measurable and re-routable (§7).

---

## 7. Sync & Latency Budget (first-class)

### 7.1 Clock domain

All feeds are normalized to one monotonic stream clock (`t_stream`, anchored
at stream start). Wall-clock mapping is recorded but never used for
cross-feed reasoning. Every graph event carries `t_stream`; MeshOS event order
is causal order.

### 7.2 Budget

| Path | Target | Ceiling | Notes |
|---|---|---|---|
| glasses → MediaMTX ingest | 150 ms | 300 ms | RTSP on LAN |
| Knower perception cycle | 200 ms | 500 ms | semantic events, not full frames every tick |
| Voice inference + inner TTS | 300 ms | 500 ms | streaming TTS first-token |
| **Inner loop end-to-end (glasses→ear)** | **< 800 ms** | 1200 ms | the budget that matters |
| Broadcast TTS → OBS mix | 300 ms | 1 s | |
| OBS → platform (RTMP) | 3–6 s | — | audience path, acceptable |
| Chat message → in rollup | 1 s | 3 s | |
| Moment confirmed → graph | < 100 ms | | |

**Rule:** the inner loop budget is the design constraint. Any component that
cannot meet its row gets bypassed for the inner path (e.g., if OmniRoute
routing is slow, inner voice pins to one model; broadcast can keep routing).

### 7.3 Whole-stack sync

Because the broadcast voice's TTS text is written to the graph as authored
(§4.2), and the streamer's speech is transcribed into the same clock domain,
the graph can always answer: *what did everyone say/hear/see at `t_stream=X`* —
streamer, cohost (both planes), chat, and game — without re-transcribing VODs.
This is the "whole stack in sync" guarantee.

---

## 8. MeshOS Node Ownership

| Node type prefix | Owner (writer) | Readers |
|---|---|---|
| `perception.*` | Knower | all |
| `chat.rollup`, `moment.*` | Knower | all |
| `voice.inner`, `voice.broadcast` | Voice | Knower, Foreman |
| `persona.*` | Voice | all |
| `foreman.task.*`, `foreman.result.*` | Foreman | all |
| `clip.*`, `dist.*` | Foreman | all |
| `grant.*` | Golden Ticket kernel | all |

Disjoint write ownership ⇒ no composition conflicts across agents
(direct consequence of the Composition Algebra's cross-field constraints).

---

## 9. Governance

- **Golden Ticket:** applies to The Foreman's desktop writes and all external
  sends. The Voice's broadcast plane carries a harm gate; inner plane carries
  the same gate (§4.3).
- **Tasting Room ranking** drives The Voice's response selection and The
  Foreman's task prioritization.
- **Owner overrides:** "clip that" (voice or chat command), publish approval,
  and Golden Ticket grants are owner-set owned values per the Factory
  Inventory.

---

## 10. Interfaces (v0.1 connector registry)

1. MediaMTX (RTSP in/out, WebRTC, HLS)
2. OBS (via obs-websocket; source control, captions)
3. Twitch (EventSub + IRC), YouTube Live, Discord
4. Meta Muse, Google Spark, Grokbot (capability clients)
5. Antigravity / Code / Cursor / Claude Code (CLI/SDK hands)
6. Buffer (distribution queue)
7. VoxCPM / VibeVoice-class TTS (via OmniRoute)

---

## 11. Roadmap

- **R0 — The Knower + inner loop.** Glasses → MediaMTX → Knower → inner voice
  → WebRTC back. No OBS, no broadcast. If this feels like a voice in your
  head that knows the game, the hard part is done.
- **R1 — Broadcast voice.** Persona object, TTS to OBS, captions, transcription
  loop.
- **R2 — Foreman.** Chat connectors, external agents, clip pipeline.
- **R3 — Desktop hands.** CLI agents under Golden Ticket grants, live-build
  mode.
- **R4 — Distribution.** Buffer, digests, scheduled clips.

---

## 12. Open Questions

1. **Glasses ingress reliability** — Meta glasses RTSP/ADB path in sustained
   3+ hour sessions: heat, battery, stream drops. Need a MediaMTX
   reconnect/re-anchor policy in the clock domain.
2. **Persona memory across streams** — does the cohost remember previous
   streams' events? (MeshOS graph says yes by default; persona continuity
   policy needs deciding.)
3. **Inner voice delivery** — WebRTC to glasses earpiece vs. bone-conduction /
   paired earbud. Latency ceiling may decide the hardware.
4. **Multi-game portability** — per-game perception adapters (game-state
   extraction differs wildly between, say, a FPS and a strategy game). v0.1
   targets generic vision-only perception; game-specific adapters later.
