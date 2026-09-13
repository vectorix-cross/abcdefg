# CI

Local check:

```bash
pip install -e ".[dev]"
pytest -q
```

A GitHub Actions workflow was omitted because the current `gh` token does not have the `workflow` scope. To add `.github/workflows/ci.yml` later:

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: pytest -q
```

Then run `gh auth refresh -h github.com -s repo,workflow` and commit the file.
