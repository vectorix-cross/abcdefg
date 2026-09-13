# CI

GitHub Actions runs `pytest` on every push and pull request to `main` (`.github/workflows/ci.yml`).

Local check:

```bash
pip install -e ".[dev]"
pytest -q
```
