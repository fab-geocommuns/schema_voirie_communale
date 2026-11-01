"""Produit ou vérifie le catalogue d'objets de MODELE.md à partir de schema.json, du diagramme et du modèle tableur.

Le catalogue est la partie de MODELE.md comprise entre les marqueurs DEBUT et FIN. Il reprend :

- pour chaque attribut de la classe VoieLocale : la description, l'exemple et les contraintes de schema.json, le type et
  la multiplicité du diagramme ;
- pour chaque énumération : les valeurs de schema.json et, mot pour mot, leurs définitions, regroupements et références
  juridiques du modèle tableur (un onglet par liste), lu par l'API de fichiers.numerique.gouv.fr.

Usage :
  python .github/workflows/catalogue.py            vérifie que le catalogue de MODELE.md est à jour (code de sortie 1 sinon)
  python .github/workflows/catalogue.py --ecrire   réécrit le catalogue de MODELE.md
Option : --tableur fichier.xlsx pour lire un fichier local au lieu de l'API.
"""
import argparse
import io
import json
import sys
import urllib.request

import openpyxl

from assert_modele import CLASSE, lire_diagramme

TABLEUR = "https://fichiers.numerique.gouv.fr/api/v1.0/items/cdf35f2b-302f-49d0-99e1-e4b38f483f68/download/"
MODELE = "MODELE.md"
DEBUT = "<!-- début du catalogue : généré par .github/workflows/catalogue.py, ne pas modifier à la main -->"
FIN = "<!-- fin du catalogue -->"

# colonnes des onglets de listes du tableur reprises dans le catalogue, dans cet ordre
COLONNES = ("Définition", "Regroupement", "Juridique")


def cellule(texte):
    """Texte d'une cellule de tableau Markdown : barres verticales échappées, sauts de ligne remplacés."""
    return str(texte).replace("|", "\\|").replace("\n", "<br>")


def tableau(entetes, lignes):
    resultat = ["| " + " | ".join(entetes) + " |", "| " + " | ".join("---" for _ in entetes) + " |"]
    resultat += ["| " + " | ".join(ligne) + " |" for ligne in lignes]
    return resultat


def lire_tableur(chemin):
    """Retourne {onglet: (colonnes présentes, {valeur: {colonne: texte}}, [valeurs dans l'ordre])}."""
    if chemin:
        contenu = open(chemin, "rb").read()
    else:
        with urllib.request.urlopen(TABLEUR, timeout=60) as reponse:
            contenu = reponse.read()
    classeur = openpyxl.load_workbook(io.BytesIO(contenu), data_only=True)
    onglets = {}
    for feuille in classeur.worksheets:
        lignes = [l for l in feuille.iter_rows(values_only=True) if any(c not in (None, "") for c in l)]
        if not lignes:
            continue
        entetes = [(str(c).strip().capitalize() if c else None) for c in lignes[0]]
        if entetes[:2] != ["Libellé", "Définition"]:
            continue
        colonnes = [c for c in COLONNES if c in entetes]
        valeurs, ordre = {}, []
        for ligne in lignes[1:]:
            valeur = str(ligne[0]).strip()
            ordre.append(valeur)
            valeurs[valeur] = {c: str(ligne[entetes.index(c)]).strip() if ligne[entetes.index(c)] else "" for c in colonnes}
        onglets[feuille.title] = (colonnes, valeurs, ordre)
    return onglets


def contraintes(champ, multiplicite, type_uml, est_enumeration):
    regles = ["valeur obligatoire" if multiplicite.startswith("1") else "valeur vide autorisée"]
    c = champ.get("constraints", {})
    if "pattern" in c:
        regles.append(f"motif : `{c['pattern']}`")
    if "minimum" in c:
        regles.append(f"minimum : {c['minimum']}")
    if est_enumeration:
        regles.append(f"liste de valeurs : [{type_uml}](#{type_uml.lower()})")
    return "<br>".join(cellule(r) for r in regles)


def construire(champs, attributs, enumerations, onglets):
    """Retourne (lignes du catalogue, erreurs de concordance entre schema.json et le tableur)."""
    erreurs = []
    modele = {nom: (type_uml, multiplicite) for nom, type_uml, multiplicite in attributs}

    lignes = [DEBUT, "", f"### Attributs de la classe {CLASSE}", ""]
    corps = []
    for champ in champs:
        type_uml, multiplicite = modele[champ["name"]]
        corps.append([
            f"`{champ['name']}`",
            cellule(champ.get("description", "")),
            multiplicite,
            f"`{type_uml}`",
            contraintes(champ, multiplicite, type_uml, type_uml in enumerations),
            f"`{cellule(champ['example'])}`" if "example" in champ else "",
        ])
    lignes += tableau(["Attribut", "Définition", "Occurrences", "Type", "Contraintes", "Exemples"], corps)

    lignes += ["", "### Types énumérés", "",
               "Les définitions, regroupements et références juridiques sont repris du [modèle tableur]"
               "(https://fichiers.numerique.gouv.fr/wopi/cdf35f2b-302f-49d0-99e1-e4b38f483f68), un onglet par liste."]
    for champ in champs:
        type_uml, _ = modele[champ["name"]]
        if type_uml not in enumerations:
            continue
        valeurs = enumerations[type_uml]
        lignes += ["", f"#### {type_uml}", "", f"Attribut `{champ['name']}`, onglet `{champ['name']}` du modèle tableur.", ""]
        if champ["name"] not in onglets:
            erreurs.append(f"onglet {champ['name']} absent du modèle tableur")
            colonnes, definitions = [], {}
        else:
            colonnes, definitions, ordre = onglets[champ["name"]]
            if ordre != valeurs:
                erreurs.append(f"valeurs de l'onglet {champ['name']} du tableur différentes de schema.json :\n    tableur : {ordre}\n    schéma : {valeurs}")
        corps = [[cellule(v)] + [cellule(definitions.get(v, {}).get(c, "")) for c in colonnes] for v in valeurs]
        lignes += tableau(["Valeur"] + list(colonnes), corps)

    lignes += ["", FIN]
    return lignes, erreurs


def main(arguments):
    parseur = argparse.ArgumentParser(description="Catalogue d'objets de MODELE.md")
    parseur.add_argument("--ecrire", action="store_true", help="réécrit le catalogue de MODELE.md")
    parseur.add_argument("--tableur", help="fichier .xlsx local à lire au lieu de l'API")
    options = parseur.parse_args(arguments)

    with open("schema.json", encoding="utf-8") as f:
        champs = json.load(f)["fields"]
    attributs, enumerations = lire_diagramme(MODELE)
    lignes, erreurs = construire(champs, attributs, enumerations, lire_tableur(options.tableur))
    for e in erreurs:
        print(f"modèle tableur : {e}")

    with open(MODELE, encoding="utf-8") as f:
        texte = f.read()
    if DEBUT not in texte or FIN not in texte:
        sys.exit(f"{MODELE} : marqueurs du catalogue introuvables")
    avant, reste = texte.split(DEBUT, 1)
    _, apres = reste.split(FIN, 1)
    nouveau = avant + "\n".join(lignes) + apres

    if options.ecrire:
        with open(MODELE, "w", encoding="utf-8", newline="\n") as f:
            f.write(nouveau)
        print(f"{MODELE} : catalogue réécrit")
    elif nouveau != texte:
        print(f"{MODELE} : catalogue pas à jour, lancer : python .github/workflows/catalogue.py --ecrire")
        return 1
    else:
        print(f"{MODELE} : catalogue à jour")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
