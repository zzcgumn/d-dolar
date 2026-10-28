# d-dolar

D-dolar and two related double-dummy-based defence statistics for bridge.

The statistics are not yet implemented; this repository is currently
scaffolding. [`specs/`](specs/) will hold the precise definition of each
statistic once written, and [`docs/`](docs/) the guide for using the package.

## Layout

| Path | What is there |
| --- | --- |
| `src/d_dolar/` | the package |
| `tests/` | its test suite (pytest) |
| `examples/` | runnable examples of the public surface |
| `docs/` | the caller's guide and module map |
| `specs/` | the design record — what each statistic must compute, and why |
| `claude/` | a tripwire, not a home: working notes live in the private sibling `../d-dolar-notes`. Nothing here is ever committed — see [`CLAUDE.md`](CLAUDE.md) |

## Installing

```
pip install -e ".[dev]"
```

## Testing

```
pytest
```
