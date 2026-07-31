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

### 0 · Initial Setup

Create a new repo and import the setup repo: https://github.com/khansen4/liberty-spark-summit-pipelines-workshop

Open the repo locally, and run script in terminal to import pytest to test files locally.

```bash
pip install -e ".[dev]"
pytest
```

### 1 · Explore the test suite

Open `tests/test_claims_processor.py` and `tests/test_policy_lookup.py`:

- Unit tests for individual functions
- Integration test for the full pipeline
- Fixtures defined in `conftest.py`

### 2 · Create a GitHub Actions workflow file

Navigate to GitHub Actions and search for "Simple Workflow" template. By selecting the template file, it will be added to your repo.

### 3 · Begin constructing the workflow file

In the workflow file, rename the file to something like "simple_file.yaml" and update the name in file. 

```
# This is a basic workflow to help you get started with Actions

name: simple_test
```

The template file providers a good starting spot with controls on main already added. This can be updated to include PR's but for the purpose of this demo we will leave it as is.

```
# Controls when the workflow will run
on:
  # Triggers the workflow on push or pull request events but only for the "main" branch
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:
```

### 4 · Begin adding actions

As discussed, for each action to be executed runners need to be installed. This are the virtual machines that will help to execute the code. In addition, the checkout step is added to allow to see the job. These are core components of an workflow file.

```
# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "build"
  build:
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v6
```

#### 4.1 · Python Libraries

Similar to running Python locally, python needs to be installed into the workflow for the runners to be able execute the code. To get the exact syntax to add it, we can search the market place for Python and it will provide us syntax for setting up Python into the workflow.

```
 - name: Setup Python
        uses: actions/setup-python@v7.0.0
        with:
          # Version range or exact version of Python or PyPy to use, using SemVer's version range syntax. Reads from .python-version if unset.
          python-version: "3.11"
```

#### 4.2 · PyTest

Now that Python is loaded, we can run commands on it to execute the code. Like in command line the execution we want is to run PyTest.

```
      # command to run is pytests in the repo
      - run: pytest
```

When checking the actions log we can see it failed, on the pytest indicating it can not be found. Like in command line, when first setting up the environment to run tests, pytest needs to be added into the environment. That is the same case here. So prior to running the pytest, it needs to be added into the action setup. 

```
# command to run is pytests in the repo
      - run: pip install -e ".[dev]"
      - run: pytest
```

### 5 · Final Step: Extend the pipeline

Now the workflow file has been created to run the pytests. As you can see some of the test are failing and the code needs to be updated. Once updating the actin will be successful. The pipeline can be further extended to include other things covered during the Code Quality workshop such as:

- Add a lint step with `ruff check`
- Add a format check with `ruff format --check`
- Run tests against multiple Python versions using a matrix strategy
- Add a status badge to this README

