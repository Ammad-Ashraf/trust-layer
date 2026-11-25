#!/usr/bin/env bash
# M4 step 7: test the built simple_ledger agent folder inside the Collider-Bench image, at no
# API cost. Run on the runner from the repo root:
#
#   python3 scripts/build_agent_folder.py
#   bash scripts/gate_container_test.sh                 # container test (free)
#   bash scripts/gate_container_test.sh --claude-hook   # + check Claude Code fires the project
#                                                         Stop hook (host claude, Haiku, ~$0.02)
#
# It checks, with the image's own Python 3.11 (no pint, pyyaml only):
#   1. the gate sends an empty workspace back (exit 2) with an actionable message;
#   2. bin/record-quantity fills the ledger, the task id is detected from the run folder name;
#   3. with matching results the gate lets the agent stop (exit 0);
#   4. with one bin 10x off it sends the agent back again (exit 2);
#   5. every decision lands in the bounce log under $HOME/.trustlayer/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT="$ROOT/build/agent/simple_ledger"
IMAGE="${IMAGE:-ghcr.io/dfaroughy/lhc-bench@sha256:8820ecd3b8cada3d37e5e16214bedc53b07cbc58ea83ef104f1795e3f9b3c01f}"
TEMPLATE="$ROOT/external/collider-bench/ColliderBench/tasks/sus-16-034_sim-TChiWZ/template"
[ -d "$AGENT" ] || { echo "build the agent folder first: python3 scripts/build_agent_folder.py" >&2; exit 1; }

TMP="$(mktemp -d /tmp/tl-gate-test.XXXXXX)"
WS="$TMP/runs/claude_test/sus-16-034_sim-TChiWZ_ContainerTest_1/workspace"
mkdir -p "$WS/results" "$WS/bin" "$TMP/home"
cp "$TEMPLATE"/*.yaml "$WS/results/"
ln -s "$AGENT/runtime/bin/record-quantity" "$WS/bin/record-quantity"
echo "test workspace: $WS"

cat > "$TMP/inside.sh" <<'INSIDE'
set -uo pipefail
GATE="$AGENT/runtime/hooks/trustlayer-gate"
hook() { echo "{\"session_id\":\"container-test\",\"cwd\":\"$WS\",\"hook_event_name\":\"Stop\"}" | "$GATE"; }
fail() { echo "FAIL: $*"; exit 1; }
fill() {  # fill() a b c d -> writes the four bin values into the results template
  /opt/conda/envs/lhc_analysis/bin/python - "$@" <<'PY'
import glob, re, sys
path = glob.glob("results/*.yaml")[0]
text = re.sub(r"value: \S+", "value: null", open(path).read())
vals = iter(sys.argv[1:])
open(path, "w").write(re.sub(r"value: null", lambda m: "value: " + next(vals), text))
PY
}
cd "$WS"
/opt/conda/envs/lhc_analysis/bin/python --version
hook 2>"$TMP/msg1"; code=$?; [ $code -eq 2 ] || fail "empty workspace: expected exit 2, got $code"
grep -q "cross_section is missing" "$TMP/msg1" || fail "empty workspace: message lacks C3 hint"
echo "ok 1: empty workspace sent back (exit 2)"

bin/record-quantity cross_section --value 30.1656 --unit fb --source-type xsec_wg \
  --process chargino_neutralino --mass chargino_1=550 --mass neutralino_2=550 --source "xsec WG" >/dev/null
bin/record-quantity luminosity --value 35.9 --unit fb^-1 --source paper >/dev/null
bin/record-quantity branching_fraction --value 0.101 --source PDG >/dev/null
bin/record-quantity efficiency --value 0.0495 --source "cut flow" >/dev/null
grep -q "task: sus-16-034_sim-TChiWZ" ledger.yaml || fail "task id not detected from run folder"
bin/record-quantity show | grep -q "= 5.41" || fail "show does not give 5.41 events"
echo "ok 2: ledger recorded, task detected, product 5.41"

fill 0.45 1.37 1.65 1.94
hook 2>"$TMP/msg2"; code=$?; [ $code -eq 0 ] || { cat "$TMP/msg2"; fail "matching results: expected exit 0, got $code"; }
echo "ok 3: matching results pass (exit 0)"

fill 0.45 1.37 1.65 19.4
hook 2>"$TMP/msg3"; code=$?; [ $code -eq 2 ] || fail "10x bin: expected exit 2, got $code"
grep -q "larger than the ledger" "$TMP/msg3" || fail "10x bin: message lacks the C5 ratio"
echo "ok 4: one bin 10x off sent back (exit 2)"

events=$(/opt/conda/envs/lhc_analysis/bin/python -c "import json;print(' '.join(json.loads(l)['event'] for l in open('$HOME/.trustlayer/bounces.jsonl')))")
[ "$events" = "bounce pass bounce" ] || fail "bounce log events: '$events'"
echo "ok 5: bounce log = $events"
echo "CONTAINER TEST PASSED"
INSIDE

podman run --rm --pull=never --network=none \
  -v "$TMP:$TMP" -v "$AGENT:$AGENT:ro" \
  -e HOME="$TMP/home" -e AGENT="$AGENT" -e WS="$WS" -e TMP="$TMP" \
  -w "$WS" "$IMAGE" bash "$TMP/inside.sh"

if [ "${1:-}" = "--claude-hook" ]; then
  # Does Claude Code load a Stop hook from the workspace's .claude/settings.json in -p mode
  # with --dangerously-skip-permissions (how the harness runs it)? Empty ledger -> the gate
  # must fire. Uses the host's claude and python3, Haiku, a few cents.
  CWS="$TMP/runs/claude_test/sus-16-034_sim-TChiWZ_HookTest_1/workspace"
  mkdir -p "$CWS/results" "$CWS/.claude" "$TMP/home2"
  cp "$TEMPLATE"/*.yaml "$CWS/results/"
  printf '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"%s","timeout":120}]}]}}\n' \
    "$AGENT/runtime/hooks/trustlayer-gate" > "$CWS/.claude/settings.json"
  (cd "$CWS" && TRUSTLAYER_PYTHON="$(command -v python3)" TRUSTLAYER_BOUNCE_LOG="$TMP/home2/bounces.jsonl" \
    claude -p "Reply with the single word done." --model claude-haiku-4-5 \
    --dangerously-skip-permissions --max-turns 6 >"$TMP/claude.out" 2>&1 || true)
  if [ -s "$TMP/home2/bounces.jsonl" ]; then
    echo "ok 6: Claude Code fired the project Stop hook ($(wc -l <"$TMP/home2/bounces.jsonl") gate calls)"
  else
    echo "FAIL 6: no gate call logged; see $TMP/claude.out"; exit 1
  fi
fi
echo "all done; scratch in $TMP"
