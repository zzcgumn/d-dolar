Repository-level instructions for GitHub Copilot and agents

Purpose
- These files provide repository-scoped guidance that Copilot, Copilot Chat, and other repository-aware agents can surface before answering or making changes.

Provenance
- Adapted from the equivalent files in `rbe` and `dds`, which are this
  project's sibling bridge repositories, so that the trees read the same way.
  `cpp.instructions.md`/`bazel.instructions.md` there become
  `python.instructions.md` here; `git.instructions.md` and
  `github.instructions.md` are carried over largely unchanged since they are
  not language-specific.

Files
- `python.instructions.md` — Python style, structure and testing guidance
- `git.instructions.md` — Git/MCP usage
- `github.instructions.md` — Branching and PR rules

Usage
- Agents should read these files to apply repository-specific context. Humans can use this README as a quick pointer.

Contact
- If you need changes to these instructions, edit the corresponding file and open a PR.
