---
name: meta-ads-agent
description: Autonomous weekly Meta Ads agent for Bienprêter #2. Fetches last 14 days of campaign data via Windsor.ai, runs a full PACTO analysis (Paramètres, Audiences, Créatives, Tunnel, Offre), generates a formatted Excel PACTO report, then presents numbered recommendations for human approval before applying changes. Invoke every Monday at 9am via scheduled task, or manually with /meta-ads-agent.
metadata:
  platform: Meta
  account_id: "683334547372319"
  account_name: "Bienprêter #2 - Compte Publicitaire"
  connector: facebook
  windsor_mcp: mcp__6d014ba9-b778-4e58-9cfe-b24735571e43
---

# Meta Ads Agent — Analyse Hebdomadaire PACTO

Agent autonome hebdomadaire pour le compte Meta Ads **Bienprêter #2**. Se lance chaque lundi à 9h. Récupère les données Windsor.ai, applique le framework PACTO, génère un rapport Excel, et attend l'approbation humaine avant toute modification.

---

## Phase 1 — Récupération des données (Windsor.ai)

**RÈGLE OBLIGATOIRE** : Appeler `get_fields` avant `get_data` (exigence Windsor.ai).

### Étape 1.1 — Niveau Campagne (14 jours pour comparaison WoW)

```
connector: facebook
accounts: ["683334547372319"]
date_preset: "last_14d"
fields: [
  "date", "campaign_id", "campaign_name", "campaign_status", "objective",
  "spend", "impressions", "reach", "frequency", "clicks", "ctr",
  "cpm", "cpc", "actions_purchase", "actions_lead",
  "cost_per_action_type_purchase", "cost_per_action_type_lead"
]
```

### Étape 1.2 — Niveau Ad Set (7 jours)

```
connector: facebook
accounts: ["683334547372319"]
date_preset: "last_7d"
fields: [
  "date", "campaign_name", "adset_id", "adset_name", "adset_status",
  "spend", "impressions", "reach", "frequency", "clicks", "ctr",
  "cpm", "cpc", "actions_purchase", "actions_lead",
  "cost_per_action_type_purchase", "cost_per_action_type_lead"
]
```

### Étape 1.3 — Niveau Annonce (7 jours)

```
connector: facebook
accounts: ["683334547372319"]
date_preset: "last_7d"
fields: [
  "date", "campaign_name", "adset_name", "ad_id", "ad_name", "status",
  "spend", "impressions", "frequency", "clicks", "ctr", "cpm",
  "actions_purchase", "actions_lead",
  "cost_per_action_type_purchase", "cost_per_action_type_lead"
]
```

### Calculs préliminaires
Après la récupération, calculer immédiatement :
- **Période S-1** = jours 1-7 des 14 jours | **Période S** = jours 8-14
- CPA leads moyen compte (S) = total spend S / total actions_lead S
- CPA achats moyen compte (S) = total spend S / total actions_purchase S (si > 0)
- CPM moyen compte, CTR moyen, Fréquence moyenne (weighted by impressions)
- Variation WoW (%) pour : spend, CPM, CTR, CPA leads, impressions, fréquence

---

## Phase 2 — Analyse PACTO

Exécuter les 5 analyses dans l'ordre. Chaque lettre PACTO reçoit un **statut** (VERT / JAUNE / ORANGE / ROUGE) et une liste de **recommandations concrètes**.

### P — Paramètres du compte et de la campagne

Vérifier :
- [ ] Nombre de campagnes actives (> 5 simultanées = signal de fragmentation)
- [ ] Nombre d'ad sets par campagne (> 6 = risque de cannibalisation)
- [ ] Nombre de créatifs actifs par ad set (idéal : 2-4)
- [ ] Objectifs de campagne cohérents avec le funnel (TOF = Trafic/Awareness, MOF = Lead, BOF = Conversion)
- [ ] Attribution correcte : 7-day click, 1-day view
- [ ] Spend S vs S-1 : variation > ±30% → anomalie budget
- [ ] Campagne avec spend = €0 depuis 3+ jours → problème de diffusion
- [ ] Delivery > 110% ou < 80% du budget journalier prévu

