# Test-subject Claude settings

The test-subject agent's only extra Claude Code setting is the Stop-hook gate:

```json
{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "<fork>/agents/simple_ledger/runtime/hooks/trustlayer-gate", "timeout": 120}]}]}}
```

It is **not** kept here as a file for the host's `~/.claude`. The harness copies the host's user settings into every run, baseline included, so `agents/simple_ledger/run.py` writes the setting above as `workspace/.claude/settings.json` in checker-arm workspaces only (see `../container/README.md`). `scripts/postrun_check.py` checks after each run that the file is still exactly this, so the agent can't remove the gate unnoticed.

This is **not** the builder's `.claude/` folder. Nothing from the builder's context belongs here. Host-side leaks (MCP servers, connectors, host settings) are closed by the fork's `auth: token` mode, which copies nothing from the host home (decision 0020).
