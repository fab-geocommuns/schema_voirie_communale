"""Vérifie que exemple-invalide.csv produit exactement les erreurs listées dans erreurs-attendues.json.

Les erreurs de la validation du schéma (frictionless) et celles des contrôles complémentaires sont comparées séparément.
Le test échoue si une erreur attendue disparaît, si une erreur inattendue apparaît, ou si un outil plante.
"""
import json
import subprocess
import sys

FICHIER = "exemple-invalide.csv"


def erreurs_frictionless():
    p = subprocess.run(
        ["frictionless", "validate", "--schema", "schema.json", "--json", FICHIER],
        capture_output=True, text=True, encoding="utf-8",
    )
    rapport = json.loads(p.stdout)
    return {(e.get("rowNumber"), e.get("fieldName"), e["type"]) for t in rapport["tasks"] for e in t["errors"]}


def erreurs_controles():
    p = subprocess.run(
        [sys.executable, "controles_complementaires.py", FICHIER, "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    return {(e["row"], e["field"], e["code"]) for e in json.loads(p.stdout)}


def main():
    with open("erreurs-attendues.json", encoding="utf-8") as f:
        attendu = json.load(f)

    comparaisons = (
        ("validation du schéma (frictionless)", {(e["row"], e["field"], e["type"]) for e in attendu["frictionless"]}, erreurs_frictionless()),
        ("contrôles complémentaires", {(e["row"], e["field"], e["code"]) for e in attendu["controles"]}, erreurs_controles()),
    )

    echec = False
    for nom, prevues, reelles in comparaisons:
        manquantes, inattendues = sorted(prevues - reelles, key=str), sorted(reelles - prevues, key=str)
        if manquantes or inattendues:
            echec = True
            print(f"{nom} : écart avec erreurs-attendues.json")
            for e in manquantes:
                print(f"  attendue mais absente : {e}")
            for e in inattendues:
                print(f"  détectée mais inattendue : {e}")
        else:
            print(f"{nom} : {len(reelles)} erreurs, conformes à erreurs-attendues.json")
    return 1 if echec else 0


if __name__ == "__main__":
    sys.exit(main())
