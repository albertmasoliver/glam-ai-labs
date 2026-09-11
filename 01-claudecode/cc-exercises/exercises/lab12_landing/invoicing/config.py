"""Configuration.

Precedence, learned the hard way: an explicit argument beats INVOICING_ENV,
which beats the file, which beats the defaults. The file is read once at
import time -- reassigning the env var later does nothing, which is the
single most common source of "it works on my machine" in this service.
"""

import json
import os

DEFAULTS = {
    "issuer_code": "ACME",
    "issuer_name": "Acme Iberia SL",
    "issuer_vat": "ESB00000000",
    "finance_api": "http://finance.internal/v2",
    "dry_run": True,
}

_CONFIG_PATH = os.environ.get("INVOICING_CONFIG", "/etc/invoicing/config.json")


def _load_file():
    try:
        with open(_CONFIG_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


_FILE = _load_file()
_ENV = {"dry_run": os.environ.get("INVOICING_ENV") != "production"}

SETTINGS = {**DEFAULTS, **_FILE, **{k: v for k, v in _ENV.items() if v is not None}}


def get(key, override=None):
    if override is not None:
        return override
    return SETTINGS[key]
