# envcheck

Compare `.env` against `.env.example` and find missing or undocumented variables — great for CI and onboarding.

## Install

```bash
pip install envcheck
```

## Usage

```bash
# Auto-detect .env and .env.example in current directory
envcheck

# Scan a specific project directory
envcheck /path/to/project

# Ignore undocumented keys (don't flag .env-only vars)
envcheck --allow-extra

# Don't warn about empty values
envcheck --no-warn-empty

# CI-friendly: only print issues, exit 0/1
envcheck --quiet
```

## Example output

```
env:     .env
example: .env.example

✗ Missing (2) — required by .env.example but not in .env:
    DATABASE_URL
    REDIS_URL

⚠ Undocumented (1) — in .env but not in .env.example:
    MY_LOCAL_DEBUG_FLAG

⚠ Empty (1) — keys with no value set:
    SECRET_KEY
```

Exits with code `1` when missing or extra keys are found, `0` when all clear.

## Supported example file names

- `.env.example`
- `.env.sample`
- `.env.template`

## CI integration

```yaml
- name: Verify .env matches .env.example
  run: envcheck --quiet
```

## License

MIT
