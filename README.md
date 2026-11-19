# Audit du référentiel TVA — Meridian Distribution

Ce projet analyse un référentiel de 10 000 lignes pour distinguer les numéros de TVA valides, invalides et non tranchés. Il suit le brief fourni dans `BRIEF_TVA.md`.

L'exploration, le nettoyage, la collecte de 200 numéros et la réconciliation sont réalisés. Les deux notebooks, le rapport, les trois graphiques, la note financière et le journal de bord sont disponibles. Les vérifications finales de remise sont précisées en fin de document.

**Auteur : Amaury Ducoulombier.**

## Technologies et ressources

- Python : préparation des données et collecte.
- pandas et openpyxl : lecture, comparaison et analyse des fichiers CSV et Excel.
- requests : appels HTTP à VIES.
- logging : journal de collecte.
- Jupyter : exploration et analyse expliquées dans les notebooks.
- matplotlib : production des trois graphiques SVG de restitution.
- Git : suivi des modifications.

Les fonctions `normaliser()` et `valider()` sont importées depuis `starter-kit/validation_structure.py`. Leurs algorithmes ne sont pas réécrits. Le README du starter-kit décrit les colonnes, les fonctions et l'adresse de VIES. Le traitement des absences, les doublons, les propositions de reconstruction et le script de collecte sont des traitements complémentaires.

Une structure conforme ne garantit pas qu'un numéro est attribué ou valide dans VIES.

## Installation sous Windows

