# Fudge Room — AI Cohost for Live Game Streaming & Content Creation

**"The Fudge Room"** — three agents in unison: a live AI cohost that sees what
you see (Meta glasses), whispers in your ear (<800 ms), talks to your audience
with a real persona, and runs the production floor while you play.

> It's Ratatouille, not JARVIS. Remy under the hat, not a butler in the ceiling.
> The cohost never takes the controller.

## The brigade

| Agent | Role | Status |
|---|---|---|
| **The Knower** (`agents/knower/`) | Perception: glasses feed, game capture, chat rollup, moment marking | R0 skeleton |
| **The Voice** (`agents/voice/`) | Persona with two planes: inner voice (streamer's ear) + broadcast voice (OBS mix) | R0 skeleton |
| **The Foreman** (`agents/foreman/`) | Operations: Muse/Spark/Grok clients, desktop CLI agents, clips, Buffer | R2/R3 |

## Architecture in one diagram

```
glasses ──RTSP──▶ MediaMTX ──▶ Knower ──events──▶ Voice
                   │                            │
                   └──◀── inner TTS ────────────┘ (WebRTC → earpiece, <800ms)
OBS ◀── broadcast TTS + captions ── Voice        (R1)
MeshOS graph ◀── shared state, t_stream clock   (all three agents)
```

Full spec: [`docs/ai-cohost-spec.md`](docs/ai-cohost-spec.md) (v0.1.0).
ADRs: [`docs/adr/`](docs/adr/).

## Repo layout

```
fudgeroom/
├── agents/
│   ├── knower/        # perception (ingest, chat rollup)
│   ├── voice/         # inner + broadcast planes, TTS adapter
│   └── foreman/       # external agents, CLI hands, clips, distribution
├── common/            # t_stream clock, shared event bus (R2: MeshOS adapter)
├── connectors/        # pluggable connector registry (chat, social, model agents)
├── docs/              # spec + ADRs
├── infra/             # MediaMTX config, docker-compose, (R1: OBS)
├── tools/             # latency harness and dev utilities
└── tests/
```

## Quick start (R0 inner loop)

```bash
docker compose -f infra/docker-compose.yml up -d
pip install -e .

# push any camera as the glasses feed (macOS example):
ffmpeg -f avfoundation -i "0:0" -c:v libx264 -preset ultrafast -tune zerolatency \
  -c:a aac -f rtsp rtsp://localhost:8554/glasses

python -m agents.knower.ingest | python -m agents.voice.inner
# listen: open http://localhost:8889/inner in a WebRTC-capable browser
```

## Status

R0 (inner loop) scaffolded. See the honest real-vs-stub table in
[`docs/r0-notes.md`](docs/r0-notes.md). Build order: R0 inner loop → R1
broadcast voice → R2 Foreman + chat → R3 desktop CLI hands → R4 distribution.

## License

MIT (open source, like the rest of the Factory).
