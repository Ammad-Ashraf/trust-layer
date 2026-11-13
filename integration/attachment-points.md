# Attachment points

Fill these in during the smoke run (`experiments/00-smoke-run/`). Checker development starts from this map.

## 1. Where the ledger lives

- Agent workspace directory inside the container (where the paper, task card and null-filled YAML template sit): _TBD_
- How `record-quantity` gets onto the agent's PATH: _TBD_
- Where the ledger file lands so the gate can read it at run end: _TBD_

## 2. Where the gate fires

- Where the harness puts Claude Code's hook configuration in the sandbox: _TBD_
- Does a Stop hook actually fire there? _TBD_
- Does the hook's rejection message reach the agent as feedback it can act on? _TBD_

## 3. Where run artifacts land

- `session.jsonl` (transcript): _TBD_ (size per run: _TBD_)
- Submitted results YAML: _TBD_
- Evaluator output: _TBD_

## 4. What `bin/run-analysis` activates

- Conda environment name and path: _TBD_
- How our checks run inside or alongside it: _TBD_
