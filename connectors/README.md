# Connector Registry — spec §3.3, §5, §10

Every external surface is an isolated adapter with its own quota, backoff,
and taste-gated output. External agents are **capability-scoped tools, never
peers**: they receive tasks, return results, and never write to MeshOS
directly.

## Planned registry

| Connector | Plane | Owner | Milestone |
|---|---|---|---|
| Twitch (EventSub + IRC) | chat in | Knower | R2 |
| YouTube Live | chat in | Knower | R2 |
| Discord gateway | chat in | Knower | R2 |
| Meta Muse | model agent client | Foreman | R2 |
| Google Spark | model agent client | Foreman | R2 |
| Grokbot | model agent client | Foreman | R2 |
| Antigravity / Code / Cursor / Claude Code | desktop CLI hands (SDK/CLI) | Foreman | R3 |
| Buffer | distribution out | Foreman | R4 |
| OBS (obs-websocket) | broadcast mix + captions | Voice | R1 |
| VoxCPM / VibeVoice-class (via OmniRoute) | TTS | Voice | R1 |

## Adapter contract (v0.1)

```python
class Connector:
    name: str
    plane: str            # "in" | "out"
    owner: str            # "knower" | "voice" | "foreman"
    def start(self, clock, emit) -> None: ...
    def health(self) -> dict: ...   # quota, backoff state, last event
```

Every emitted event is stamped in the `t_stream` domain by the caller; a
connector never invents its own timestamps.
