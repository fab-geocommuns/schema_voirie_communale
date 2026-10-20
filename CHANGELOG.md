# Changements

Ce fichier répertorie les changements entre différentes versions du schéma.

## Version 0.1.1 - 2026-10-17

Version encore en construction. Les fichiers valides en 0.1.0 le restent, à une exception près : la valeur `Chemin d’exploitation` du champ `classement` s'écrit désormais avec une apostrophe droite.

Changements du schéma :

- `numero` : motif généralisé (préfixe de 1 à 3 lettres, espace facultatif, numéro, suffixe alphabétique facultatif) pour accepter tous les classements (`RD 26`, `N 12`, `A 7`, `CE 1`), qu'un motif limité à `C`, `VC`, `R` et `CR` rejetait ; la cohérence avec le classement pour les voies communales et les chemins ruraux est contrôlée par le script ;
- `largeur_moyenne` : minimum abaissé de 1 à 0,1 pour accepter les sentiers ; le champ reste obligatoire ;
- `classement` : `Chemin d'exploitation` avec une apostrophe droite, comme les autres valeurs contenant une apostrophe (`Plan d'alignement`, `Collectivité d'outre-mer`) ;
- `type` : suppression de la définition de la valeur `Tronçon`, ajoutée à tort à la description et absente du modèle tableur ;
- `id_externe` et `geom_source` : descriptions liées, l'identifiant externe étant celui du référentiel indiqué par `geom_source` (l'identifiant BAN peut y être saisi) ;
- « voies intercommunales » n'est plus citée parmi les voies locales dans les descriptions ; la valeur `Voie intercommunale` reste dans la liste `classement`.

Ajouts :

- `controles_complementaires.py` : contrôles que Table Schema ne sait pas exprimer (numéro et classement, type de géométrie, coordonnées des points obligatoires si la voie a une géométrie, emprise France, longitude et latitude inversées, extrémités de la géométrie, servitudes répétées) ;
- exemple invalide complété (9 lignes) et fichier `erreurs-attendues.json` listant exactement les erreurs attendues ;
- README : réorganisé selon la trame du modèle de README du CNIG (sections à compléter marquées « À compléter »), règle « une ligne par voie ou par tronçon » corrigée avec un exemple, points ouverts (identifiant de ligne, `etat`), encadré sur la virgule décimale, lien vers le modèle tableur, qui évolue en parallèle du schéma ;
- `CONTROLES.md` : documentation détaillée des contrôles complémentaires (règles, codes d'erreur, exemples, emprises, limites) ;
- vérification automatique : déclenchement aussi sur les pull requests, Python 3.12, comparaison exacte des erreurs de l'exemple invalide.

## Version 0.1.0 - 2026-10-17

Publication initiale, version en construction.

Schéma Table Schema d'un fichier CSV décrivant les voies locales (voies communales, chemins ruraux, etc.), à raison d'une ligne par voie ou par tronçon de voie, avec ou sans géométrie :

- 23 champs, dont 11 obligatoires : `commune_insee`, `numero`, `classement`, `type`, `appellation`, `point_ini_designation`, `point_fin_designation`, `longueur`, `date_d_affectation`, `largeur_moyenne` et `etat` ;
- format d'échange : CSV encodé en UTF-8, séparateur de champs virgule, guillemets doubles comme caractère d'encadrement, séparateur décimal point ;
- 8 listes de valeurs (`classement`, `type`, `etat`, `servitudes`, `delimitation`, `domanialite`, `gestionnaire`, `revetement`) ;
- `point_ini_coordonnees` et `point_fin_coordonnees` de type `geopoint` (WGS 84, ordre « longitude, latitude »), `servitudes` de type `array` et `geometry` de type `geojson`, facultative ;
- exemples valide et invalide, licence ouverte 2.0 et contrôles de validation en intégration continue.

Écarts avec le modèle tableur à la publication de la version 0.1.0 :

- noms de champs en snake_case, avec un tiret bas à la place des points (`point_ini.designation` devient `point_ini_designation`) ;
- `commune_insee` obligatoire (facultatif dans le modèle tableur) ;
- coordonnées des points facultatives (conditionnelles à la représentation graphique dans le modèle tableur) ;
- `numero` : le pattern accepte en plus les préfixes en minuscules, un espace avant un suffixe alphabétique et ce suffixe lui-même (`CR 1 bis`, `R 14E`) ;
- `longueur`, `largeur_moyenne` et `superficie` : valeur minimale de 1 (strictement positive dans le modèle tableur) ;
- `servitudes` : liste de valeurs (type `array`) au lieu d'une valeur unique ;
- valeurs des listes écrites avec une majuscule initiale.

Écart assumé avec le guide qualité de schema.data.gouv.fr :

- noms de champs en snake_case sans préfixe commun, au lieu du camelCase préfixé recommandé.

Le séparateur point-virgule sans guillemets a été envisagé puis écarté : Validata devine le séparateur, ne permet pas de le déclarer, et se trompe sur les fichiers contenant des géométries. Le format retenu est celui recommandé par le guide : séparateur virgule, avec guillemets doubles.
