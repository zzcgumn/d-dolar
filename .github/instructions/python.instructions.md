---
name: Python Development Rules
languages: ["python", "py"]
alwaysApply: false
applyTo: "**/*.py"
---

# Python Style and Development Rules

## Project Structure

- **`src/d_dolar/`**: the package.
- **`tests/`**: its test suite (pytest).
- **`examples/`**: runnable examples of the public surface.

## Style

### Naming
- **snake_case** for functions, methods, and variables.
- **PascalCase** for classes.
- **Leading underscore** for private/internal attributes and modules.
- **SCREAMING_SNAKE_CASE** for module-level constants.

### Type Hints
- Required on function parameters and return types.
- Use modern type hints: `X | None` for nullable types, built-in generics
  (`list[X]`, `dict[K, V]`, `tuple[X, ...]`) rather than `typing.Optional`,
  `typing.List`, etc.
- Use `TYPE_CHECKING` blocks for imports needed only by type checkers.

### Docstrings
- Module-level docstrings describing purpose.
- Public function/class docstrings for anything a caller imports, with
  `Args:`/`Returns:` sections where the signature alone is not enough.
- No docstring restating what a well-named, type-hinted function already
  says.

### Imports
- Group: standard library, third-party, local.
- Absolute imports within the package (`d_dolar.module`).

## Testing

- **Framework**: pytest (config in `pyproject.toml`).
- **Run tests**: `pytest`
- **Test organization**: one test module per source module
  (`tests/test_<module>.py`), function-based tests named for the behaviour
  they prove.
- **Fixtures**: defined in `conftest.py` when shared across modules.

A passing test proves little on its own: when adding or changing a guard,
break the thing it guards and confirm it goes red, then restore it.