**Seuils de statut P :**
| Statut | Condition |
|--------|-----------|
| VERT | Tout OK, pas d'anomalie |
| JAUNE | 1-2 points d'attention mineurs |
| ORANGE | Anomalie budget ou structure confirmée |
| ROUGE | Campagne bloquée / spend €0 / attribution cassée |

**Référentiel d'optimisations P :**
Réduire le nombre de campagnes | Réduire le nombre d'audiences par campagne | Réduire le nombre de créatifs (2) | Tester un nouvel objectif de campagne | Tester un nouvel objectif d'optimisation (achat, ATC, vue) | Passer en Dynamic Creatives | Passer en CBO | Passer en ABO | Utiliser les placements automatiques (Advantage+) | Tester les cost controls (bid cap / cost cap) | Augmenter le budget de 20% | Réduire le budget de 20% | Utiliser le budget « lifetime » | Réduction de la fréquence | Attribution (7day-view 1-day-click) | Stand By – pas assez de data | Refaire la campagne au complet | Lancer une campagne « Test » annexe

---

### A — Audiences du groupe d'annonces

Vérifier :
- [ ] Fréquence moyenne des ad sets actifs (seuil warning : > 3.5, critique : > 5.0)
- [ ] CPM WoW : hausse > 30% sans hausse de spend → saturation audience
- [ ] Ratio reach / taille audience estimée → % audience atteinte (Inspect Meta)
- [ ] Overlap audience estimé entre ad sets (si 2+ ad sets ciblant des segments similaires)
- [ ] Présence d'exclusions sur les audiences chaudes (visiteurs 180j si objectif prospection)
- [ ] Ad sets avec audience < 50 000 personnes → trop restrictif

**Seuils de statut A :**
| Statut | Condition |
|--------|-----------|
| VERT | Fréquence < 2.5, CPM stable, audiences fraîches |
| JAUNE | Fréquence 2.5-3.5 ou CPM +20-30% WoW |
| ORANGE | Fréquence 3.5-5.0 ou CPM +30-40% WoW ou overlap probable |
| ROUGE | Fréquence > 5.0 ou audience exhausted |

**Référentiel d'optimisations A :**
Augmenter le volume de l'audience lookalike (%) | Tester le ciblage broad | Tester le ciblage par intérêt | Audiences glaciales (exclusion visiteurs 180j) | Audiences remarketing 30j (nouvelles interactions seulement) | Créer audience ATC pour recibler fort volume d'ajout au panier | Élargir les audiences de remarketing (mode stack) | Special Ads Category | Exclusion d'audiences (audience overlap) | Cibler uniquement un sexe | Ciblage all (homme et femme) | Élargir les âges (18-65+) | Ciblage géographique le plus large possible | Recibler les Video Views | Optimisation pour ad delivery en « Value » | Language (All) | Advantage+ Audience | Exclure les clients existants

---

### C — Créatives : visuels, textes et CTAs

Vérifier au niveau annonce :
- [ ] CTR WoW : baisse > 20% → signal de fatigue créative
- [ ] CPM WoW : hausse > 30% sur une annonce spécifique
- [ ] Fréquence annonce > 3.5 avec CTR en baisse simultanée
- [ ] Annonces avec spend > €30 et 0 conversions → créatif inefficace
- [ ] Ratio de première impression (Inspect Meta) > 60% → majorité a déjà vu la pub
- [ ] Diversité des formats : vidéo vs image vs carrousel vs DPA

