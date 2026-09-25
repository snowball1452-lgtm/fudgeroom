# The Foreman — operations (spec §5)

R2/R3 component. Placeholder in R0.

## Scope

- **External model agents** (Muse, Spark, Grokbot): capability-scoped clients.
  The Foreman sends task requests, writes results to the graph. External
  agents never speak on stream and never write to MeshOS.
- **Desktop CLI hands** (Antigravity, Code, Cursor, Claude Code via SDK/CLI):
  all desktop actions flow through the hands layer. Every invocation is a
  Golden Ticket-signed grant: scope (cwd, repo, globs), expiry, revocation.
  Default: read/analyze freely; write only in `foreman/wip/<task-id>`;
  deploy nothing without a signed grant.
- **Post-production**: clip pipeline from `moment.confirmed` events, session
  digest.
- **Distribution**: Buffer queue; publishes as drafts, owner confirms (v0.1).

## Layout (when built)

```
agents/foreman/
├── hands.py          # CLI agent adapters behind Golden Ticket grants
├── externals.py      # Muse / Spark / Grokbot clients
├── clips.py          # moment.confirmed → rendered clip
└── distribution.py   # Buffer queue, digests
```
