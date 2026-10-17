# Schéma des voies locales

> [!TIP]
> Statut : **en construction** (version 0.1.0). Ce schéma est élaboré par le groupe de travail du projet [Voies locales en commun](https://www.voies-locales.beta.gouv.fr/). Il n'est pas un standard CNIG : il s'inspire des recommandations du guide qualité de schema.data.gouv.fr et du processus et des modèles du CNIG (Conseil national de l'information géolocalisée).

Ce dépôt contient le schéma de données (Table Schema) du recensement des voies locales : voies communales, chemins ruraux, voies intercommunales, etc. Le format d'échange est un **CSV**, décrit par [schema.json](schema.json). Une ligne correspond à une **voie** ou à un **tronçon** de voie, avec ou sans géométrie : la colonne `geometry` est facultative et reste vide en l'absence de géométrie.

## Contexte et cadre réglementaire

- Circulaire du 31 juillet 1961 : [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000685464) ;
- Arrêté du 16 février 2023 : [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047247048).

À compléter : enjeux et objectifs, gouvernance du projet Voies locales en commun, cas d'usage, modalités de production des données.

## Contenu du dépôt

- [schema.json](schema.json) : schéma Table Schema du fichier CSV ;
- [dialect.json](dialect.json) : dialecte CSV (séparateur point-virgule, sans encadrement) ;
- [check_format.py](check_format.py) : script de contrôle du format du fichier (encodage, séparateur, absence d'encadrement) ;
- [exemple-valide.csv](exemple-valide.csv) et [exemple-invalide.csv](exemple-invalide.csv) : fichiers d'exemple CSV ; l'exemple valide comporte quatre lignes : une voie communale (VC) et un chemin rural (CR) avec géométrie (respectivement `MultiLineString` et `LineString`), et une VC et un CR sans géométrie ;
- [CHANGELOG.md](CHANGELOG.md) : liste des changements ;
- [LICENSE.md](LICENSE.md) : Licence Ouverte 2.0.

## Format des fichiers

Le format d'échange est un fichier CSV ayant les caractéristiques suivantes :

- **séparateur de champs : le point-virgule** `;` ;
- **aucun caractère d'encadrement des chaînes** (pas de guillemets autour des valeurs) ;
- **séparateur décimal : le point** ;
- **encodage UTF-8**.

Le point-virgule est retenu à la place de la virgule, plus courante, parce que des valeurs peuvent contenir des virgules : les appellations (ex. « Voie communale de Lure, Servaire et Phlimpe »), les coordonnées des points et les géométries GeoJSON. Avec le point-virgule, ces virgules ne nécessitent plus aucun encadrement.

Ce dialecte est décrit par le fichier [dialect.json](dialect.json), au format [CSV Dialect](https://specs.frictionlessdata.io/csv-dialect/), à fournir aux outils qui ne devinent pas le séparateur (voir [Valider un fichier](#valider-un-fichier)).

> [!IMPORTANT]
> Puisqu'aucun encadrement n'est utilisé, une valeur ne doit contenir **ni point-virgule, ni saut de ligne**, et ne doit **pas commencer par un guillemet double**. Les guillemets doubles internes aux valeurs JSON (`geometry`, `servitudes`) sont en revanche sans effet et ne sont pas doublés. Ces règles sont vérifiées par le script [check_format.py](check_format.py) (voir [Valider un fichier](#valider-un-fichier)).

Autres règles :

- toutes les colonnes sont présentes, dans l'ordre du schéma, même vides ;
- coordonnées des points initial et final en WGS 84, dans un seul champ de type `geopoint` au format « longitude, latitude » (ex. `5.466656, 45.445213`), point comme séparateur décimal, 6 décimales au maximum (limite non vérifiée par Table Schema) ; elles sont facultatives dans le schéma mais **obligatoires si la voie est représentée graphiquement** (arrêté du 16 février 2023), règle non vérifiable par Table Schema ;
- `geometry` est une géométrie GeoJSON de type `LineString` ou `MultiLineString`, en WGS 84 (coordonnées `[longitude, latitude]`), écrite telle quelle dans la cellule (ex. `{"type":"LineString","coordinates":[[5.466656,45.445213],[5.471959,45.450308]]}`) ; cellule vide en l'absence de géométrie. Table Schema vérifie seulement que la cellule est un GeoJSON valide : le type de géométrie et le système de coordonnées ne sont pas contrôlés ;
- `servitudes` est une liste JSON écrite telle quelle, par exemple `["PDIPR","DFCI"]` ; cellule vide s'il n'y en a aucune ; les valeurs ne doivent pas être répétées (règle non vérifiable par Table Schema) ;
- valeurs des listes énumérées : première lettre en majuscule (`Voie communale`, `Bon`, `Public`) ;
- toute colonne en plus du schéma est refusée (Table Schema ne permet pas de tolérer des extensions locales).

Le guide qualité de schema.data.gouv.fr privilégie la virgule comme séparateur, tout en précisant que « la question du séparateur [...] n'est pas essentielle » puisque la validation s'appuie sur la structure tabulaire des données. Le choix du point-virgule est donc un **écart assumé** au guide, motivé par la présence de virgules dans les valeurs et par l'usage courant du point-virgule dans les tableurs configurés en français.

### Nommage des fichiers

Règle retenue : `AAAAMMJJ_SIREN_voies-locales.csv`, où

- `AAAAMMJJ` est la date de création du fichier ;
- `SIREN` est le numéro SIREN à 9 chiffres du producteur (commune, EPCI, département) ;
- `voies-locales` est le nom du fichier, en minuscules non accentuées, avec des tirets du milieu ;
- les trois éléments sont séparés par un tiret bas.

Exemple : `20261011_213500953_voies-locales.csv`.

Cette règle est celle du guide qualité de schema.data.gouv.fr (`AAAAMMJJ_idProducteur_nom-du-fichier.extension`). Le nom du producteur en clair n'y figure pas : aucune des conventions de référence ne le fait, toutes identifiant le producteur par un code.

| Référence | Règle de nommage du livrable | Identification du producteur |
| --- | --- | --- |
| Guide qualité schema.data.gouv.fr | `AAAAMMJJ_idProducteur_nom-du-fichier.extension` | SIREN |
| Standard CNIG Accessibilité en voirie (gabarit GeoPackage) | `<INSEE/SIREN>_accessibilite_voirie_AAAAMMJJ.gpkg` | code INSEE ou SIREN |
| Modèle de standard CNIG (Star-Eau) | `Stareau-fr<code>-<SIREN><type><date>.<extension>` | SIREN |
| Métadonnées CNIG | `fr-<SIREN>-thème<date>.xml` | SIREN |
| Standards CNIG ACEN et PDIPR | pas de règle définie | — |

Une variante du type `AAAAMMJJ_voies-locales_SIREN_nomproducteur.csv` a été écartée : elle ajoute un nom en clair redondant avec le SIREN, instable dans le temps (fusions, changements de dénomination) et source de variantes d'écriture (accents, espaces, casse), et elle n'est conforme à aucune des conventions ci-dessus.

Les fichiers d'exemple du dépôt (`exemple-valide.csv`, `exemple-invalide.csv`) ne suivent pas cette règle : leur nom est celui attendu par les outils de validation.

### Nommage des champs

Les noms des champs reprennent ceux du modèle initial (`proposition_modele_voies_locales.xlsx`) : minuscules, snake_case, sans accent, avec un tiret bas à la place des points (`point_ini.designation` devient `point_ini_designation`, `point_ini.coordonnees` devient `point_ini_coordonnees`).

Ce choix, retenu pour la version 0.1.0 et à soumettre au groupe de travail du projet Voies locales en commun, **s'écarte volontairement du guide qualité de schema.data.gouv.fr**, qui recommande des noms en camelCase précédés d'un préfixe commun au standard (par exemple `voieLocNumero`), au singulier. Il se rapproche des exemples du modèle de standard du CNIG (`classe_1_id`, `ban_id`), qui n'impose toutefois aucune règle de nommage des attributs. Conséquences :

- les champs n'ont pas de préfixe commun au standard ;
- `servitudes` est au pluriel, comme dans le modèle initial ;
- les noms ne contiennent ni accent ni caractère spécial, hormis le tiret bas, et ne dépassent pas 50 caractères.

## Valider un fichier

```bash
pip install -r requirements.txt
python check_format.py mon-fichier.csv
frictionless validate --schema schema.json --dialect dialect.json mon-fichier.csv
```

Deux contrôles complémentaires, à lancer dans cet ordre :

1. `check_format.py` vérifie le **format du fichier** : encodage UTF-8, en-têtes identiques à ceux du schéma, même nombre de colonnes sur chaque ligne, aucune valeur commençant par un guillemet double. Il signale ainsi, avec un message explicite, un point-virgule ou un saut de ligne à l'intérieur d'une valeur ;
2. `frictionless validate` vérifie le **contenu** (types, listes de valeurs, contraintes). Il détecte aussi un point-virgule ou un saut de ligne parasite, mais avec des messages moins explicites (`extra-cell`, `missing-cell`).

L'option `--dialect` est indispensable : frictionless suppose par défaut un séparateur virgule.

Un fichier peut aussi être validé en ligne sur [validata.fr](https://validata.fr). Validata devine le séparateur ; en cas de doute sur le résultat, utiliser la commande ci-dessus, qui fait foi.
