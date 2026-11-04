# Contributing

Issues and pull requests are welcome.

- `pip install -e ".[dev]"`, then `ruff check . && ruff format --check . && mypy && pytest`
  must pass. Coverage below 100% fails the run, and so does any warning raised during tests.
- The package depends on numpy only. Matplotlib is used only by `scripts/make_figures.py`.
- A change to the formulas must keep the hand cases in `docs/derivation.md` passing.
- Any new beam section, steel value or price must be labelled illustrative unless it is
  quoted from a named source. This project is not a structural design standard.
