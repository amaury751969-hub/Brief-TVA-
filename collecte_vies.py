"""Collecte VIES — script à compléter selon le brief TVA."""

import argparse
import json
import logging
from pathlib import Path
import time
import requests
import pandas as pd
from datetime import datetime, timezone

# Placer le journal à côté du script, quel que soit le dossier de lancement.
dossier_projet = Path(__file__).resolve().parent

# Le brief demande un journal avec logging plutôt que des print().
logging.basicConfig(
    filename=dossier_projet / "collecte_vies.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logging.info("Démarrage du script")

# Charger les candidats exportés depuis le notebook
fichier_candidats = dossier_projet / "resultats" / "candidats_vies.csv"

candidats = pd.read_csv(
    fichier_candidats,
    dtype=str,
    keep_default_na=False
)

logging.info("Nombre de candidats chargés : %s", len(candidats))

# Choisir le nombre de numéros depuis la commande de lancement
parametres = argparse.ArgumentParser()
parametres.add_argument("--taille", type=int, default=200)
options = parametres.parse_args()

if options.taille < 1 or options.taille > len(candidats):
    parametres.error("La taille doit être comprise entre 1 et le nombre de candidats.")

# Tirage aléatoire reproductible
echantillon = candidats.sample(
    n=options.taille,
    random_state=42
)

logging.info("Taille de l'échantillon : %s", len(echantillon))

fichier_resultats = dossier_projet / "resultats" / "collecte_vies.json"

# Restaurer les résultats précédents
if fichier_resultats.exists():
    with open(fichier_resultats, encoding="utf-8") as fichier:
        resultats = json.load(fichier)
else:
    resultats = []

# Retrouver les numéros déjà enregistrés
numeros_deja_traites = []

for resultat in resultats:
    numeros_deja_traites.append(resultat["numero"])

logging.info("Résultats déjà enregistrés : %s", len(resultats))

for numero in echantillon["numero_tva"]:

    if numero in numeros_deja_traites:
        logging.info("Appel sauté, numéro déjà enregistré : %s", numero)
        continue

    logging.info("Numéro à vérifier : %s", numero)

    # Attendre entre les appels
    time.sleep(1)

    # Séparer le pays du numéro
    pays = numero[:2]
    numero_sans_pays = numero[2:]

    # Adresse fournie dans le README
    url = (
        "https://ec.europa.eu/taxation_customs/vies/rest-api/"
        f"ms/{pays}/vat/{numero_sans_pays}"
    )


    # Préparer les informations à conserver pour cet appel
    resultat = {
        "numero": numero,
        "pays": pays,
        "date_appel": datetime.now(timezone.utc).isoformat(),
        "code_http": None,
        "duree_secondes": None,
        "reponse_complete": None,
        "erreur": None,
        "statut": "non_tranche"
    }

    debut = time.perf_counter()

    try:
        reponse = requests.get(url, timeout=30)
        duree = time.perf_counter() - debut
        resultat["code_http"] = reponse.status_code
        resultat["duree_secondes"] = duree
        resultat["reponse_complete"] = reponse.text

        logging.info(
            "Appel %s — HTTP %s — durée %.2f secondes",
            numero,
            reponse.status_code,
            duree
        )
        if reponse.status_code == 200:
            try:
                donnees = json.loads(reponse.text)

                validite = donnees.get("isValid")
                erreur_service = donnees.get("userError")

                if validite is True and erreur_service == "VALID":
                    resultat["statut"] = "valide"

                elif validite is False and erreur_service == "INVALID":
                    resultat["statut"] = "invalide"

                else:
                    resultat["erreur"] = str(erreur_service)
                    logging.warning(
                        "Numéro non tranché : %s — réponse du service : %s",
                        numero,
                        erreur_service
                    )

            except (ValueError, AttributeError):
                resultat["erreur"] = "Réponse JSON non exploitable"
                logging.error("Réponse JSON non exploitable pour %s", numero)

        else:
            resultat["erreur"] = f"Erreur HTTP {reponse.status_code}"
            logging.warning(
                "Erreur HTTP %s pour %s",
                reponse.status_code,
                numero
            )

    except requests.RequestException as erreur:
        duree = time.perf_counter() - debut

        logging.error(
            "Erreur réseau pour %s — durée %.2f secondes — %s",
            numero,
            duree,
            erreur
        )
        resultat["duree_secondes"] = duree
        resultat["erreur"] = str(erreur)

    # Ajouter le résultat de cette tentative
    resultats.append(resultat)

    # Écrire dans un fichier temporaire avant de remplacer la sauvegarde
    fichier_temporaire = fichier_resultats.with_suffix(".tmp")

    with open(fichier_temporaire, "w", encoding="utf-8") as fichier:
        json.dump(resultats, fichier, ensure_ascii=False, indent=2)

    fichier_temporaire.replace(fichier_resultats)

    numeros_deja_traites.append(numero)

    logging.info(
        "Résultat sauvegardé : %s — statut %s",
        numero,
        resultat["statut"]
    )

logging.info("Fin de la campagne — taille de l'échantillon : %s", len(echantillon))