Depuis la racine du dépôt, dans PowerShell, avec Python 3 installé :

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install pandas openpyxl requests matplotlib jupyter
.\.venv\Scripts\python.exe -m jupyter lab
```

Dans Jupyter, choisir le noyau de cet environnement. Les versions des dépendances ne sont pas encore figées dans un fichier dédié.

## Reproduire les analyses sans appel VIES

1. Ouvrir `Notebook/Exploration.ipynb` et exécuter les cellules dans l'ordre pour examiner les données brutes et comparer CSV et Excel.
2. Ouvrir `Notebook/Nettoyage.ipynb`. Exécuter depuis le dossier `Notebook` : plusieurs chemins relatifs supposent ce dossier de travail.
3. Conserver `relancer_essais = False` dans `Nettoyage.ipynb` et exécuter les cellules dans l'ordre. Les fichiers de réponses archivées du dépôt doivent rester présents.
4. Le notebook régénère `resultats/candidats_vies.csv`, le rapport de réconciliation, sa synthèse et les trois graphiques.

Le notebook est configuré avec `relancer_essais = False` : il relit les réponses de `resultats/essais_manuels_vies.json` et les vingt mesures archivées, sans nouvel appel VIES. Il régénère la réconciliation et les graphiques depuis les résultats sauvegardés. Activer volontairement ce paramètre relance les essais réseau ; le script `collecte_vies.py` reste le point de lancement de la collecte. Une exécution complète depuis un noyau neuf a été vérifiée avec `requests.get` bloqué.

Le CSV est la source de référence choisie après comparaison avec Excel. Les valeurs brutes et les identifiants sont conservés dans le tableau de nettoyage.

Les deux notebooks ont été exécutés sans erreur dans un noyau neuf. Pour le notebook d'analyse, les appels `requests.get` étaient bloqués pendant la vérification. Ce contrôle local ne remplace pas le test depuis un clone neuf.

Pour une nouvelle collecte, préparer d'abord les candidats jusqu'à la cellule d'export, lancer le script ci-dessous, puis réexécuter les analyses à partir des réponses sauvegardées. Ne pas activer les essais réseau pour simplement consulter ou régénérer les rapports.

## Choix de nettoyage

- Six formes d'absence sont traitées explicitement ; `NU.LL` est considéré comme une absence probable.
- Deux lignes ont un doublon de numéro si leur numéro normalisé non vide est identique.
- Le motif `cle_invalide` couvre un rejet du format ou de la clé selon les contrôles du module.
- Le motif `pays_non_couvert` n'est pas une preuve d'invalidité.
- Pour 500 numéros sans préfixe apparent, l'ajout du pays déclaré est une hypothèse de correction. Les propositions passent le contrôle structurel ; cela ne prouve pas que le pays ajouté est correct. Les valeurs d'origine restent conservées dans le notebook.

L'export contient 6 302 candidats uniques, dont ces 500 propositions. Sans elles, 5 802 numéros sont initialement conformes. Le gain de 3 698 appels par rapport aux 10 000 lignes repose sur l'inclusion des propositions et le traitement documenté des autres familles.

## Lancer la collecte

Depuis la racine du projet :

```powershell
.\.venv\Scripts\python.exe collecte_vies.py --taille 200
```

Pour un premier essai sur trois numéros :

```powershell
.\.venv\Scripts\python.exe collecte_vies.py --taille 3
```

Sans `--taille`, la taille est de 200. Elle doit être comprise entre 1 et le nombre de candidats. Le script attend une seconde avant chaque nouvel appel et utilise un délai d'attente réseau de 30 secondes.

La sélection est aléatoire, sans remise, avec `random_state=42`. Elle est reproductible si le fichier d'entrée, son ordre et l'environnement restent identiques. Elle porte sur les candidats uniques, pas sur les 10 000 lignes brutes. La comparaison des pays et des reconstructions est présentée dans le notebook ; elle ne suffit pas à démontrer une représentativité globale.

## Résultats et journal

| Fichier | Contenu |
|---|---|
| `resultats/candidats_vies.csv` | Liste unique des candidats exportés par le notebook |
| `resultats/essais_manuels_vies.json` | Réponses archivées des essais manuels de phase 3 |
| `resultats/mesures_vies.json` | Vingt essais de phase 2, avec les durées et réponses |
| `resultats/collecte_vies.json` | Résultats datés de la collecte du script |
| `collecte_vies.log` | Journal du script, à la racine du projet |

## Livrables de l'étude

| Livrable | Fichier |
|---|---|
| Consignes du projet | [BRIEF_TVA.md](BRIEF_TVA.md) |
| Exploration des données brutes | [Exploration.ipynb](Notebook/Exploration.ipynb) |
| Nettoyage, essais et analyse | [Nettoyage.ipynb](Notebook/Nettoyage.ipynb) |
| Script de collecte | [collecte_vies.py](collecte_vies.py) |
| Rapport des 10 000 lignes | [rapport_reconciliation.csv](resultats/rapport_reconciliation.csv) |
| Statuts croisés avec les motifs | [synthese_reconciliation.csv](resultats/synthese_reconciliation.csv) |
| Trois graphiques SVG | [Graphiques](resultats/graphiques/) |
| Note signée à la direction financière | [note_direction_financiere.md](resultats/note_direction_financiere.md) |
| Blocages, tentatives et résolutions | [JOURNAL_DE_BORD.md](JOURNAL_DE_BORD.md) |
| Documentation du kit fourni | [README du starter-kit](starter-kit/README.md) |

Le rapport porte sur **10 000 lignes, répétitions incluses** : 6 valides selon VIES, 2 755 invalides en l'état et 7 239 non tranchées. Il conserve les motifs, dates disponibles, hypothèses de reconstruction et 438 répétitions supplémentaires. Ces comptes ne représentent pas des clients distincts. Les 200 numéros interrogés sont associés à 208 lignes du référentiel.

## Lire les résultats de collecte

Le script conserve le numéro, le pays, la date UTC de début d'appel, le code HTTP, la durée, la réponse complète, l'erreur éventuelle et le statut. La réponse complète conserve aussi la date renvoyée par VIES.

Le journal utilise `logging` pour les démarrages, les appels et leurs durées, les erreurs, les sauvegardes, les numéros sautés et les fins normales. Le fichier `Notebook/collecte_vies.log`, s'il est présent, n'est pas le journal utilisé par le script actuel.

Le classement est prudent :

- `valide` : HTTP 200, `isValid=true` et `userError=VALID` ;
- `invalide` : HTTP 200, `isValid=false` et `userError=INVALID` ;
- `non_tranche` : erreur réseau, HTTP, réponse inexploitable, limitation du service ou combinaison inattendue.

Un HTTP 200 ne prouve pas la validité du numéro. En particulier, `MS_MAX_CONCURRENT_REQ` reste non tranché. Un numéro valide ne prouve pas non plus qu'il appartient au client du référentiel : l'identité retournée doit être examinée séparément.

## Interrompre et reprendre

1. Interrompre le terminal avec **Ctrl + C** pendant la collecte.
2. Relancer exactement la même commande, avec le même fichier de candidats.
3. Vérifier dans le journal que les numéros enregistrés sont sautés et que les autres sont traités.

Chaque tentative est sauvegardée dans un fichier temporaire, puis remplace le fichier de résultats. La relance charge ce fichier et évite de refaire les tentatives enregistrées, y compris les non tranchées. Ne pas lancer plusieurs instances simultanément sur le même fichier de résultats.

Un appel interrompu avant sauvegarde peut être retenté. L'interruption n'est pas explicitement journalisée ; le message de fin n'apparaît qu'en cas de fin normale. Les essais d'interruption/reprise ont conservé les résultats sauvegardés sans doublon.

## Limites et revérification

Un verdict décrit une situation à la date de consultation, sans garantie permanente. Pour ce projet, une nouvelle vérification avant une nouvelle facturation intracommunautaire est proposée : c'est une règle métier proposée, pas une durée réglementaire fournie par le brief.

Le script assure la reprise d'une campagne ; il n'automatise ni le renouvellement des verdicts ni une nouvelle campagne ciblant les non tranchés. Leur réexamen doit être organisé séparément en conservant l'historique. Ne pas supprimer les résultats existants pour simuler une reprise.

La campagne enregistrée comporte 200 résultats uniques : 5 valides, 145 invalides et 50 non tranchés. Ces comptes concernent cette sélection et ses dates d'appel, sans extrapolation directe aux 10 000 lignes. Une relance avec la même sélection conserve ces résultats ; elle n'actualise pas les verdicts.

## Vérifications finales de remise

- Vérifier la tenue de la note sur une page avec ses trois graphiques agrandis.
- Figer les versions des dépendances pour faciliter la reproduction de l'environnement et du tirage.
- Vérifier le lancement depuis un clone neuf dans un dossier séparé, en suivant ce README et en conservant le dossier de travail actuel.
- Vérifier la présence des livrables dans le dépôt GitHub public, l'historique réel des commits et préparer la démonstration demandée par le brief.

L'auteur et le journal de bord sont renseignés. Les tests de reprise et d'exécution depuis un noyau neuf sont réalisés ; la publication et le test depuis un clone neuf ne sont pas attestés par ces seuls contrôles.
