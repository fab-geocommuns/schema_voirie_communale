"""Vérifie que les numéros de version cités dans le schéma sont identiques à son champ « version »."""
import json
import re
import sys

PATTERN = r"v?\d+\.\d+\.\d+"
IGNORED_KEYS = {"fields"}


def check(obj, version, parents=""):
    errors = []
    if isinstance(obj, str):
        found = re.search(PATTERN, obj)
        if found and found[0] != version:
            errors.append((parents, found[0]))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            errors += check(item, version, f"{parents}[{index}]")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if key not in IGNORED_KEYS:
                errors += check(value, version, f"{parents}.{key}" if parents else key)
    return errors


failed = False
for schema_path in ("schema.json",):
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    version = schema["version"]
    for location, found in check(schema, version):
        print(f"{schema_path} : {location} cite la version {found}, attendue {version}")
        failed = True

sys.exit(1 if failed else 0)
