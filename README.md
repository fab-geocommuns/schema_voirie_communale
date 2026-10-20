# Schéma des voies locales

> [!TIP]
> Statut : **en construction** (version 0.1.1). Ce schéma est élaboré par le groupe de travail du projet [Voies locales en commun](https://www.voies-locales.beta.gouv.fr/). Il n'est pas un standard CNIG : il s'inspire des recommandations du guide qualité de schema.data.gouv.fr et du processus et des modèles du CNIG (Conseil national de l'information géolocalisée).

Ce dépôt contient le schéma de données (Table Schema) du recensement des voies locales : voies communales, chemins ruraux, etc. Le format d'échange est un **CSV**, décrit par [schema.json](schema.json). Une ligne correspond à une **voie** ou à un **tronçon** de voie, avec ou sans géométrie : la colonne `geometry` est facultative et reste vide en l'absence de géométrie.

Davantage d'informations sur le site du projet : [Voies locales en commun](https://www.voies-locales.beta.gouv.fr/).

## Contexte

À compléter.

## Cadre juridique

- Circulaire du 31 juillet 1961 : [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000685464) ;
- Arrêté du 16 février 2023 : [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047247048).

## Finalité

À compléter.

## Cas d'usage

À compléter.

## Organisation du dépôt

- [schema.json](schema.json) : schéma Table Schema du fichier CSV ;
- [modèle tableur](https://fichiers.numerique.gouv.fr/wopi/cdf35f2b-302f-49d0-99e1-e4b38f483f68) : le modèle de données au format tableur, publié en dehors du dépôt. Il évolue **en parallèle** du schéma : toute modification de l'un est reportée dans l'autre ;
- [controles_complementaires.py](controles_complementaires.py) : script de contrôles que Table Schema ne sait pas exprimer, décrit dans [CONTROLES.md](CONTROLES.md) ;
- [exemple-valide.csv](exemple-valide.csv) et [exemple-invalide.csv](exemple-invalide.csv) : fichiers d'exemple CSV ; l'exemple valide comporte quatre lignes : une voie communale (VC) et un chemin rural (CR) avec géométrie (respectivement `MultiLineString` et `LineString`), et une VC et un CR sans géométrie ; l'exemple invalide comporte neuf lignes et illustre, ligne par ligne, les erreurs détectées par le schéma et par le script ;
- [erreurs-attendues.json](erreurs-attendues.json) : liste exacte des erreurs de l'exemple invalide, comparée à celles détectées par la vérification automatique ; à mettre à jour à chaque changement du schéma ou du script ;
- [CHANGELOG.md](CHANGELOG.md) : liste des changements ;
- [LICENSE.md](LICENSE.md) : Licence Ouverte 2.0.

## Modalités de production des données

À compléter.

## Format des fichiers

Le format d'échange est un fichier CSV ayant les caractéristiques suivantes, conformes au guide qualité de schema.data.gouv.fr :

- **séparateur de champs : la virgule** `,` ;
- **guillemets doubles `"` comme caractère d'encadrement** : toute cellule contenant une virgule, un guillemet double ou un saut de ligne est entourée de guillemets doubles, et les guillemets doubles qu'elle contient sont doublés ;
- **séparateur décimal : le point** ;
- **encodage UTF-8**.

Les valeurs contenant des virgules sont fréquentes : appellations (ex. « Voie communale de Lure, Servaire et Phlimpe »), coordonnées des points, géométries GeoJSON. Les logiciels qui écrivent du CSV (tableurs, bibliothèques de programmation) ajoutent ces guillemets automatiquement.

> [!NOTE]
> Le point-virgule, plus lisible dans les tableurs français et utilisable sans guillemets, a été écarté : l'outil de validation Validata de schema.data.gouv.fr devine le séparateur et ne permet pas de le déclarer. Il se trompe sur les fichiers contenant des géométries, dont les virgules l'emportent sur les points-virgules.

> [!WARNING]
> Les nombres décimaux s'écrivent avec un **point** (`3.5`) et non une virgule (`3,5`). Un export depuis un tableur français doit être corrigé avant dépôt : un nombre écrit avec une virgule est rejeté, avec seulement un message « type-error » qui n'en donne pas la cause.

Autres règles :

- toutes les colonnes sont présentes, dans l'ordre du schéma, même vides ;
- `numero` : préfixe de 1 à 3 lettres, espace facultatif, numéro, puis suffixe alphabétique facultatif (`VC 12`, `CR1`, `C12bis`, `RD 26`, `N 12`). Le motif du schéma est volontairement large pour accepter tous les classements ; pour une **voie communale** le préfixe doit être `C` ou `VC`, pour un **chemin rural** `R` ou `CR`, ce que contrôle le script (`CR 3` avec « Voie communale » est signalé). « Voie intercommunale » et les autres classements n'ont pas de règle de numéro ;
- `largeur_moyenne` est obligatoire (circulaire du 31 juillet 1961) et strictement positive : Table Schema ne sait exprimer qu'un minimum inclusif, il est fixé à 0,1 ;
- coordonnées des points initial et final en WGS 84, dans un seul champ de type `geopoint` au format « longitude, latitude » entouré de guillemets doubles (ex. `"5.466656, 45.445213"`), point comme séparateur décimal, 6 décimales au maximum (limite non vérifiée par Table Schema) ; elles sont facultatives dans le schéma mais **obligatoires si la voie est représentée graphiquement** (arrêté du 16 février 2023), règle non vérifiable par Table Schema, contrôlée par le script. Table Schema **ne détecte pas l'inversion** de la longitude et de la latitude (`"48.0, -1.5"` est accepté, -1,5 étant une latitude possible) : le script la signale ;
- `geometry` est une géométrie GeoJSON de type `LineString` ou `MultiLineString`, en WGS 84 (coordonnées `[longitude, latitude]`), écrite dans la cellule avec les guillemets doublés (ex. `"{""type"":""LineString"",""coordinates"":[[5.466656,45.445213],[5.471959,45.450308]]}"`) ; cellule vide en l'absence de géométrie. Table Schema vérifie seulement que la cellule est un GeoJSON valide : le type de géométrie, le système de coordonnées (un `Point`, un `Polygon` ou des coordonnées en Lambert 93 sont acceptés) et la cohérence des extrémités avec les points initial et final sont contrôlés par le script ;
- `servitudes` est une liste JSON entre guillemets, par exemple `"[""PDIPR"",""DFCI""]"` ; cellule vide s'il n'y en a aucune ; les valeurs ne doivent pas être répétées (règle non vérifiable par Table Schema, contrôlée par le script) ;
- `id_externe` est l'identifiant de la voie dans le référentiel indiqué par `geom_source` (BD TOPO IGN, OSM, BAN, base locale…) ; l'identifiant de la Base Adresse Nationale peut y être saisi, avec `geom_source` valant « BAN ». Le référentiel de l'identifiant et celui de la géométrie sont supposés identiques, et une voie sans géométrie n'a donc pas de référentiel déclaré ;
- valeurs des listes énumérées : première lettre en majuscule (`Voie communale`, `Bon`, `Public`), apostrophe droite (`Chemin d'exploitation`) ;
- toute colonne en plus du schéma est refusée (Table Schema ne permet pas de tolérer des extensions locales).

### Une ligne par voie ou par tronçon

Chaque ligne décrit une portion de voie : soit la voie entière, soit l'un de ses tronçons. Une voie découpée en tronçons est décrite par **une ligne par tronçon**. Les lignes d'une même voie ont les mêmes `commune_insee`, `numero` et `classement` ; chacune porte ses propres longueur, largeur, état et géométrie. Les tronçons d'une voie ne se chevauchent pas.

**Il ne faut jamais fournir à la fois la voie entière et ses tronçons** : leurs longueurs seraient comptées deux fois. Aucune colonne ne distingue une voie d'un tronçon.

Exemple : la voie communale `VC 3`, décrite en deux tronçons (seules quelques colonnes sont affichées ; les autres sont renseignées sur chaque ligne) :

| commune_insee | numero | classement | appellation | point_ini_designation | point_fin_designation | longueur |
| --- | --- | --- | --- | --- | --- | --- |
| 35095 | VC 3 | Voie communale | Rue des Écoles | Place de la Mairie | Carrefour avec la rue des Tilleuls | 420 |
| 35095 | VC 3 | Voie communale | Rue des Écoles | Carrefour avec la rue des Tilleuls | Intersection avec la RD 4 | 311.5 |

### Nommage des fichiers

Règle retenue : `AAAAMMJJ_SIREN_voies-locales.csv`, où

- `AAAAMMJJ` est la date de création du fichier ;
- `SIREN` est le numéro SIREN à 9 chiffres du producteur (commune, EPCI, département) ;
- `voies-locales` est le nom du fichier, en minuscules non accentuées, avec des tirets du milieu (`-`) ;
- les trois éléments sont séparés par un tiret bas (underscore, `_`).

Exemple : `20261011_213500953_voies-locales.csv`.

Cette règle est celle du guide qualité de schema.data.gouv.fr.

Les fichiers d'exemple du dépôt (`exemple-valide.csv`, `exemple-invalide.csv`) ne suivent pas cette règle : leur nom est celui attendu par les outils de validation.

### Nommage des champs

Les noms des champs reprennent ceux du [modèle tableur](https://fichiers.numerique.gouv.fr/wopi/cdf35f2b-302f-49d0-99e1-e4b38f483f68) : minuscules, snake_case, sans accent, avec un tiret bas à la place des points (`point_ini.designation` devient `point_ini_designation`, `point_ini.coordonnees` devient `point_ini_coordonnees`).

Ce choix **s'écarte volontairement du guide qualité de schema.data.gouv.fr**, qui recommande des noms en camelCase précédés d'un préfixe commun au standard (par exemple `voieLocNumero`), au singulier. Il se rapproche des exemples du modèle de standard du CNIG (`classe_1_id`, `ban_id`), qui n'impose toutefois aucune règle de nommage des attributs. Conséquences :

- les champs n'ont pas de préfixe commun au standard ;
- `servitudes` est au pluriel, comme dans le modèle tableur ;
- les noms ne contiennent ni accent ni caractère spécial, hormis le tiret bas, et ne dépassent pas 50 caractères.

## Valider un fichier

```bash
pip install -r requirements.txt
frictionless validate --schema schema.json mon-fichier.csv
python controles_complementaires.py mon-fichier.csv
```

Deux contrôles complémentaires :

1. `frictionless validate` vérifie le **schéma** : colonnes, types, listes de valeurs, contraintes. Un fichier peut aussi être validé en ligne sur [validata.fr](https://validata.fr) ;
2. `controles_complementaires.py` vérifie ce que Table Schema ne sait pas exprimer : cohérence du numéro et du classement, géométrie (type, coordonnées, extrémités), coordonnées des points obligatoires si la ligne a une géométrie, servitudes répétées. Validata n'exécute pas ce script. Chaque contrôle est décrit dans [CONTROLES.md](CONTROLES.md).

La vérification automatique GitHub contrôle le schéma, l'exemple valide, le script, la cohérence des numéros de version, et que l'exemple invalide produit **exactement** les erreurs de [erreurs-attendues.json](erreurs-attendues.json).

## Informations et participation

### Actualisation

Statut : **en construction**.

**Points ouverts.** Ces choix sont connus et pourront être rediscutés :

- **pas d'identifiant de ligne** : décision prise avec l'ANCT, à rediscuter. Sans identifiant, il n'y a ni mise à jour incrémentale, ni comparaison automatique entre deux versions d'un fichier ; `id_externe` ne joue pas ce rôle ;
- **`etat` regroupe deux notions** : le cycle de vie (En projet, En construction, Fermé, Supprimé, Inexistant) et l'état d'entretien (Bon, Moyen, Mauvais, Très mauvais). Une voie fermée **et** en mauvais état ne peut pas être décrite.

### Comment contribuer

À compléter.

### Nous contacter

À compléter.

### Licence

Ce schéma est publié sous [Licence Ouverte 2.0](LICENSE.md).
