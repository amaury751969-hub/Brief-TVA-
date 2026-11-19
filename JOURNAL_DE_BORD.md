# Journal de bord — Audit du référentiel TVA

**Auteur : Amaury Ducoulombier**  
**Période de travail documentée : du 16 au 18 novembre 2026**

Ce journal est reconstitué à partir des échanges de travail, des notebooks, des résultats sauvegardés et du journal de collecte. Les étapes sont regroupées par période ; aucune durée de travail non mesurée n’est inventée. Le brief prévoit deux jours : le travail documenté s’étend sur trois dates calendaires. La répartition effective des heures n’a pas été enregistrée.

Le brief demande de noter les blocages, les tentatives et leurs résolutions, et de demander un indice après deux heures sur un même point. Aucun blocage de plus de deux heures n’a été chronométré : le respect de ce seuil ne peut pas être attesté rétrospectivement.

## 1. Prise en main et exploration — à partir du 16 novembre

**Objectif.** Comprendre le référentiel avant de le corriger et répondre aux six questions de la phase 1.

**Ressources utilisées.** `BRIEF_TVA.md`, `starter-kit/README.md`, les données CSV et Excel et la lecture de `starter-kit/validation_structure.py`. La règle de `normaliser()` sert à décrire les caractères à retirer, sans modifier les données brutes.

**Travail réalisé.** Chargement des valeurs comme du texte, observation des codes pays, exemples FR, longueurs et formes, comptage des absences, comparaison pays/préfixe, comparaison CSV/Excel et analyse par canal et période.

**Constats et décisions.**

- Le référentiel contient 10 000 lignes et 15 codes déclarés. Les 974 lignes FR présentent 50 formes observées, marqueurs d’absence inclus ; ce ne sont pas 50 formats valides.
- 1 861 lignes comportent des caractères que la normalisation supprimerait, soit 18,61 %.
- Six formes d’absence représentent 261 lignes, soit 2,61 %. `NU.LL` est retenu comme une absence probable.
- Les 9 207 préfixes comparables correspondent au pays déclaré. Pour 532 lignes sans préfixe repérable et 261 absences, la comparaison n’est pas possible.
- CSV et Excel produisent des tableaux identiques avec les options utilisées. Le CSV est retenu comme source de référence pour sa simplicité d’utilisation.
- Les dates observées vont du 1er janvier 2024 au 1er octobre 2025, contrairement aux huit années d’accumulation évoquées dans le contexte. Cette différence est signalée sans explication supposée. Octobre 2025 ne compte que 16 lignes sur une journée.

**Blocage : variables absentes après redémarrage du noyau.** Des cellules utilisaient `pd` ou `df` sans que les imports et le chargement aient été exécutés dans la session. Les sorties anciennes restaient visibles, ce qui pouvait masquer le problème. Les cellules nécessaires ont été remises dans l’ordre et le chargement explicite du CSV a été ajouté. La vérification finale depuis un noyau neuf a confirmé le fonctionnement.

**Point d’attention : absence dans pandas et absence métier.** `isna()` renvoyait zéro alors que des chaînes vides et marqueurs textuels étaient présents. Les formes brutes ont été comptées avec `repr` et des masques explicites, sans les confondre avec les seules valeurs manquantes pandas.

## 2. Intégration du module et nettoyage — 17 novembre

**Objectif.** Réutiliser les fonctions fournies, définir les doublons et chiffrer les candidats à une vérification VIES.

**Ressources utilisées.** Les imports et exemples du README ; les fonctions `normaliser()` et `valider()` de `validation_structure.py`. Le traitement pandas des absences, doublons et reconstructions est complémentaire : aucun algorithme national n’a été réécrit.

**Difficulté de mise en place.** Le fichier de travail était initialement sans extension et un nom comportait une extension supplémentaire. Le notebook retenu est `Notebook/Nettoyage.ipynb`. Le fichier avec l’extension superflue a été supprimé à la demande de l’auteur.

**Traitements et résultats.** Les valeurs brutes sont conservées dans une copie de travail. Les six marqueurs d’absence sont traités avant `normaliser()` : la fonction ne reconnaît pas automatiquement `null` ou `N/A` comme des absences. La définition retenue d’un doublon est un même numéro normalisé non vide. Les répétitions supplémentaires sont comptées après la première occurrence.

| Étape | Nombre |
|---|---:|
| Lignes initiales | 10 000 |
| Lignes avec numéro non vide | 9 739 |
| Répétitions supplémentaires | 438 |
| Numéros uniques non vides | 9 301 |
| Structures initialement conformes | 5 802 |
| Rejets de format ou de clé | 2 499 |
| Numéros classés `pays_non_couvert` | 1 000 |

**Difficulté d’interprétation : `pays_non_couvert`.** La lecture du module montre qu’il utilise systématiquement les deux premiers caractères comme code pays. L’examen des 1 000 cas distingue 500 préfixes non couverts et 500 numéros commençant par un chiffre. Ils ne sont pas tous déclarés invalides sur ce seul motif.

