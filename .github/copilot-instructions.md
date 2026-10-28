# d-dolar Repository Instructions

## Project Overview

**d-dolar** computes D-dolar and two other double-dummy-based defence
statistics for bridge. The statistics themselves are not yet defined in
code — this repository is currently scaffolding, built to the same shape as
the sibling bridge repositories `rbe` and `dds`.

- The design record for each statistic, once written, is `specs/`
- The caller's guide and module map, once there is a public surface, is `docs/`

**Read the spec before changing behaviour**, once one exists. It is not a
summary written after the fact; it is what the tests encode, and a change
that contradicts it is a change to the spec first.

**Languages & tools**: Python 3.11+, pytest.

## Building and Testing

```bash
pip install -e ".[dev]"
pytest
```

Run the suite before and after making changes, so a pre-existing failure is
not attributed to your change.

## Project Layout and Architecture

```
<repository-root>/
├── .github/
│   ├── copilot-instructions.md      # This file
│   ├── instructions/                 # Path-specific instructions
│   └── workflows/                    # CI
├── src/d_dolar/                      # The package
├── tests/                            # pytest suite
├── examples/                         # runnable examples of the public surface
├── docs/  specs/
├── pyproject.toml
└── claude/                           # tripwire only — see CLAUDE.md
```

## Coding Standards and Conventions

**Follow `.github/instructions/python.instructions.md`.** Key points:

- **Types**: `PascalCase`. **Functions/variables**: `snake_case`.
- Type hints required on public functions. Modern syntax (`X | None`,
  built-in generics).

### Testing

pytest. This repository is meant to be built test-first (see `AGENTS.md`).

**A passing test proves little on its own.** When you add or change a guard,
break the thing it guards and confirm it goes red, then restore it.

## Important Facts for Agents

### Trust these instructions
Only search the codebase if the information here is incomplete for your task,
you find a discrepancy with reality, or you need implementation detail.
**If you find a discrepancy, fix this file as part of your change.**

### Don't
- Don't add a dependency without strong justification
- Don't commit anything private to this tree — it is meant to become public;
  working notes belong in `../d-dolar-notes`

### Always
- Always run the test suite before committing
- Always open a PR; never commit to `main` directly
- Always check `.github/instructions/*.instructions.md` for file-specific rules
