"""Gate: a Claude Code Stop hook that runs the registered checks when the agent tries to finish.

Sends the agent back (exit 2) until the checks pass, at most `max_bounces` times (3 by default),
then lets it submit with warnings. Every decision goes to the bounce log. See `hook.py`.
"""

from trustlayer.gate.config import GateConfig, load_config
from trustlayer.gate.hook import Outcome, main, run

__all__ = ["GateConfig", "Outcome", "load_config", "main", "run"]