**Décision à justifier : reconstruction de 500 préfixes.** L’ajout du pays déclaré produit 500 propositions conformes aux contrôles locaux. Aucun doublon supplémentaire n’est détecté entre ces propositions ni avec les 5 802 numéros initialement conformes. Elles restent identifiées comme des hypothèses, et non comme des corrections prouvées. Leur inclusion porte les candidats à 6 302 et évite 3 698 appels par rapport à un appel par ligne.

## 3. Premières mesures VIES — 17 novembre

**Objectif.** Observer les réponses et mesurer les durées sur deux numéros initialement conformes de chacun des dix pays couverts.

**Tentative initiale.** Deux appels ont été réalisés séparément, avec lecture de leur réponse entière. Une boucle a ensuite été retenue pour les vingt essais, avec temporisation et liste de résultats.

**Blocage anticipé : perte des résultats à la fermeture.** Une liste en mémoire ne survit pas au redémarrage du noyau. Les mesures ont donc été sauvegardées après chaque tentative dans `resultats/mesures_vies.json`, puis rechargées à la relance. Les deux premières réponses ont été préservées à partir des sorties ; leurs durées récupérées étaient arrondies à deux décimales et sont identifiées comme telles.

**Résultats.** Vingt mesures sont conservées : durée moyenne de 1,79 s, médiane de 0,41 s, écart-type de 3,31 s, minimum de 0,13 s et maximum de 11,19 s. Avec une seconde de pause, l’estimation pour les 6 302 candidats est de 4,88 heures, soit un gain estimé de 2,86 heures. Ces calculs ne lancent pas 10 000 appels et ne prévoient pas les nouvelles tentatives après erreur.

**Apprentissage central.** Les vingt réponses comprennent 17 `INVALID` et 3 `MS_MAX_CONCURRENT_REQ`. Un HTTP 200 et `isValid=false` ne suffisent pas à déclarer un numéro invalide. Les trois erreurs du service restent non tranchées. Les durées mesurées incluent ces réponses techniques ; deux observations par pays donnent un ordre de grandeur, pas une performance garantie.

## 4. Essais manuels et script de collecte — 18 novembre

**Objectif.** Expliquer les champs de réponse et construire une collecte paramétrable, datée, journalisée et reprenable.

**Essais et correction d’une erreur de construction.**

| Essai | Observation | Suite retenue |
|---|---|---|
| Référence du README `FR27552032534` | Structure conforme ; réponse `MS_MAX_CONCURRENT_REQ` | Conserver le cas non tranché sans forcer un verdict |
| Clé fausse `FR99552032534` | Rejet local et réponse `INVALID` | Expliquer la différence entre code HTTP et verdict |
| Premier numéro construit `FR40345678901` | La clé annoncée conforme était incorrecte ; le module le rejette | Recalculer avec la formule FR fournie : clé 15 |
| Numéro corrigé `FR15345678901` | Structure conforme ; limitation du service | Conserver la réponse comme non tranchée |
| Cas positif `DK50549151` observé pendant la collecte | `isValid=true`, `userError=VALID`, identité retournée | Documenter le cas positif depuis la réponse sauvegardée |

Le cas positif n’a donc pas été obtenu au premier essai manuel avant la boucle. Cette limite du déroulement est explicitement conservée. Une validité de numéro ne prouve pas son rattachement au client du référentiel.

**Ressource indisponible.** Le cours local `06-logging-structure.ipynb` était vide sur disque lors de sa lecture. Aucun exemple de ce fichier n’a pu être repris. Le script utilise néanmoins le module `logging`, conformément à l’exigence du brief ; aucune consultation non réalisée du cours n’est revendiquée.

**Construction progressive de `collecte_vies.py`.** Export des candidats, chargement, paramètre `--taille` (200 par défaut), tirage sans remise avec `random_state=42`, pause d’une seconde, délai réseau de 30 secondes, dictionnaire de résultat daté, lecture conjointe de `isValid` et `userError`, sauvegarde temporaire puis remplacement du fichier JSON. Le journal conserve les appels, leurs codes HTTP et durées, les erreurs, les sauvegardes et les numéros sautés.

**Corrections de code.** Des messages d’erreur d’exemple auraient été écrits à chaque lancement sans erreur réelle : ils ont été retirés. L’import `json` manquait initialement ; il a été ajouté. L’indentation d’une condition HTTP et du message de fin a été corrigée pour éviter une erreur Python et une fin annoncée après chaque numéro.

**Tests de reprise.**

