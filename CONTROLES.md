# Contrôles complémentaires

Le script [controles_complementaires.py](controles_complementaires.py) vérifie des règles que Table Schema ne sait pas exprimer. Il complète la validation du schéma ([schema.json](schema.json)), il ne la remplace pas.

## Sommaire

- [Pourquoi ce script](#pourquoi-ce-script)
- [Utilisation](#utilisation)
- [Les contrôles](#les-contrôles)
- [Emprises utilisées](#emprises-utilisées)
- [Limites](#limites)
- [Maintenance](#maintenance)

## Pourquoi ce script

Table Schema vérifie chaque cellule isolément : son type, sa liste de valeurs, son motif. Il ne peut pas :

- comparer deux colonnes entre elles (le numéro et le classement, la géométrie et les points initial et final) ;
- contrôler le contenu d'une géométrie GeoJSON (son type, ses coordonnées) ;
- détecter des valeurs répétées dans une liste ;
- rendre une colonne obligatoire seulement quand une autre est renseignée.

Ces erreurs sont pourtant probables chez les producteurs : un `Point` à la place d'une ligne, des coordonnées en Lambert 93, une longitude et une latitude permutées, un chemin rural numéroté `VC 3`. Un fichier peut les contenir et être déclaré valide par le schéma seul.

## Utilisation

**Prérequis :** Python 3. Aucune bibliothèque à installer. Le script a été testé avec Python 3.12 et 3.13.

```bash
python controles_complementaires.py mon-fichier.csv
```

Le fichier doit être un CSV au format décrit dans le [README](README.md#format-des-fichiers) : encodage UTF-8, séparateur virgule, guillemets doubles.

| Option ou résultat | Effet |
| --- | --- |
| *(aucune)* | Affiche les erreurs en clair, une par ligne. |
| `--json` | Affiche les erreurs au format JSON : une liste d'objets avec `row`, `field`, `code` et `message`. |
| Code de sortie `0` | Aucune erreur. |
| Code de sortie `1` | Au moins une erreur. |

La valeur `row` (« ligne » dans l'affichage en clair) est la ligne du fichier : l'en-tête est la ligne 1, la première voie est la ligne 2.

**Exemple de sortie** (extrait de l'exécution sur [exemple-invalide.csv](exemple-invalide.csv)) :

```text
exemple-invalide.csv : 16 erreur(s)
  - ligne 3, numero : le numéro « 12 » ne convient pas au classement « Voie communale » (préfixe attendu : C ou VC)
  - ligne 6, geometry : géométrie de type Point (LineString ou MultiLineString attendu)
  - ligne 8, point_ini_coordonnees : la longitude et la latitude semblent inversées
  - ligne 9, servitudes : valeurs répétées : PDIPR
```

À lancer **en plus** de la validation du schéma :

```bash
frictionless validate --schema schema.json mon-fichier.csv
python controles_complementaires.py mon-fichier.csv
```

## Les contrôles

Chaque erreur porte un code, le champ concerné et un message. Les cellules vides ou mal formées sont ignorées par le script (c'est la validation du schéma qui les signale), sauf pour `largeur-obligatoire`, `etat-obligatoire` et `points-obligatoires`, dont l'objet est justement de signaler une cellule vide.

| Code | Champ | Règle |
| --- | --- | --- |
| [`numero-classement`](#numero-classement) | `numero` | Le préfixe du numéro correspond au classement. |
| [`largeur-obligatoire`](#largeur-obligatoire) | `largeur_moyenne` | La largeur moyenne est renseignée pour une voie communale. |
| [`etat-obligatoire`](#etat-obligatoire) | `etat` | L'état est renseigné pour un chemin rural. |
| [`points-obligatoires`](#points-obligatoires) | `point_ini_coordonnees`, `point_fin_coordonnees` | Les deux points sont renseignés si la ligne a une géométrie. |
| [`coordonnees-emprise`](#coordonnees-emprise) | `point_ini_coordonnees`, `point_fin_coordonnees` | Les coordonnées sont en WGS 84, dans l'emprise de la France, dans l'ordre longitude puis latitude. |
| [`geometry-type`](#geometry-type) | `geometry` | La géométrie est une `LineString` ou une `MultiLineString`. |
| [`geometry-emprise`](#geometry-emprise) | `geometry` | Les positions de la géométrie sont en WGS 84 et dans l'emprise de la France. |
| [`geometry-extremites`](#geometry-extremites) | `geometry` | Les extrémités de la géométrie sont les points initial et final. |
| [`servitudes-doublon`](#servitudes-doublon) | `servitudes` | Aucune servitude n'est répétée. |

### numero-classement

**Règle.** Pour une **voie communale**, le numéro commence par `C` ou `VC`. Pour un **chemin rural**, il commence par `R` ou `CR`. Les majuscules et les minuscules sont acceptées, avec un espace facultatif avant le numéro et un suffixe alphabétique facultatif (`VC 12`, `c12bis`, `CR 1 bis`, `R14E`).

**Lignes concernées.** Seulement les lignes dont le classement est `Voie communale` ou `Chemin rural`. Les autres classements (`Route départementale`, `Voie intercommunale`, etc.) n'ont pas de règle : le schéma accepte n'importe quel préfixe de 1 à 3 lettres.

| | Classement | Numéro | Résultat |
| --- | --- | --- | --- |
| Erreur | `Voie communale` | `CR 3` | `le numéro « CR 3 » ne convient pas au classement « Voie communale » (préfixe attendu : C ou VC)` |
| Valide | `Voie communale` | `VC 3` | |
| Valide | `Route départementale` | `RD 26` | |

**Correction.** Corriger le numéro (`VC 3`) ou le classement (`Chemin rural`), selon celui des deux qui est faux.

### largeur-obligatoire

**Règle.** Pour une **voie communale**, `largeur_moyenne` est renseignée (circulaire du 31 juillet 1961). Pour les chemins ruraux, l'arrêté du 16 février 2023 la rend seulement possible. Dans le schéma, la colonne est donc facultative, car une ligne d'un autre classement n'a pas à la renseigner.

**Lignes concernées.** Seulement les lignes dont le classement est `Voie communale`. Les autres classements n'ont pas de règle, faute de texte les concernant. Une largeur renseignée mais invalide (`0`, `3,5`) est signalée par la validation du schéma, pas par le script.

| | Classement | Largeur moyenne | Résultat |
| --- | --- | --- | --- |
| Erreur | `Voie communale` | *(vide)* | `obligatoire pour le classement « Voie communale » (circulaire du 31 juillet 1961)` |
| Valide | `Voie communale` | `5` | |
| Valide | `Chemin rural` | *(vide)* | |

**Correction.** Renseigner la largeur moyenne en mètres, avec un point comme séparateur décimal (`3.5`).

### etat-obligatoire

**Règle.** Pour un **chemin rural**, `etat` est renseigné (arrêté du 16 février 2023). La circulaire du 31 juillet 1961, qui concerne les voies communales, ne le demande pas. Dans le schéma, la colonne est donc facultative, car une ligne d'un autre classement n'a pas à la renseigner.

**Lignes concernées.** Seulement les lignes dont le classement est `Chemin rural`. Les autres classements n'ont pas de règle, faute de texte les concernant. Une valeur renseignée mais absente de la liste (`Excellent`) est signalée par la validation du schéma, pas par le script.

| | Classement | État | Résultat |
| --- | --- | --- | --- |
| Erreur | `Chemin rural` | *(vide)* | `obligatoire pour le classement « Chemin rural » (arrêté du 16 février 2023)` |
| Valide | `Chemin rural` | `Bon` | |
| Valide | `Voie communale` | *(vide)* | |

**Correction.** Renseigner l'une des valeurs de la liste du champ `etat` (`Bon`, `Moyen`, `Mauvais`, `Très mauvais`, `En projet`, etc.).

### points-obligatoires

**Règle.** Quand la colonne `geometry` est renseignée, `point_ini_coordonnees` et `point_fin_coordonnees` doivent l'être aussi (arrêté du 16 février 2023 : les coordonnées sont obligatoires si la voie est représentée graphiquement). Dans le schéma, ces deux colonnes sont facultatives, car une voie sans géométrie n'a pas à les renseigner.

**Lignes concernées.** Toutes les lignes dont la cellule `geometry` n'est pas vide, même si son contenu est invalide. Une erreur est émise pour chaque point manquant.

**Correction.** Renseigner le point manquant avec la première position de la géométrie pour le point initial, et la dernière pour le point final, au format `longitude, latitude`.

### coordonnees-emprise

**Règle.** Les coordonnées d'un point doivent être dans l'[emprise de la France](#emprises-utilisées). Le message précise la cause probable :

| Message | Cause |
| --- | --- |
| `la longitude et la latitude semblent inversées` | Les valeurs, une fois permutées, tombent dans l'emprise de la France. Exemple : `48.0, -1.5` à la place de `-1.5, 48.0`. |
| `les coordonnées sont hors des limites de WGS 84 (système projeté, par exemple Lambert 93 ?)` | Une valeur dépasse 180 (longitude) ou 90 (latitude) en valeur absolue. |
| `les coordonnées sont hors de l'emprise de la France` | Les coordonnées sont des valeurs WGS 84 plausibles, mais hors de France. |

**Lignes concernées.** Les lignes dont la cellule est de la forme `nombre, nombre`. Table Schema rejette déjà une latitude hors de -90 / 90 : le script la signale aussi, avec une explication.

**Correction.** Écrire `longitude, latitude`, en degrés décimaux WGS 84 (EPSG:4326). Beaucoup d'applications cartographiques affichent la latitude en premier : l'ordre est à vérifier.

### geometry-type

**Règle.** Le champ `type` de la géométrie GeoJSON vaut `LineString` ou `MultiLineString`. Table Schema accepte tout type GeoJSON valide (`Point`, `Polygon`...).

**Lignes concernées.** Les lignes dont la cellule `geometry` est un objet JSON ayant un champ `type`.

**Exemple d'erreur.** `géométrie de type Point (LineString ou MultiLineString attendu)`

**Correction.** Fournir le tracé de la voie sous forme de ligne. Une voie en plusieurs morceaux non connectés est une `MultiLineString`.

### geometry-emprise

**Règle.** Toutes les positions de la géométrie sont dans l'[emprise de la France](#emprises-utilisées). Le message est le même que pour [coordonnees-emprise](#coordonnees-emprise), avec les mêmes causes.

**Lignes concernées.** Les lignes dont la géométrie est une `LineString` ou une `MultiLineString` bien formée. Le script signale la première position fautive.

**Exemple d'erreur.** Une ligne en Lambert 93, `{"type":"LineString","coordinates":[[351000,6789000],[351100,6789100]]}`, est acceptée par le schéma et signalée par le script.

**Correction.** Reprojeter la géométrie en WGS 84 avant de l'écrire dans le fichier, avec des coordonnées `[longitude, latitude]`.

### geometry-extremites

**Règle.** La première position de la géométrie et sa dernière position correspondent aux points initial et final, à 0,0001 degré près (environ 10 mètres). Le sens n'importe pas : le point initial peut correspondre au début ou à la fin de la géométrie.

**Lignes concernées.** Les lignes dont la géométrie est bien formée, dans l'emprise de la France, et dont les deux points sont renseignés, lisibles et dans l'emprise de la France. Pour une `MultiLineString`, ce sont le début de la première ligne et la fin de la dernière.

**Exemple d'erreur.** Un point initial `-1.5, 48.0` avec une géométrie qui commence en `[-1.4, 48.1]`.

**Correction.** Aligner les points sur la géométrie, ou la géométrie sur les points.

### servitudes-doublon

**Règle.** Une même servitude n'apparaît qu'une fois dans la liste.

**Lignes concernées.** Les lignes dont la cellule `servitudes` est une liste JSON.

**Exemple d'erreur.** `["PDIPR","PDIPR"]` donne `valeurs répétées : PDIPR`.

**Correction.** Supprimer les doublons : `["PDIPR"]`.

## Emprises utilisées

Les emprises sont des rectangles en longitude et latitude WGS 84 (EPSG:4326), volontairement larges. Une position est acceptée si elle est dans l'un d'eux.

| Territoire | Longitude | Latitude |
| --- | --- | --- |
| France métropolitaine et Corse | -5,5 à 10,0 | 41,0 à 51,5 |
| Guadeloupe, Saint-Martin et Saint-Barthélemy | -63,2 à -60,8 | 15,8 à 18,2 |
| Martinique | -61,3 à -60,7 | 14,3 à 14,95 |
| Guyane | -54,7 à -51,5 | 2,0 à 6,0 |
| La Réunion | 55,0 à 56,0 | -21,5 à -20,8 |
| Mayotte | 44,9 à 45,4 | -13,1 à -12,5 |
| Saint-Pierre-et-Miquelon | -56,5 à -56,0 | 46,7 à 47,2 |
| Wallis-et-Futuna | -178,3 à -176,0 | -14,5 à -13,0 |
| Polynésie française | -155,0 à -134,0 | -28,0 à -7,0 |
| Nouvelle-Calédonie | 163,0 à 169,0 | -23,0 à -19,0 |

Elles sont définies dans la constante `EMPRISES` du script.

## Limites

- **Les emprises sont approximatives.** Un point situé en mer ou dans un pays voisin, à l'intérieur d'un de ces rectangles, n'est pas détecté. Les Terres australes et antarctiques françaises et Clipperton ne sont pas couvertes : leurs voies seraient signalées à tort.
- **Le contrôle des extrémités tolère environ 10 mètres.**
- **Cellules ignorées.** Une cellule vide, une géométrie qui n'est pas du JSON ou des coordonnées qui ne sont pas de la forme `nombre, nombre` ne sont pas signalées par le script. La validation du schéma les signale.
- **Pas de contrôle de la cohérence de la géométrie avec la longueur ou la superficie déclarées**, ni de la topologie (auto-intersections, tronçons qui se chevauchent).
- **Validata n'exécute pas ce script.** Un fichier accepté par Validata peut donc être refusé par le script.

## Maintenance

Ce document décrit le comportement du script. Il est à mettre à jour avec lui, ainsi que [erreurs-attendues.json](erreurs-attendues.json), que la vérification automatique GitHub compare aux erreurs réellement détectées sur [exemple-invalide.csv](exemple-invalide.csv).
