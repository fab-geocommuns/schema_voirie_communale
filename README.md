# Schéma des voies locales

> [!TIP]
> Statut : **en construction** (version 0.1.0). Ce schéma est élaboré par le [GT Voirie communale](https://www.voies-locales.beta.gouv.fr/). Il n'est pas un standard CNIG : il s'inspire des recommandations du guide qualité de schema.data.gouv.fr et du processus et des modèles du CNIG (Conseil national de l'information géolocalisée).

Ce dépôt contient le schéma de données (Table Schema) du recensement des voies locales : voies communales, chemins ruraux, voies intercommunales, etc. Le format d'échange est un **CSV**, décrit par [schema.json](schema.json). Une ligne correspond à une **voie** ou à un **tronçon** de voie, avec ou sans géométrie : la colonne `geometry` est facultative et reste vide en l'absence de géométrie.

## Contexte et cadre réglementaire

- Circulaire du 31 juillet 1961 : [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000685464) ;
- Arrêté du 16 février 2023 : [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047247048).

À compléter : enjeux et objectifs, gouvernance du GT Voirie communale, cas d'usage, modalités de production des données.

## Contenu du dépôt

- [schema.json](schema.json) : schéma Table Schema du fichier CSV ;
- [exemple-valide.csv](exemple-valide.csv) et [exemple-invalide.csv](exemple-invalide.csv) : fichiers d'exemple CSV ;
- [CHANGELOG.md](CHANGELOG.md) : liste des changements ;
- [LICENSE.md](LICENSE.md) : Licence Ouverte 2.0.

## Format des fichiers

- CSV encodé en UTF-8, séparateur virgule ; toute cellule contenant une virgule, un guillemet double ou un saut de ligne est entourée de guillemets doubles, et les guillemets qu'elle contient sont doublés ;
- toutes les colonnes sont présentes, dans l'ordre du schéma, même vides ;
- coordonnées des points initial et final en WGS 84, dans un seul champ de type `geopoint` au format « longitude, latitude » entouré de guillemets doubles (ex. `"5.466656, 45.445213"`), point comme séparateur décimal, 6 décimales au maximum (limite non vérifiée par Table Schema) ; elles sont facultatives dans le schéma mais **obligatoires si la voie est représentée graphiquement** (arrêté du 16 février 2023), règle non vérifiable par Table Schema ;
- `geometry` est une géométrie GeoJSON de type `LineString` ou `MultiLineString`, en WGS 84 (coordonnées `[longitude, latitude]`), écrite dans la cellule avec les guillemets doublés (ex. `"{""type"":""LineString"",""coordinates"":[[5.466656,45.445213],[5.471959,45.450308]]}"`) ; cellule vide en l'absence de géométrie. Table Schema vérifie seulement que la cellule est un GeoJSON valide : le type de géométrie et le système de coordonnées ne sont pas contrôlés ;
- `servitudes` est une liste JSON entre guillemets, par exemple `"[""PDIPR"",""DFCI""]"` ; cellule vide s'il n'y en a aucune ; les valeurs ne doivent pas être répétées (règle non vérifiable par Table Schema) ;
- valeurs des listes énumérées : première lettre en majuscule (`Voie communale`, `Bon`, `Public`) ;
- toute colonne en plus du schéma est refusée (Table Schema ne permet pas de tolérer des extensions locales).

### Nommage des fichiers

Règle du guide qualité de schema.data.gouv.fr : `AAAAMMJJ_SIREN_voies-locales.csv`, où

- `AAAAMMJJ` est la date de création du fichier ;
- `SIREN` est le numéro SIREN à 9 chiffres du producteur ;
- `voies-locales` est le nom du fichier, en minuscules non accentuées, avec des tirets.

Exemple : `20261011_213500953_voies-locales.csv`. Les fichiers d'exemple du dépôt (`exemple-valide.csv`, `exemple-invalide.csv`) ne suivent pas cette règle : leur nom est celui attendu par les outils de validation.

### Nommage des champs

Les noms des champs reprennent ceux du modèle initial (`proposition_modele_voies_locales.xlsx`) : minuscules, snake_case, sans accent, avec un tiret bas à la place des points (`point_ini.designation` devient `point_ini_designation`, `point_ini.coordonnees` devient `point_ini_coordonnees`).

Ce choix, retenu pour la version 0.1.0 et à soumettre au GT Voirie communale, **s'écarte volontairement du guide qualité de schema.data.gouv.fr**, qui recommande des noms en camelCase précédés d'un préfixe commun au standard (par exemple `voieLocNumero`), au singulier. Il se rapproche des exemples du modèle de standard du CNIG (`classe_1_id`, `ban_id`), qui n'impose toutefois aucune règle de nommage des attributs. Conséquences :

- les champs n'ont pas de préfixe commun au standard ;
- `servitudes` est au pluriel, comme dans le modèle initial ;
- les noms ne contiennent ni accent ni caractère spécial, hormis le tiret bas, et ne dépassent pas 50 caractères.

## Valider un fichier

```bash
pip install -r requirements.txt
frictionless validate --schema schema.json mon-fichier.csv
```

Un fichier peut aussi être validé en ligne sur [validata.fr](https://validata.fr).
