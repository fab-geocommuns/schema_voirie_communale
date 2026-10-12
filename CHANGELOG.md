# Changements

Ce fichier répertorie les changements entre différentes versions du schéma.

## Version 0.1.0 - 2026-10-11

Version initiale, en construction, établie à partir de `proposition_modele_voies_locales.xlsx` :

- une ligne par voie ou par tronçon de voie ;
- noms de champs repris de `proposition_modele_voies_locales.xlsx` en snake_case, les points étant remplacés par des tirets bas (ex. `point_ini.designation` devient `point_ini_designation`) ;
- format d'échange unique : CSV (`schema.json`, Table Schema), avec une colonne `geometry` facultative de type `geojson` (`LineString` ou `MultiLineString`, WGS 84) ;
- coordonnées des points initial et final : un seul champ de type `geopoint` de Table Schema (WGS 84, ordre « longitude, latitude »).
