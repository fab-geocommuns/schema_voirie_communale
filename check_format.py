"""Vérifie le format d'un fichier CSV des voies locales : UTF-8, point-virgule, sans encadrement des chaînes.

Une valeur ne doit contenir ni point-virgule, ni saut de ligne, et ne doit pas commencer par un guillemet double.
Le nombre de colonnes et les en-têtes sont comparés à ceux de schema.json.

Usage : python check_format.py fichier.csv [autre.csv ...]
"""
import json
import os
import sys

SEPARATOR = ";"
SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.json")


def check(path, expected):
    errors = []
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        return [f"l'encodage n'est pas UTF-8 ({e.reason} à l'octet {e.start})"]

    if not text.strip():
        return ["le fichier est vide"]

    lines = text.splitlines()
    if lines[0].split(SEPARATOR) != expected:
        errors.append(f"ligne 1 : les en-têtes ne sont pas ceux du schéma, dans le même ordre (attendu : {SEPARATOR.join(expected)})")

    for number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"ligne {number} : ligne vide")
            continue
        cells = line.split(SEPARATOR)
        if len(cells) != len(expected):
            errors.append(
                f"ligne {number} : {len(cells)} colonnes au lieu de {len(expected)} "
                f"(une valeur contient un point-virgule, ou un saut de ligne a coupé la ligne précédente ou suivante)"
            )
            continue
        for name, cell in zip(expected, cells):
            if cell.startswith('"'):
                errors.append(f"ligne {number}, colonne « {name} » : la valeur commence par un guillemet double, alors qu'aucun encadrement n'est utilisé")
    return errors


def main(paths):
    if not paths:
        print(__doc__)
        return 2
    with open(SCHEMA, encoding="utf-8") as f:
        expected = [field["name"] for field in json.load(f)["fields"]]

    failed = False
    for path in paths:
        errors = check(path, expected)
        if errors:
            failed = True
            print(f"{path} : NON CONFORME")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"{path} : conforme (UTF-8, séparateur « {SEPARATOR} », sans encadrement, {len(expected)} colonnes)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
