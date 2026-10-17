# Changements

Ce fichier répertorie les changements entre différentes versions du schéma.

## Version 0.1.0 - 2026-10-17

Publication initiale, version en construction.

Schéma Table Schema d'un fichier CSV décrivant les voies locales (voies communales, chemins ruraux, voies intercommunales, etc.), à raison d'une ligne par voie ou par tronçon de voie, avec ou sans géométrie :

- 23 champs, dont 11 obligatoires : `commune_insee`, `numero`, `classement`, `type`, `appellation`, `point_ini_designation`, `point_fin_designation`, `longueur`, `date_d_affectation`, `largeur_moyenne` et `etat` ;
- format d'échange : CSV encodé en UTF-8, séparateur de champs virgule, guillemets doubles comme caractère d'encadrement, séparateur décimal point ;
- 8 listes de valeurs (`classement`, `type`, `etat`, `servitudes`, `delimitation`, `domanialite`, `gestionnaire`, `revetement`) ;
- `point_ini_coordonnees` et `point_fin_coordonnees` de type `geopoint` (WGS 84, ordre « longitude, latitude »), `servitudes` de type `array` et `geometry` de type `geojson`, facultative ;
- exemples valide et invalide, licence ouverte 2.0 et contrôles de validation en intégration continue.

Écarts avec le modèle initial (`proposition_modele_voies_locales.xlsx`) :

- noms de champs en snake_case, avec un tiret bas à la place des points (`point_ini.designation` devient `point_ini_designation`) ;
- `commune_insee` obligatoire (facultatif dans le modèle initial) ;
- coordonnées des points facultatives (conditionnelles à la représentation graphique dans le modèle initial) ;
- `numero` : le pattern accepte en plus les préfixes en minuscules, un espace avant un suffixe alphabétique et ce suffixe lui-même (`CR 1 bis`, `R 14E`) ;
- `longueur`, `largeur_moyenne` et `superficie` : valeur minimale de 1 (strictement positive dans le modèle initial) ;
- `servitudes` : liste de valeurs (type `array`) au lieu d'une valeur unique ;
- valeurs des listes écrites avec une majuscule initiale.

Écart assumé avec le guide qualité de schema.data.gouv.fr :

- noms de champs en snake_case sans préfixe commun, au lieu du camelCase préfixé recommandé.

Le séparateur point-virgule sans guillemets a été envisagé puis écarté : Validata devine le séparateur, ne permet pas de le déclarer, et se trompe sur les fichiers contenant des géométries. Le format retenu est celui recommandé par le guide : séparateur virgule, avec guillemets doubles.
