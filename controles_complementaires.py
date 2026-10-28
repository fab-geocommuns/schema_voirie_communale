"""Contrôles complémentaires d'un fichier CSV des voies locales.

Table Schema ne sait pas exprimer ces règles. Le script les vérifie en complément de la validation du schéma :

- cohérence du numéro avec le classement (voie communale : préfixe C ou VC ; chemin rural : préfixe R ou CR) ;
- largeur moyenne obligatoire pour une voie communale (circulaire du 31 juillet 1961) ;
- état obligatoire pour un chemin rural (arrêté du 16 février 2023) ;
- type de géométrie (LineString ou MultiLineString) ;
- coordonnées des points initial et final obligatoires lorsque la ligne a une géométrie ;
- coordonnées des points et de la géométrie dans l'emprise de la France (métropole et outre-mer), ce qui détecte aussi
  les longitudes et latitudes inversées et les systèmes de coordonnées projetés (Lambert 93) ;
- extrémités de la géométrie cohérentes avec les points initial et final ;
- servitudes non répétées.

Les cellules vides ou mal formées sont ignorées : c'est le rôle de la validation du schéma de les signaler.

Documentation complète (règles, codes d'erreur, exemples, limites) : CONTROLES.md.

Usage : python controles_complementaires.py fichier.csv [--json]
Code de sortie : 0 si aucune erreur, 1 sinon.
"""
import argparse
import csv
import json
import re
import sys

REGLES_NUMERO = {
    "Voie communale": (re.compile(r"^([Vv]|)[Cc]\s?\d+(\s?[A-Za-z]+)?$"), "C ou VC"),
    "Chemin rural": (re.compile(r"^([Cc]|)[Rr]\s?\d+(\s?[A-Za-z]+)?$"), "R ou CR"),
}

GEOMETRIES_ATTENDUES = ("LineString", "MultiLineString")

# champ : (code d'erreur, classements pour lesquels il est obligatoire, texte qui l'impose)
OBLIGATOIRES_PAR_CLASSEMENT = {
    "largeur_moyenne": ("largeur-obligatoire", ("Voie communale",), "circulaire du 31 juillet 1961"),
    "etat": ("etat-obligatoire", ("Chemin rural",), "arrêté du 16 février 2023"),
}

# (nom, longitude min, longitude max, latitude min, latitude max) : emprises approximatives
EMPRISES = (
    ("France métropolitaine et Corse", -5.5, 10.0, 41.0, 51.5),
    ("Guadeloupe, Saint-Martin et Saint-Barthélemy", -63.2, -60.8, 15.8, 18.2),
    ("Martinique", -61.3, -60.7, 14.3, 14.95),
    ("Guyane", -54.7, -51.5, 2.0, 6.0),
    ("La Réunion", 55.0, 56.0, -21.5, -20.8),
    ("Mayotte", 44.9, 45.4, -13.1, -12.5),
    ("Saint-Pierre-et-Miquelon", -56.5, -56.0, 46.7, 47.2),
    ("Wallis-et-Futuna", -178.3, -176.0, -14.5, -13.0),
    ("Polynésie française", -155.0, -134.0, -28.0, -7.0),
    ("Nouvelle-Calédonie", 163.0, 169.0, -23.0, -19.0),
)

TOLERANCE_EXTREMITES = 1e-4  # degrés, environ 10 mètres


def dans_la_france(lon, lat):
    return any(lon_min <= lon <= lon_max and lat_min <= lat <= lat_max for _, lon_min, lon_max, lat_min, lat_max in EMPRISES)


def lire_geopoint(valeur):
    parties = valeur.strip().split(",")
    if len(parties) != 2:
        return None
    try:
        return float(parties[0]), float(parties[1])
    except ValueError:
        return None


def lire_json(valeur):
    try:
        return json.loads(valeur)
    except ValueError:
        return None


def positions(geometrie):
    """Liste des lignes (listes de positions) d'une géométrie LineString ou MultiLineString, ou None si mal formée."""
    try:
        coordonnees = geometrie["coordinates"]
        lignes = [coordonnees] if geometrie["type"] == "LineString" else coordonnees
        resultat = []
        for ligne in lignes:
            resultat.append([(float(p[0]), float(p[1])) for p in ligne])
        return resultat if resultat and all(resultat) else None
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def probleme_emprise(lon, lat):
    if dans_la_france(lon, lat):
        return None
    if abs(lon) > 180 or abs(lat) > 90:
        return "les coordonnées sont hors des limites de WGS 84 (système projeté, par exemple Lambert 93 ?)"
    if dans_la_france(lat, lon):
        return "la longitude et la latitude semblent inversées"
    return "les coordonnées sont hors de l'emprise de la France"


