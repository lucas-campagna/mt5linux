# Issue #58 — `Metatrader5` (no description provided)

Upstream: https://github.com/lucas-campagna/mt5linux/issues/58
Status: open, but currently untriagable as written. This document records what is
known, what is missing, and how to turn it into an actionable issue.

## 1. Issue description

The GitHub issue contains only:

- Title: `Metatrader5`
- Reporter: `fetihdizbay2-web`
- Created: `2026-09-30`
- Body: `No description provided.`
- Assignees: none.
- Labels: none.
- Milestone: none.

There is no environment, traceback, reproduction, expected behavior, or log in
the issue itself.

Because of that, this repository document cannot state a technical root cause.
The correct next step is triage, not implementation.

## 2. What to ask the reporter

Request all of the following in one triage comment:

1. `mt5linux` version:
   - output of `pip show mt5linux`
   - whether the Docker image or Wine workflow is used
2. Environment:
   - host OS and version
   - Python version
   - Docker/uDocker/Wine availability and versions
   - broker/server name if relevant
3. Minimal reproduction:
   - complete short script, including imports
   - exact command used to run it
4. Actual behavior:
   - full traceback or error text
   - `mt5.last_error()` where applicable
5. Expected behavior:
   - what the reporter thought should happen
6. Logs:
   - client output
   - container logs if Docker is used (`docker logs <container>`)
   - terminal/journal excerpt if available
7. Whether any existing issue already covers it:
   - #50 for Wine/container-runtime selection
   - #51 for `order_send()` retcode `10027`
   - #55 for `initialize()` IPC timeout / restart problems
   - #57 for RPyC `PicklingError` on MT5 result objects

If the reporter confirms one of those, close #58 as a duplicate and link the
canonical issue.

## 3. How to triage it in this repository

1. Check whether the report matches a known failure signature:
   - `RuntimeError: No container runtime available` → #50.
   - `retcode 10027` → #51.
   - `(-10005, 'IPC timeout')` or RPyC `result expired` → #55 / #22.
   - `PicklingError: ... TerminalInfo/AccountInfo/SymbolInfo ...` → #57.
2. If it matches, ask for the missing confirmation details and close as duplicate
   once confirmed.
3. If it does not match, ask for the minimal reproduction above and keep the
   issue open in a “needs info” state.
4. Do not implement a fix from the title alone.

## 4. How to validate resolution

Resolution depends on triage outcome:

- Duplicate: closed with a link to #50, #51, #55, or #57, plus a short note
  explaining why.
- New actionable bug: rewritten issue body with reproduction, expected/actual
  behavior, environment, and logs; then a tracking e2e test in `tests/e2e/`
  following the existing pattern:

```bash
.venv/bin/python -m pytest tests/e2e -v
```

- Invalid / no response: closed under the project’s normal stale/insufficient-info
  policy, with a pointer to the issue template if one is added.

## 5. Suggested repository improvement

This empty issue is a good argument for adding a GitHub issue template requiring:

- version/environment
- reproduction script
- expected vs actual behavior
- full traceback/logs
- Docker vs Wine workflow

That would prevent future title-only reports.

## 6. Related files and tests

- No code change is associated with #58 at this time.
- Candidate mapping once details arrive:
  - engine/runtime: `mt5linux/_runtime.py`, `tests/e2e/test_standalone_engine.py`
  - trading: `docker/src/config.sh`, `tests/e2e/test_trading.py`
  - initialize/restart: `tests/e2e/test_initialization.py`,
    `tests/e2e/test_z_container_restart.py`
  - serialization: `mt5linux/types.py`, `tests/e2e/test_serialization.py`
- Related: #50, #51, #55, #57
