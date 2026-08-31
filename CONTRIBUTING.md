# Contributing

Thanks for contributing to `ai-quota`.

## Development

```bash
cd ~/ai-quota
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pip install pytest
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q ai_quota
```

## Adding a Provider

1. Add one module under `ai_quota/providers/`.
2. Implement a provider class with `key`, `label`, and `fetch(timeout=8.0)`.
3. Keep parsing separate and test it with redacted fixtures.
4. Register it in `providers/__init__.py` and `cli.py`.
5. Document credential source, endpoint stability, and limitations.
6. Never add real credentials or private account responses.

## Provider policy

Prefer official public APIs. If a provider requires a private client endpoint,
label it experimental and fail closed when the response shape is unknown. Do
not implement automatic login, CAPTCHA bypass, browser-cookie harvesting, or
credential upload.

## Pull requests

Keep changes focused. Include tests for success, missing credentials, malformed
responses, authentication failures, and timeout/error isolation. The full test
suite must pass before requesting review.
