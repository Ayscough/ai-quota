# Security Policy

## Scope

`ai-quota` is a local-only CLI. It reads credentials supplied through environment
variables, a local TOML file, or provider CLI credential files. It does not
upload credentials to the project maintainer.

## Credential handling

- Never put API keys, cookies, OAuth access tokens, or refresh tokens in Git.
- Use environment variables or `~/.config/ai-quota/config.toml` with restrictive
  permissions (`chmod 600`).
- Do not paste real credentials into issues, pull requests, logs, or examples.
- OAuth and Cookie-based providers use private/experimental provider endpoints;
  revoke and re-authenticate if a credential may have been exposed.

## Reporting a vulnerability

Do not open a public issue containing a credential or an exploitable proof of
concept. Contact the maintainer privately through the repository's security
contact once the GitHub repository is created. Include the affected version,
impact, reproduction steps without secrets, and a suggested mitigation.