**Seuils de statut C :**
| Statut | Condition |
|--------|-----------|
| VERT | CTR stable/croissant, fréquence < 2.5 par annonce |
| JAUNE | CTR -10% à -20% WoW ou fréquence 2.5-3.5 |
| ORANGE | CTR -20%+ WoW ou fréquence > 3.5 sur annonces principales |
| ROUGE | CTR effondré, annonces sans distribution, 0 conversions après €50+ |

**Référentiel d'optimisations C :**
UGC pour présenter le produit/service | Tester le format Instant Expérience | Changer les 5 premières secondes d'une vidéo | Tester le format catalogue carrousel DPA | Créatif product-oriented VS lifestyle | Tester différents CTAs | 5 leviers de hooks (Have, Feel, Average Day, Status, Proofs) | Reviews / stars rating dans les copy et visuels | Changer les couleurs d'une publicité gagnante | Rédaction bullet point avec emoji | Tester 3 nouveaux hooks/angles | Décliner le/les visuel(s) gagnant(s) | Réaliser un A/B test créatif | Tester le format « illustration » | Mettre de l'avant de vraies personnes/visages | Vidéo du produit en action/utilisation | Tester des éléments « familiers »

---

### T — Tunnel de vente

Vérifier :
- [ ] CTR élevé (> 1%) mais CPA élevé → problème tunnel (landing page ≠ ad)
- [ ] Ratio Add-to-Cart / Achat (si disponible dans les events) → taux de passage à la caisse
- [ ] Volume de Landing Page Views vs Clicks → taux de chargement page (< 70% = page lente)
- [ ] Cohérence entre promesse de la pub et contenu de la landing page
- [ ] Type de funnel utilisé (direct LP, lead form, Messenger, webinaire...)

**Seuils de statut T :**
| Statut | Condition |
|--------|-----------|
| VERT | CTR ≥ 1%, CPA atteint, cohérence pub/LP OK |
| JAUNE | CTR bon mais CPA > cible de 20% → optimiser LP |
| ORANGE | CTR bon mais très peu de conversions → tunnel cassé |
| ROUGE | Taux de conversion LP < 1% ou tunnel non fonctionnel |

**Référentiel d'optimisations T :**
Redirection vers la page produit | Créer une landing page optimisée | Lead Ad | Lead magnet | Campagne Messenger | Funnel Quiz | Challenge | Campagne Video Views | Funnel Webinaire | Liste VIP / Concours | Funnel tripwire + upsell | Campagne Flash sale | DABA | Améliorer cohérence pub ↔ landing page | Améliorer l'expérience client du tunnel de vente | Chat/bot de qualification

---

### O — Offre

Analyser (basé sur les données disponibles et contexte) :
- [ ] Valeur de conversion moyenne (si actions_purchase > 0) → panier moyen
- [ ] ROAS calculé (si e-commerce) : si < 2.0 → problème d'offre ou de marge
- [ ] Type d'offre actuelle (lead, achat direct, essai, devis...)
- [ ] Opportunité d'améliorer la proposition de valeur pour réduire le CPA

**Seuils de statut O :**
| Statut | Condition |
|--------|-----------|
| VERT | Offre en ligne avec les objectifs, ROAS/CPA satisfaisants |
| JAUNE | CPA légèrement au-dessus de la cible malgré bonnes créas et audiences |
| ORANGE | CPA bien au-dessus de la cible → offre potentiellement inadaptée |
| ROUGE | ROAS < 1 ou offre non compétitive vs concurrents |

**Référentiel d'optimisations O :**
Offre plus agressive | BOGO (Buy 1 Get 1) | Buy 1 + Free gift | Livraison gratuite | Essai gratuit / démo | Gated Shopping Event | Scarcity / FOMO | Changer % en € ou vice versa sur les rabais | Bundles pour augmenter la valeur de conversion | Rabais de volume | Upsells / cross-sells | Améliorer la promesse de valeur principale

---

## Phase 3 — Troubleshooting & Enjeux

Pour chaque problème identifié dans les 5 analyses PACTO, documenter dans la table Enjeux :