- Premier test de trois numéros : réponses sauvegardées ; relance avec trois appels sautés.
- Les campagnes de vingt puis trente numéros se sont terminées normalement : elles ne prouvaient pas une interruption.
- Une campagne de quarante a ensuite été arrêtée avant la sauvegarde d’un nouvel appel. La relance a chargé et sauté les trente résultats existants, puis terminé les dix restants sans doublon.
- Limite : un appel interrompu avant sa sauvegarde peut être retenté. L’interruption n’est pas explicitement journalisée par un message dédié.

**Campagne de 200.** La vérification intermédiaire a trouvé 162 résultats : aucune fin de campagne n’était alors attestée. La vérification suivante a confirmé la fin normale et **200 numéros uniques : 5 valides, 145 invalides et 50 non tranchés**. Ces derniers sont conservés et sautés à la reprise normale ; leur réexamen doit être organisé séparément avec conservation de l’historique.

**Tirage et limites.** Les dix pays sont présents, avec un écart maximal de répartition d’environ 2,2 points par rapport aux candidats. Onze numéros reconstruits figurent dans la sélection, soit 5,5 %, contre 7,93 % parmi les candidats. Ces comparaisons ne démontrent pas une représentativité globale et ne permettent pas une extrapolation directe aux 10 000 lignes.

## 5. Réconciliation et analyse — 18 novembre

**Objectif.** Rattacher les réponses aux lignes d’origine et produire les trois catégories attendues, leurs motifs et les doublons.

**Méthode.** Conservation des 10 000 lignes, création d’un numéro de rapprochement et d’un indicateur de préfixe ajouté, puis jointure contrôlée avec les résultats uniques. Les 200 réponses se rattachent à 208 lignes. Les rejets structurels sont intégrés séparément des verdicts VIES. Les numéros non interrogés restent non tranchés même si leur structure est conforme.

| Classement des lignes | Nombre | Détail |
|---|---:|---|
| Valide selon VIES | 6 | Répétitions incluses ; hypothèse de reconstruction conservée le cas échéant |
| Invalide en l’état | 2 755 | 2 605 rejets structurels et 150 verdicts négatifs VIES |
| Non tranché | 7 239 | 6 407 non interrogées, 519 non couvertes, 261 absences et 52 sans verdict VIES |
| Total | 10 000 | 438 répétitions supplémentaires identifiées, sans suppression de ligne |

**Interprétation.** Les écarts de parts classées invalides atteignent 3,48 points entre canaux, 4,95 points entre pays couverts et 0,85 point entre années. Ils restent descriptifs et ne prouvent ni une cause ni la responsabilité d’un groupe. Les codes non couverts à 0 % d’invalidité ne sont pas assimilés à des groupes sans erreur.

**Incertitude.** Les 50 numéros sans verdict laissent un encadrement de 2,5 % à 27,5 % de valides dans les 200 essais, selon leur statut inconnu. Ce n’est pas un intervalle de confiance. Le repère théorique de ±6,9 points à 95 % pour 200 verdicts tous connus ne corrige pas les réponses manquantes ; il n’est pas utilisé comme intervalle du taux réel global.

**Décisions proposées.** Vérifier en priorité les dossiers des prochaines factures, demander les données manquantes ou corrections, confirmer les reconstructions et prévoir un réexamen des erreurs techniques. La fréquence de revérification, les responsables opérationnels, le calendrier et le traitement fiscal relèvent de la direction financière.

## 6. Restitution et vérifications finales — 18 novembre

**Livrables préparés.** Deux notebooks harmonisés ; rapport détaillé et synthèse CSV ; script, résultats JSON et journal ; trois graphiques SVG ; README du projet ; note signée à la direction financière ; présent journal de bord.

**Difficultés de présentation.** Les sauvegardes des figures étaient placées avant leur création, avec un nom incorrect pour la deuxième. Elles ont été déplacées après la construction de chaque graphique et avant `plt.show()`. Les trois exports SVG ont été vérifiés. La note a ensuite été réorganisée avec un graphique par bloc et l’explication à côté. Les agrandissements successifs peuvent être limités par la largeur de l’aperçu Markdown ; la tenue sur une page n’est pas encore attestée.

**Révision éditoriale.** Retrait des formulations de conversation et commentaires périmés, correction de l’affirmation sur la clé du numéro construit, harmonisation des titres par phase et clarification des sources. La note distingue les constats du data analyst, ses propositions et les arbitrages réservés à la direction financière. Son auteur est Amaury Ducoulombier.

**Vérification de reproductibilité.** Les essais manuels ont été archivés dans `resultats/essais_manuels_vies.json`. Le notebook d’analyse utilise `relancer_essais=False` par défaut. Il a été exécuté intégralement depuis un noyau neuf, avec `requests.get` bloqué, sans erreur ; rapports et figures ont été régénérés sans nouvel appel VIES. Le notebook d’exploration a également été exécuté intégralement depuis un noyau neuf. Son contrôle final confirme 261 absences sous six formes et aucune date absente ou non interprétable. Les données sources sont restées intactes.
