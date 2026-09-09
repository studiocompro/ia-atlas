# Mettre IA Atlas à jour

Les données importantes sont maintenant centralisées.

## Les 4 fichiers principaux

- `data/ias.json` : noms, descriptions, catégories, compétences, liens officiels, points forts/faibles, alternatives.
- `data/prix.json` : prix, notes tarifaires, date de vérification, état de vérification et source.
- `data/modeles-locaux.json` : familles de modèles, variantes, tailles et estimations de VRAM Q4.
- `data/gpu.json` : cartes NVIDIA, VRAM et architecture.

## Reconstruction locale

Après une modification :

```bash
python scripts/build.py
```

Le script régénère automatiquement :

- `assets/data.js` à partir de `ias.json` + `prix.json` ;
- `assets/local-data.js` à partir de `gpu.json` + `modeles-locaux.json` ;
- les 155 fiches détaillées dans `ia/` ;
- les 9 pages de catégories ;
- les pages des familles de modèles locaux.

Le catalogue, le comparateur et le questionnaire « Quelle IA choisir ? » utilisent tous le même `assets/data.js` généré depuis les JSON.
La page GPU utilise `assets/local-data.js`, lui-même généré depuis les JSON.

## Une fois IA Atlas sur GitHub Pages

Le fichier `.github/workflows/deploy-pages.yml` est déjà préparé.
À chaque envoi sur la branche `main`, GitHub :

1. lit les JSON ;
2. lance `python scripts/build.py` ;
3. reconstruit les pages ;
4. republie le site.

Ainsi, pour changer le prix de ChatGPT, il suffit de modifier l'entrée `chatgpt` dans `data/prix.json`. Il n'est plus nécessaire d'éditer la fiche ChatGPT, le catalogue et le comparateur séparément.

## Important

Les fichiers dans `ia/`, `categorie/` et `modeles/` sont des pages générées. Pour les données, modifiez les JSON puis relancez le build au lieu d'éditer ces pages à la main.
