"""
entr0py.core.config
~~~~~~~~~~~~~~~~~~~
Loads default.toml from the package config/ dir, then merges any user
overrides from ~/.entr0py/config.toml.  Returns a plain dict.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

from entr0py.core.paths import CONFIG_FILE

_DEFAULT_CFG = Path(__file__).parent.parent.parent / "config" / "default.toml"
_USER_CFG    = CONFIG_FILE


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load() -> dict:
    with _DEFAULT_CFG.open("rb") as f:
        cfg = tomllib.load(f)

    if _USER_CFG.exists():
        with _USER_CFG.open("rb") as f:
            user = tomllib.load(f)
        cfg = _deep_merge(cfg, user)

    return cfg


# Module-level singleton so the config is only read once per process.
_cfg: dict | None = None


def get() -> dict:
    global _cfg
    if _cfg is None:
        _cfg = load()
    return _cfg
