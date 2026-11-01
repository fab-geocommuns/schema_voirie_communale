"""Vérifie que le diagramme de classes de MODELE.md concorde avec schema.json.

Sont comparés, pour chaque champ : le nom et l'ordre des attributs de la classe VoieLocale, leur type, leur
multiplicité et, pour les listes de valeurs, les valeurs de l'énumération et leur ordre.
"""
import json
import re
import sys

CLASSE = "VoieLocale"

# type Table Schema : type UML (ISO 19103 et ISO 19107), comme dans le tableau de MODELE.md
TYPES = {
    "string": "CharacterString",
    "number": "Real",
    "date": "Date",
    "geopoint": "GM_Point",
    "geojson": "GM_MultiCurve",
}


def lire_diagramme(chemin):
    """Retourne les attributs de la classe principale [(nom, type, multiplicité)] et les énumérations {nom: [valeurs]}."""
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    bloc = re.search(r"```mermaid\n(.*?)```", texte, re.S)
    if not bloc:
        sys.exit(f"{chemin} : aucun bloc mermaid")

    classes = {}
    for nom, corps in re.findall(r"class (\w+) \{\n(.*?)\n\s*\}", bloc[1], re.S):
        classes[nom] = [ligne.strip() for ligne in corps.splitlines() if ligne.strip()]

    lignes = classes.pop(CLASSE, [])
    if lignes[:1] != ["<<featureType>>"]:
        sys.exit(f"{chemin} : la classe {CLASSE} doit porter le stéréotype <<featureType>>")

    attributs = []
    for ligne in lignes[1:]:
        trouve = re.fullmatch(r"(\w+) : (\w+)(?: \[([\d.*]+)\])?", ligne)
        if not trouve:
            sys.exit(f"{chemin} : attribut illisible dans {CLASSE} : {ligne}")
        nom, type_uml, multiplicite = trouve.groups()
        # sans multiplicité, l'attribut vaut exactement 1 (convention UML suivie par le modèle de standard du CNIG)
        attributs.append((nom, type_uml, multiplicite or "1"))

    enumerations = {nom: lignes[1:] for nom, lignes in classes.items() if lignes[:1] == ["<<enumeration>>"]}
    return attributs, enumerations


def attendu(champ):
    """Retourne (type Table Schema, multiplicité, liste de valeurs ou None) d'un champ du schéma."""
    obligatoire = champ.get("constraints", {}).get("required", False)
    if champ["type"] == "array":
        return champ["type"], "1..*" if obligatoire else "0..*", champ["arrayItem"]["constraints"].get("enum")
    return champ["type"], "1" if obligatoire else "0..1", champ.get("constraints", {}).get("enum")


def main():
    with open("schema.json", encoding="utf-8") as f:
        champs = json.load(f)["fields"]
    attributs, enumerations = lire_diagramme("MODELE.md")

    erreurs = []
    noms_schema, noms_modele = [c["name"] for c in champs], [a[0] for a in attributs]
    if noms_schema != noms_modele:
        erreurs.append(f"attributs différents des champs du schéma (noms ou ordre) :\n    schéma : {noms_schema}\n    modèle : {noms_modele}")

    modele = {nom: (type_uml, multiplicite) for nom, type_uml, multiplicite in attributs}
    utilisees = set()
    for champ in champs:
        if champ["name"] not in modele:
            continue
        type_schema, multiplicite, valeurs = attendu(champ)
        type_uml, multiplicite_uml = modele[champ["name"]]
        if multiplicite_uml != multiplicite:
            erreurs.append(f"{champ['name']} : multiplicité [{multiplicite_uml}], attendue [{multiplicite}]")
        if valeurs:
            utilisees.add(type_uml)
            if type_uml not in enumerations:
                erreurs.append(f"{champ['name']} : type {type_uml}, qui n'est pas une énumération du diagramme")
            elif enumerations[type_uml] != valeurs:
                erreurs.append(f"{champ['name']} : valeurs de {type_uml} différentes du schéma :\n    schéma : {valeurs}\n    modèle : {enumerations[type_uml]}")
        elif type_schema not in TYPES:
            erreurs.append(f"{champ['name']} : type {type_schema} du schéma sans type UML correspondant dans TYPES (assert_modele.py et tableau de MODELE.md)")
        elif type_uml != TYPES[type_schema]:
            erreurs.append(f"{champ['name']} : type {type_uml}, attendu {TYPES[type_schema]} (type {type_schema} du schéma)")

    for nom in sorted(set(enumerations) - utilisees):
        erreurs.append(f"énumération {nom} utilisée par aucun attribut")

    for e in erreurs:
        print(f"MODELE.md : {e}")
    if not erreurs:
        print(f"MODELE.md : {len(attributs)} attributs et {len(enumerations)} énumérations, conformes à schema.json")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
