# Liberty Mutual — Claims Processing Demo

> **Teaching repo** for the 2026 Spark Summit _Pipelines with GitHub Actions_ workshop.
> Covers writing tests, running them in CI, and automating quality checks with GitHub Actions.

---

## Repo Layout

```
liberty-spark-summit-pipelines-workshop/
├── claims_sample/
│   ├── __init__.py
│   └── good/                 # Production-quality claims processing code
│       ├── __init__.py
│       ├── models.py
│       ├── claims_processor.py
│       └── policy_lookup.py
├── tests/
│   ├── __init__.py
│   ├── test_claims_processor.py
│   └── test_policy_lookup.py
├── conftest.py               # Shared pytest fixtures
├── pyproject.toml            # Project metadata + pytest config
└── README.md
```

---

## Workshop Walkthrough

### 0 · Setup local test environment

Run script in order to be able to run the test files locally.

```bash
pip install -e ".[dev]"
pytest
```

### 2 · Explore the test suite

Open `tests/test_claims_processor.py` and `tests/test_policy_lookup.py`:

- Unit tests for individual functions
- Integration test for the full pipeline
- Fixtures defined in `conftest.py`

### 3 · Add a GitHub Actions workflow

Create `.github/workflows/ci.yml` to run the test suite on every push and pull request:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest
```

### 4 · Extend the pipeline

Ideas to explore during the workshop:

- Add a lint step with `ruff check`
- Add a format check with `ruff format --check`
- Run tests against multiple Python versions using a matrix strategy
- Add a status badge to this README