| Champ | Contenu |
|-------|---------|
| metrique | Nom de la métrique concernée |
| resultat | Valeur actuelle constatée |
| kpi_cible | Seuil visé |
| enjeu | Description concise du problème |
| raisonnement | Pourquoi c'est un problème et quelle en est la cause probable |
| optimisation | Référence PACTO + actions concrètes |

---

## Phase 4 — Génération du rapport Excel

Après l'analyse complète, construire le fichier JSON `data/report_data.json` avec exactement cette structure :

```json
{
  "client_name": "Bienprêter #2",
  "report_date": "[DATE_AUJOURD_HUI_JJ/MM/AAAA]",
  "period_start": "[DATE_DEBUT]",
  "period_end": "[DATE_FIN]",
  "account_status": "[VERT|JAUNE|ORANGE|ROUGE basé sur worst PACTO status]",

  "kpis_cibles": {
    "cpa_leads": [seuil cible],
    "cpa_achats": [seuil cible ou null],
    "budget_journalier": [budget quotidien actuel],
    "frequence_max": 3.0
  },

  "kpis_actuels": {
    "cpa_leads": [valeur semaine],
    "cpa_achats": [valeur semaine ou null],
    "budget_journalier": [spend moyen/jour cette semaine],
    "frequence_moyenne": [valeur pondérée]
  },

  "rapport_semaine": [{
    "periode_debut": "[DATE]",
    "periode_fin": "[DATE]",
    "analyse": "[Synthèse narrative de la semaine en 3-5 phrases]",
    "campagnes_a_optimiser": ["[Campagne 1]", "[Campagne 2]"],
    "niveau_optimisation": "[Lettre PACTO du problème principal : P/A/C/T/O]",
    "explications": "[Détail de l'optimisation recommandée cette semaine]"
  }],

  "optimisations_90j": [
    {
      "optimisation": "[Description de l'optimisation]",
      "metrique": "[Métrique suivie]",
      "resultat_depart": "[Valeur au début]",
      "resultat_actuel": "[Valeur actuelle]",
      "resultat_vise": "[Cible]",
      "progression": "[VERT|JAUNE|ORANGE|ROUGE|NON-DÉBUTÉ|TERMINÉ]",
      "finalite": "[Objectif final]",
      "periode_debut": "[JJ/MM/AAAA]",
      "periode_fin": "[JJ/MM/AAAA]"
    }
  ],

  "pacto_analysis": {
    "P": { "status": "[STATUT]", "recommendations": ["[R1]", "[R2]"] },
    "A": { "status": "[STATUT]", "recommendations": ["[R1]"] },
    "C": { "status": "[STATUT]", "recommendations": ["[R1]", "[R2]"] },
    "T": { "status": "[STATUT]", "recommendations": [] },
    "O": { "status": "[STATUT]", "recommendations": [] }
  },

  "enjeux": [
    {
      "metrique": "[Nom métrique]",
      "resultat": "[Valeur actuelle]",
      "kpi_cible": "[Seuil cible]",
      "enjeu": "[Description du problème]",
      "raisonnement": "[Analyse causale]",
      "optimisation": "[Actions PACTO référencées]"
    }
  ],

  "learning": [
    {
      "debut": "[DATE]",
      "fin": "[DATE]",
      "statut": "SUCCÈS|ÉCHEC",
      "campagne": "[Nom]",
      "facteurs": "[Ce qui a fonctionné ou échoué]",
      "audiences": "[Audiences impliquées]",
      "publicites": "[Créatifs impliqués]",
      "offres_funnel": "[Offre / funnel testé]"
    }
  ]
}
```

**Important pour les optimisations_90j** : Charger les entrées existantes depuis le dernier rapport Excel (si disponible dans `reports/`) et mettre à jour `resultat_actuel` et `progression`. Ne pas supprimer les optimisations en cours — seulement les marquer TERMINÉ si le KPI est atteint.