def proches(a, b):
    return abs(a[0] - b[0]) <= TOLERANCE_EXTREMITES and abs(a[1] - b[1]) <= TOLERANCE_EXTREMITES


def controler_ligne(ligne):
    """Retourne la liste des (champ, code, message) d'une ligne du fichier."""
    erreurs = []

    numero = (ligne.get("numero") or "").strip()
    classement = (ligne.get("classement") or "").strip()
    if numero and classement in REGLES_NUMERO:
        motif, prefixes = REGLES_NUMERO[classement]
        if not motif.match(numero):
            erreurs.append(("numero", "numero-classement", f"le numéro « {numero} » ne convient pas au classement « {classement} » (préfixe attendu : {prefixes})"))

    for champ, (code, classements, texte) in OBLIGATOIRES_PAR_CLASSEMENT.items():
        if classement in classements and not (ligne.get(champ) or "").strip():
            erreurs.append((champ, code, f"obligatoire pour le classement « {classement} » ({texte})"))

    ini = lire_geopoint(ligne.get("point_ini_coordonnees") or "")
    fin = lire_geopoint(ligne.get("point_fin_coordonnees") or "")
    for champ, point in (("point_ini_coordonnees", ini), ("point_fin_coordonnees", fin)):
        if point:
            probleme = probleme_emprise(*point)
            if probleme:
                erreurs.append((champ, "coordonnees-emprise", probleme))

    contenu = (ligne.get("geometry") or "").strip()
    if contenu:
        for champ in ("point_ini_coordonnees", "point_fin_coordonnees"):
            if not (ligne.get(champ) or "").strip():
                erreurs.append((champ, "points-obligatoires", "obligatoire lorsque la voie est représentée graphiquement (arrêté du 16 février 2023)"))

    geometrie = lire_json(contenu) if contenu else None
    if isinstance(geometrie, dict) and "type" in geometrie:
        if geometrie["type"] not in GEOMETRIES_ATTENDUES:
            erreurs.append(("geometry", "geometry-type", f"géométrie de type {geometrie['type']} (LineString ou MultiLineString attendu)"))
        else:
            lignes = positions(geometrie)
            if lignes:
                hors_emprise = next((p for l in lignes for p in l if probleme_emprise(*p)), None)
                if hors_emprise:
                    erreurs.append(("geometry", "geometry-emprise", probleme_emprise(*hors_emprise)))
                elif ini and fin and dans_la_france(*ini) and dans_la_france(*fin):
                    debut, bout = lignes[0][0], lignes[-1][-1]
                    if not ((proches(ini, debut) and proches(fin, bout)) or (proches(ini, bout) and proches(fin, debut))):
                        erreurs.append(("geometry", "geometry-extremites", "les extrémités de la géométrie ne correspondent pas aux points initial et final"))

    servitudes = lire_json(ligne.get("servitudes") or "")
    if isinstance(servitudes, list):
        repetees = sorted({v for v in servitudes if isinstance(v, str) and servitudes.count(v) > 1})
        if repetees:
            erreurs.append(("servitudes", "servitudes-doublon", "valeurs répétées : " + ", ".join(repetees)))

    return erreurs


def controler(chemin):
    resultat = []
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        for numero_ligne, ligne in enumerate(csv.DictReader(f), start=2):
            for champ, code, message in controler_ligne(ligne):
                resultat.append({"row": numero_ligne, "field": champ, "code": code, "message": message})
    return resultat


def main(arguments):
    parseur = argparse.ArgumentParser(description="Contrôles complémentaires d'un fichier CSV des voies locales.")
    parseur.add_argument("fichier")
    parseur.add_argument("--json", action="store_true", help="affiche les erreurs au format JSON")
    options = parseur.parse_args(arguments)

    erreurs = controler(options.fichier)
    if options.json:
        print(json.dumps(erreurs, ensure_ascii=False, indent=2))
    elif erreurs:
        print(f"{options.fichier} : {len(erreurs)} erreur(s)")
        for e in erreurs:
            print(f"  - ligne {e['row']}, {e['field']} : {e['message']}")
    else:
        print(f"{options.fichier} : aucune erreur")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
