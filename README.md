# 🏛️ Liberty Mutual — Claims Processing Demo

> **Teaching repo** for the 2026 Spark Summit _Code Quality_ lecture.
> Covers formatting, linting, testing, pre-commit hooks, CI, and command runners.

---

## 📁 Repo Layout

```
liberty-spark-summit-code-quality-demo/
├── claims_sample/
│   ├── bad/                  # ❌ Demo: code BEFORE quality tools
│   │   ├── claims_processor_bad.py
│   │   └── policy_lookup_bad.py
│   └── good/                 # ✅ Demo: code AFTER quality tools
│       ├── models.py
│       ├── claims_processor.py
│       └── policy_lookup.py
├── tests/
│   ├── test_claims_processor.py
│   └── test_policy_lookup.py
├── .github/workflows/ci.yml  # Continuous integration
├── .pre-commit-config.yaml   # Pre-commit hooks
├── pyproject.toml            # Ruff config + Hatch scripts (command runner)
└── justfile                  # Alternative: `just` command runner
```

---

## 🎓 Demo Walkthrough (Instructor Notes)

### 1 · Formatting (`just format`)

Open `bad/claims_processor_bad.py` side-by-side with `good/claims_processor.py`.
Point out: inconsistent quotes, missing spaces around operators, unsorted imports,
lines > 88 chars. Run `ruff format` and watch it fix everything automatically.

### 2 · Linting (`just lint`)

Run `ruff check claims_sample/bad/` — notice the flagged rules:

- `SIM102` — collapsible nested `if`
- `E501` — line too long
- `F841` — local variable assigned but never used
- `PLR2004` — magic number comparison

### 3 · Testing (`just test`)

Show `tests/test_claims_processor.py`:

- Unit tests for individual functions
- Integration test for the full pipeline
- A regression test (comment in the bug, watch the test fail)
  Run `just coverage` and open `htmlcov/index.html` to see line-by-line coverage.

### 4 · Pre-commit hooks

```bash
git add claims_sample/bad/claims_processor_bad.py
git commit -m "adding bad file"   # hooks fire, Ruff blocks the commit
```

### 5 · CI (`.github/workflows/ci.yml`)

Show the YAML — format check, lint, type-check, tests run on every push.
Break something on purpose and push; watch the badge go red.

### 6 · Command runner (`just --list`)

Show `justfile` — one word to run any tool instead of memorising long CLI flags.