Puis générer le rapport Excel :

```powershell
cd C:\Users\bbere\claude-projects\meta-ads-agent
python scripts/generate_pacto_report.py --data data/report_data.json
```

Le fichier sera généré dans `reports/PACTO-Bienpréter-[DATE].xlsx`.

---

## Phase 5 — Rapport textuel + Gate d'approbation

Présenter le rapport structuré suivant, puis s'arrêter :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RAPPORT META ADS PACTO — Bienprêter #2
[Période analysée]  |  Dépense : €[X]  |  Statut : [STATUT]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RÉSUMÉ COMPTE
  Campagnes actives : [N]
  Dépense 7j : €[X] ([+/-X%] vs semaine précédente)
  CPA leads : €[X] (cible : €[X])
  CPM moyen : €[X] | CTR moyen : [X]% | Fréquence : [X]

DIAGNOSTIC PACTO
  P – Paramètres   : [STATUT]  [✓ OK / → action]
  A – Audiences    : [STATUT]  [✓ OK / → action]
  C – Créatives    : [STATUT]  [✓ OK / → action]
  T – Tunnel       : [STATUT]  [✓ OK / → action]
  O – Offre        : [STATUT]  [✓ OK / → action]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIONS URGENTES (impact estimé : €[X]/semaine)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

R1 — [Titre court] [LETTRE PACTO]
  Problème   : [Description avec chiffres]
  Action     : [Ce qu'il faut faire concrètement]
  Impact     : €[X] estimés / semaine
  Confiance  : HIGH / MEDIUM
  Appliquer ? [ ] OUI  [ ] NON

R2 — ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPTIMISATIONS RECOMMANDÉES (non-urgentes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

R3 — [Titre court] [LETTRE PACTO]
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPPORTUNITES DE SCALING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

R5 — [Titre court] [LETTRE PACTO]
  Opportunité  : [Données]
  Action       : [Budget +X% ou lancer Y]
  Impact projeté : +[X]% conversions
  Appliquer ? [ ] OUI  [ ] NON

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMPAGNES EN BONNE SANTÉ — aucune action
  - [Campagne] : CPA €[X], fréquence [X], CTR [X]%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rapport Excel : reports/PACTO-Bienpréter-[DATE].xlsx

Pour appliquer : réponds avec les numéros (ex: "Applique R1, R3")
ou "Applique tout" ou "Annule".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**STOP ICI.** Ne rien appliquer avant approbation explicite.

---

## Phase 6 — Application (après approbation)

Une fois les recommandations approuvées, invoquer le skill `/meta-ads-apply` en passant la liste des recommandations approuvées avec :
- Numéros des recommandations approuvées
- IDs des campagnes/ad sets/annonces concernés (récupérés depuis Windsor.ai)
- Type de changement (pause, budget, statut...)

---

## Règles de sécurité

- Ne jamais mettre en pause une campagne avec > €500 de dépense cette semaine sans signal HIGH confidence
- Ne jamais augmenter un budget de plus de 30% en une seule session
- Ne jamais appliquer > 5 modifications sans re-confirmation
- Si Windsor.ai retourne 0 lignes : reporter le problème de connectivité et s'arrêter
- Toujours loguer : objet modifié, valeur avant, valeur après

---

## Gestion des erreurs

| Erreur | Action |
|--------|--------|
| Windsor.ai retourne 0 lignes | Vérifier l'account_id, reporter et s'arrêter |
| Champ manquant | Passer, noter dans le rapport, continuer avec les champs disponibles |
| Campagne avec spend = €0 toute la semaine | Signaler comme problème de diffusion (pas wasted spend) |
| Aucune conversion (0 leads, 0 achats) | Analyser CTR/CPM/spend uniquement, noter le gap |
| Script Python échoue | Générer le rapport textuel uniquement, signaler l'erreur |
