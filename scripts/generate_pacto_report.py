"""
Génère le rapport PACTO Meta Ads hebdomadaire (Bienprêter #2).
Usage: python scripts/generate_pacto_report.py --data data/report_data.json
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

# ─── Palette ──────────────────────────────────────────────────────────────────

COLORS = {
    "VERT":        "00B050",
    "JAUNE":       "FFC000",
    "ORANGE":      "FF6600",
    "ROUGE":       "FF0000",
    "NON-DÉBUTÉ":  "A6A6A6",
    "TERMINÉ":     "00B0F0",
    "SUCCÈS":      "00B050",
    "ÉCHEC":       "FF0000",
    "header_bg":   "1F3864",
    "section_bg":  "2F5496",
    "subheader":   "D6E4F7",
    "P":           "7030A0",
    "A":           "2F5496",
    "C":           "375623",
    "T":           "974706",
    "O":           "843C0C",
    "alt_row":     "F2F2F2",
    "white":       "FFFFFF",
    "light_grey":  "D9D9D9",
}

PACTO_LABELS = {
    "P": "P – Paramètres",
    "A": "A – Audiences",
    "C": "C – Créatives",
    "T": "T – Tunnel de vente",
    "O": "O – Offre",
}

# ─── Style helpers ─────────────────────────────────────────────────────────────

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color="000000", size=10, italic=False):
    return Font(bold=bold, color=color, size=size, italic=italic, name="Arial")

def border_thin():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def align(h="left", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def status_fill(status):
    key = status.upper().replace(" ", "")
    for k, v in COLORS.items():
        if k.upper().replace(" ", "") == key:
            return fill(v)
    return fill("FFFFFF")

def write_header(ws, row, col, text, bg="header_bg", fg="FFFFFF", bold=True, size=11, merge_to=None):
    cell = ws.cell(row=row, column=col, value=text)
    cell.fill = fill(COLORS[bg])
    cell.font = font(bold=bold, color=fg, size=size)
    cell.alignment = align("center", "center", wrap=True)
    cell.border = border_thin()
    if merge_to:
        ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=merge_to)

def write_cell(ws, row, col, value, bg=None, bold=False, fg="000000", wrap=True, h_align="left"):
    cell = ws.cell(row=row, column=col, value=value)
    if bg:
        cell.fill = fill(bg)
    cell.font = font(bold=bold, color=fg, size=10)
    cell.alignment = align(h_align, "center", wrap)
    cell.border = border_thin()
    return cell

def write_status(ws, row, col, status):
    bg = COLORS.get(status.upper(), "FFFFFF")
    fg = "FFFFFF" if status.upper() in ("ROUGE", "VERT", "NON-DÉBUTÉ", "TERMINÉ", "ÉCHEC") else "000000"
    cell = ws.cell(row=row, column=col, value=status)
    cell.fill = fill(bg)
    cell.font = font(bold=True, color=fg, size=10)
    cell.alignment = align("center", "center")
    cell.border = border_thin()

# ─── Sheet: DASHBOARD ─────────────────────────────────────────────────────────

def build_dashboard(wb, d):
    ws = wb.create_sheet("DASHBOARD")
    ws.sheet_view.showGridLines = False

    col_widths = [2, 28, 14, 14, 14, 14, 2, 28, 14, 14]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for r in range(1, 40):
        ws.row_dimensions[r].height = 20

    # ── Titre ──
    ws.merge_cells("B2:E2")
    c = ws["B2"]
    c.value = d.get("client_name", "NOM DU CLIENT")
    c.fill = fill(COLORS["header_bg"])
    c.font = font(bold=True, color="FFFFFF", size=14)
    c.alignment = align("center", "center")

    ws.merge_cells("H2:I2")
    ws["H2"].value = "Date de mise à jour"
    ws["H2"].fill = fill(COLORS["section_bg"])
    ws["H2"].font = font(bold=True, color="FFFFFF", size=10)
    ws["H2"].alignment = align("center", "center")
    ws["J2"].value = d.get("report_date", datetime.today().strftime("%d/%m/%Y"))
    ws["J2"].fill = fill(COLORS["subheader"])
    ws["J2"].font = font(bold=True, size=10)
    ws["J2"].alignment = align("center", "center")

    # ── Statut compte ──
    ws.merge_cells("H3:I3")
    ws["H3"].value = "Statut du compte"
    ws["H3"].fill = fill(COLORS["section_bg"])
    ws["H3"].font = font(bold=True, color="FFFFFF", size=10)
    ws["H3"].alignment = align("center", "center")
    status = d.get("account_status", "VERT")
    write_status(ws, 3, 10, status)

    # ── KPIs ──
    ws.row_dimensions[5].height = 22
    headers_kpi = ["", "CPA Leads", "CPA Achats", "Budget/j", "Fréquence max"]
    for i, h in enumerate(headers_kpi, 2):
        c = ws.cell(row=5, column=i, value=h)
        c.fill = fill(COLORS["section_bg"])
        c.font = font(bold=True, color="FFFFFF", size=10)
        c.alignment = align("center", "center")
        c.border = border_thin()

    ws.cell(row=6, column=2, value="KPIs Visés").fill = fill(COLORS["subheader"])
    ws["B6"].font = font(bold=True, size=10)
    ws["B6"].alignment = align("center", "center")
    ws["B6"].border = border_thin()
    targets = d.get("kpis_cibles", {})
    for col, key in [(3, "cpa_leads"), (4, "cpa_achats"), (5, "budget_journalier"), (6, "frequence_max")]:
        val = targets.get(key)
        v = f"€{val}" if val and key != "frequence_max" else (str(val) if val else "-")
        write_cell(ws, 6, col, v, h_align="center")

    ws.cell(row=7, column=2, value="KPIs Actuels").fill = fill(COLORS["subheader"])
    ws["B7"].font = font(bold=True, size=10)
    ws["B7"].alignment = align("center", "center")
    ws["B7"].border = border_thin()
    actuals = d.get("kpis_actuels", {})
    for col, key in [(3, "cpa_leads"), (4, "cpa_achats"), (5, "budget_journalier"), (6, "frequence_moyenne")]:
        val = actuals.get(key)
        v = f"€{val}" if val and key not in ("frequence_moyenne", "budget_journalier") else (f"€{val}/j" if key == "budget_journalier" and val else (str(val) if val else "-"))
        if key == "cpa_leads" and val:
            v = f"€{val}"
        write_cell(ws, 7, col, v, h_align="center")

    # ── Plan 90 jours ──
    ws.row_dimensions[9].height = 22
    ws.merge_cells("B9:J9")
    ws["B9"].value = "📋  PLAN OPTIMISATIONS / TESTS – 90 JOURS"
    ws["B9"].fill = fill(COLORS["header_bg"])
    ws["B9"].font = font(bold=True, color="FFFFFF", size=11)
    ws["B9"].alignment = align("center", "center")

    plan_headers = ["OPTIMISATION / TEST", "MÉTRIQUE", "DÉPART", "ACTUEL", "VISÉ", "PROGRESSION", "FINALITÉ", "DÉBUT", "FIN"]
    for i, h in enumerate(plan_headers, 2):
        c = ws.cell(row=10, column=i, value=h)
        c.fill = fill(COLORS["section_bg"])
        c.font = font(bold=True, color="FFFFFF", size=9)
        c.alignment = align("center", "center", wrap=True)
        c.border = border_thin()

    plan = d.get("optimisations_90j", [])
    for r_off, item in enumerate(plan[:10]):
        row = 11 + r_off
        bg = COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF"
        write_cell(ws, row, 2, item.get("optimisation", ""), bg=bg)
        write_cell(ws, row, 3, item.get("metrique", ""), bg=bg, h_align="center")
        write_cell(ws, row, 4, item.get("resultat_depart", ""), bg=bg, h_align="center")
        write_cell(ws, row, 5, item.get("resultat_actuel", ""), bg=bg, h_align="center")
        write_cell(ws, row, 6, item.get("resultat_vise", ""), bg=bg, h_align="center")
        write_status(ws, row, 7, item.get("progression", "NON-DÉBUTÉ"))
        write_cell(ws, row, 8, item.get("finalite", ""), bg=bg)
        write_cell(ws, row, 9, item.get("periode_debut", ""), bg=bg, h_align="center")
        write_cell(ws, row, 10, item.get("periode_fin", ""), bg=bg, h_align="center")

    if not plan:
        for r_off in range(5):
            row = 11 + r_off
            for col in range(2, 11):
                write_cell(ws, row, col, "", bg=COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF")

# ─── Sheet: RAPPORT ───────────────────────────────────────────────────────────

def build_rapport(wb, d):
    ws = wb.create_sheet("RAPPORT")
    ws.sheet_view.showGridLines = False

    widths = [2, 12, 12, 50, 30, 18, 2, 30]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("B2:H2")
    ws["B2"].value = "📊  RAPPORT HEBDOMADAIRE META ADS – BIENPRÊTER #2"
    ws["B2"].fill = fill(COLORS["header_bg"])
    ws["B2"].font = font(bold=True, color="FFFFFF", size=12)
    ws["B2"].alignment = align("center", "center")

    headers = ["DATE DÉBUT", "DATE FIN", "ANALYSE DU COMPTE", "CAMPAGNES À OPTIMISER", "NIVEAU PACTO", "EXPLICATIONS / NOTES"]
    for i, h in enumerate(headers, 2):
        c = ws.cell(row=4, column=i, value=h)
        c.fill = fill(COLORS["section_bg"])
        c.font = font(bold=True, color="FFFFFF", size=10)
        c.alignment = align("center", "center", wrap=True)
        c.border = border_thin()
    ws.row_dimensions[4].height = 30

    rapports = d.get("rapport_semaine", [])
    for r_off, item in enumerate(rapports[:20]):
        row = 5 + r_off
        ws.row_dimensions[row].height = 60
        bg = COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF"
        write_cell(ws, row, 2, item.get("periode_debut", ""), bg=bg, h_align="center")
        write_cell(ws, row, 3, item.get("periode_fin", ""), bg=bg, h_align="center")
        write_cell(ws, row, 4, item.get("analyse", ""), bg=bg, wrap=True)
        campagnes = item.get("campagnes_a_optimiser", [])
        write_cell(ws, row, 5, "\n".join(campagnes) if isinstance(campagnes, list) else campagnes, bg=bg, wrap=True)
        niveau = item.get("niveau_optimisation", "")
        pacto_bg = COLORS.get(niveau, "FFFFFF") if niveau in COLORS else COLORS.get(niveau, COLORS["subheader"])
        c = ws.cell(row=row, column=6, value=PACTO_LABELS.get(niveau, niveau))
        c.fill = fill(COLORS.get(niveau, "FFFFFF"))
        c.font = font(bold=True, color="FFFFFF" if niveau in ("P", "A", "C", "T", "O") else "000000", size=10)
        c.alignment = align("center", "center", wrap=True)
        c.border = border_thin()
        write_cell(ws, row, 7, item.get("explications", ""), bg=bg, wrap=True)

    if not rapports:
        for r_off in range(5):
            row = 5 + r_off
            ws.row_dimensions[row].height = 50
            bg = COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF"
            for col in range(2, 8):
                write_cell(ws, row, col, "", bg=bg)

# ─── Sheet: ENJEUX ────────────────────────────────────────────────────────────

def build_enjeux(wb, d):
    ws = wb.create_sheet("ENJEUX")
    ws.sheet_view.showGridLines = False

    widths = [2, 22, 14, 14, 24, 45, 35]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("B2:G2")
    ws["B2"].value = "🔍  TROUBLESHOOTING COMPTE – ENJEUX & DIAGNOSTICS META ADS"
    ws["B2"].fill = fill(COLORS["header_bg"])
    ws["B2"].font = font(bold=True, color="FFFFFF", size=12)
    ws["B2"].alignment = align("center", "center")

    ws.merge_cells("B3:G3")
    ws["B3"].value = "Entrez les métriques pour identifier à quel niveau se situent les enjeux (campagne, audience, publicité)."
    ws["B3"].fill = fill(COLORS["subheader"])
    ws["B3"].font = font(italic=True, size=9)
    ws["B3"].alignment = align("center", "center")

    headers = ["MÉTRIQUES", "RÉSULTATS", "KPIs CIBLE", "ENJEUX", "RAISONNEMENT", "PISTES D'OPTIMISATION(S)"]
    for i, h in enumerate(headers, 2):
        c = ws.cell(row=5, column=i, value=h)
        c.fill = fill(COLORS["section_bg"])
        c.font = font(bold=True, color="FFFFFF", size=10)
        c.alignment = align("center", "center", wrap=True)
        c.border = border_thin()
    ws.row_dimensions[5].height = 25

    # Base de connaissance Meta Ads (pré-remplie)
    base = [
        ("Nb achats / leads", "", "", "Aucune conversion",
         "Le pixel/tracking est-il bien configuré ? Vérifier Events Manager, CAPI, EMQ ≥6.",
         "P – Vérifier paramétrage campagne et objectif\nA – Audience trop restrictive ?\nC – Le créatif capte-t-il l'attention ?"),
        ("CPA leads", "", "", "CPA trop élevé",
         "Le CPA a-t-il explosé du jour au lendemain (effet plafond de verre) ou monte progressivement ?",
         "P – Réduire le budget de 20%\nA – Audiences glaciales (exclusion visiteurs 180j)\nC – Tester 3 nouveaux hooks/angles"),
        ("ROAS", "", "", "ROAS insuffisant",
         "Le ROAS est lié à la valeur du panier moyen. Peut-on augmenter le volume ou la valeur de conversion ?",
         "O – Mettre en place des bundles / upsells\nO – Tester une offre plus agressive"),
        ("CTR", "", "≥ 0,90%", "CTR < 0,50% → mauvaise accroche",
         "Les gens ne cliquent pas. Le créatif ne capte pas l'attention. Revoir les 5 premières secondes.",
         "C – Tester 3 nouveaux hooks/angles\nC – Décliner visuel(s) gagnant(s)\nC – UGC / vrais visages"),
        ("CTR", "", "≥ 0,90%", "CTR élevé, peu de conversions",
         "CTR OK mais les gens n'achètent/ne convertissent pas sur la landing page.",
         "T – Améliorer cohérence pub ↔ landing page\nT – Optimiser l'expérience tunnel de vente"),
        ("Fréquence", "", "≤ 3,0", "Fréquence > 3,5 → fatigue créative",
         "L'audience a trop vu la pub. Coûts en hausse, CTR en baisse. Ratio de première impression élevé ?",
         "C – Tester 3 nouveaux hooks/angles\nC – Décliner visuel(s) gagnant(s)\nP – Réduction de la fréquence"),
        ("CPM", "", "", "CPM en hausse > 30%",
         "Saturation d'audience ou concurrence accrue sur la période. Vérifier si fréquence monte aussi.",
         "A – Élargir audience lookalike (%)\nA – Audiences glaciales (exclusion 180j)\nP – Réduire budget 20%"),
        ("Audience overlap", "", "< 20%", "Overlap > 20% → cannibalisation",
         "Les audiences se chevauchent : vous enchérissez contre vous-même, les CPM et CPA augmentent.",
         "A – Exclusion d'audiences\nA – Consolidation en CBO"),
        ("Add to cart", "", "", "ATC élevés, peu d'achats",
         "L'intention d'achat est là mais le tunnel bloque. Problème de frais de livraison, UX ou confiance.",
         "T – Améliorer expérience tunnel de vente\nO – Tester livraison gratuite\nO – Tester BOGO"),
        ("Impressions / Reach", "", "", "Dépense €0 ou distribution nulle",
         "La campagne ne distribue pas. Vérifier : statut actif, budget, dates, politique publicitaire Meta.",
         "P – Vérifier paramétrage et statuts\nP – Refaire la campagne si bloquée"),
        ("Budget quotidien", "", "", "Budget sous-dépensé (< 80%)",
         "La campagne n'utilise pas son budget. Phase d'apprentissage ? Audience trop petite ? CPC trop bas ?",
         "A – Élargir la taille d'audience\nP – Passer en CBO\nP – Tester un nouvel objectif d'optimisation"),
        ("Taux de conversion LP", "", "≥ 2%", "Taux conversion LP bas",
         "Les visiteurs arrivent mais ne convertissent pas. Problème de cohérence, de vitesse ou d'offre.",
         "T – Améliorer cohérence pub ↔ landing page\nT – Créer une landing page optimisée\nO – Tester offre plus agressive"),
    ]

    enjeux_data = d.get("enjeux", [])
    rows_to_write = enjeux_data if enjeux_data else [
        {"metrique": b[0], "resultat": b[1], "kpi_cible": b[2], "enjeu": b[3],
         "raisonnement": b[4], "optimisation": b[5]} for b in base
    ]

    for r_off, item in enumerate(rows_to_write):
        row = 6 + r_off
        ws.row_dimensions[row].height = 55
        bg = COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF"
        if isinstance(item, dict):
            write_cell(ws, row, 2, item.get("metrique", ""), bg=bg, bold=True)
            write_cell(ws, row, 3, item.get("resultat", ""), bg=bg, h_align="center")
            write_cell(ws, row, 4, item.get("kpi_cible", ""), bg=bg, h_align="center")
            write_cell(ws, row, 5, item.get("enjeu", ""), bg=bg, bold=True)
            write_cell(ws, row, 6, item.get("raisonnement", ""), bg=bg, wrap=True)
            write_cell(ws, row, 7, item.get("optimisation", ""), bg=bg, wrap=True)

# ─── Sheet: OPTIMISATIONS PACTO ───────────────────────────────────────────────

PACTO_OPTIONS = {
    "P": [
        "Réduire le nombre de campagnes dans le compte",
        "Réduire le nombre d'audiences dans la campagne",
        "Réduire le nombre de créatifs dans la campagne (2)",
        "Tester un nouvel objectif de campagne",
        "Tester un nouvel objectif d'optimisation (achat, ATC, vue)",
        "Passer en Dynamic Creatives",
        "Passer la campagne en CBO",
        "Passer la campagne en ABO",
        "Utiliser les placements automatiques (Advantage+)",
        "Tester les cost controls (bid cap / cost cap)",
        "Augmenter le budget de 20%",
        "Réduire le budget de 20%",
        "Utiliser le budget « lifetime »",
        "Réduction de la fréquence",
        "Passer l'attribution en (7day-view 1-day-click)",
        "« Stand By » – Pas assez de data/distribution",
        "Refaire la campagne au complet",
        "Lancer une campagne « Test » annexe",
    ],
    "A": [
        "Augmenter le volume de l'audience lookalike (%)",
        "Tester le ciblage broad",
        "Tester le ciblage par intérêt",
        "Utiliser des audiences glaciales (exclusion visiteurs 180j)",
        "Utiliser des audiences remarketing 30j (nouvelles interactions seulement)",
        "Créer une audience ATC pour recibler le fort volume d'ajout au panier",
        "Élargir les audiences de remarketing (mode stack)",
        "Utiliser les Special Ads Category",
        "Exclusion d'audiences (audience overlap)",
        "Cibler uniquement un des deux sexes",
        "Ciblage all (homme et femme)",
        "Élargir les âges au maximum (18-65+)",
        "Utiliser le ciblage géographique le plus large possible",
        "Recibler les Video Views",
        "Tester l'optimisation pour ad delivery en « Value »",
        "Language (All)",
        "Advantage+ Audience (ciblage IA Meta)",
        "Exclure les clients existants",
    ],
    "C": [
        "Utiliser le UGC pour présenter le produit/service",
        "Tester le format Instant Expérience",
        "Changer les 5 premières secondes d'une vidéo",
        "Tester le format catalogue carrousel DPA",
        "Tester un créatif product-oriented VS lifestyle",
        "Tester différents CTAs",
        "Utiliser les 5 leviers de hooks (Have, Feel, Average Day, Status, Proofs)",
        "Utiliser les reviews / stars rating dans les copy et visuels",
        "Changer les couleurs d'une publicité gagnante",
        "Tester la rédaction bullet point avec emoji",
        "Tester 3 nouveaux hooks / angles",
        "Décliner le/les visuel(s) gagnant(s)",
        "Réaliser un A/B test créatif",
        "Tester le format « illustration »",
        "Mettre de l'avant de vraies personnes/visages",
        "Tester une vidéo du produit en action/utilisation",
        "Tester des éléments « familiers »",
    ],
    "T": [
        "Tester la redirection vers la page produit",
        "Créer une landing page optimisée",
        "Tester la Lead Ad",
        "Tester le « lead magnet »",
        "Tester la campagne Messenger",
        "Tester le funnel Quiz",
        "Mettre en place un challenge",
        "Mettre en place une campagne Video Views",
        "Créer un funnel Webinaire",
        "Liste VIP / Concours",
        "Mettre en place un funnel tripwire + upsell",
        "Mettre en place une campagne Flash sale",
        "DABA (Dynamic Ads for Broad Audiences)",
        "Améliorer la cohérence entre la publicité et la landing page",
        "Améliorer l'expérience client du tunnel de vente",
        "Mettre en place un chat/bot de qualification",
    ],
    "O": [
        "Tester une offre plus agressive",
        "Tester le BOGO (Buy 1 Get 1)",
        "Tester le Buy 1 + Free gift",
        "Tester la livraison gratuite",
        "Tester l'essai gratuit / démo",
        "Tester un « Gated Shopping Event »",
        "Utiliser du « scarcity » / FOMO",
        "Changer les % en € ou vice versa sur les rabais",
        "Mettre en place des bundles pour augmenter la valeur de conversion",
        "Tester les rabais de volume",
        "Mettre en place des upsells / cross-sells",
        "Améliorer la promesse de valeur principale",
    ],
}

def build_pacto(wb, d):
    ws = wb.create_sheet("OPTIMISATIONS PACTO")
    ws.sheet_view.showGridLines = False

    for i, w in enumerate([2, 32, 32, 32, 32, 32], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("B2:F2")
    ws["B2"].value = "⚙️  RÉFÉRENTIEL OPTIMISATIONS PACTO – META ADS"
    ws["B2"].fill = fill(COLORS["header_bg"])
    ws["B2"].font = font(bold=True, color="FFFFFF", size=12)
    ws["B2"].alignment = align("center", "center")

    for col, key in enumerate(["P", "A", "C", "T", "O"], 2):
        c = ws.cell(row=4, column=col, value=PACTO_LABELS[key])
        c.fill = fill(COLORS[key])
        c.font = font(bold=True, color="FFFFFF", size=11)
        c.alignment = align("center", "center")
        c.border = border_thin()
    ws.row_dimensions[4].height = 28

    max_rows = max(len(v) for v in PACTO_OPTIONS.values())
    pacto_analysis = d.get("pacto_analysis", {})

    for r_off in range(max_rows):
        row = 5 + r_off
        ws.row_dimensions[row].height = 22
        for col, key in enumerate(["P", "A", "C", "T", "O"], 2):
            items = PACTO_OPTIONS[key]
            val = items[r_off] if r_off < len(items) else ""
            active = pacto_analysis.get(key, {}).get("recommendations", [])
            is_active = val in active
            bg_col = COLORS[key] if is_active else (COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF")
            fg_col = "FFFFFF" if is_active else "000000"
            c = ws.cell(row=row, column=col, value=val)
            c.fill = fill(bg_col)
            c.font = font(bold=is_active, color=fg_col, size=10)
            c.alignment = align("left", "center", wrap=True)
            c.border = border_thin()

    # Statut PACTO en bas
    ws.row_dimensions[5 + max_rows + 1].height = 25
    ws.cell(row=5 + max_rows + 2, column=2).value = "STATUT CETTE SEMAINE"
    ws.cell(row=5 + max_rows + 2, column=2).fill = fill(COLORS["section_bg"])
    ws.cell(row=5 + max_rows + 2, column=2).font = font(bold=True, color="FFFFFF", size=10)
    ws.cell(row=5 + max_rows + 2, column=2).alignment = align("center", "center")
    ws.merge_cells(start_row=5 + max_rows + 2, start_column=2, end_row=5 + max_rows + 2, end_column=2)

    for col, key in enumerate(["P", "A", "C", "T", "O"], 2):
        status = pacto_analysis.get(key, {}).get("status", "NON-DÉBUTÉ")
        write_status(ws, 5 + max_rows + 2, col, status)

# ─── Sheet: LEARNING ──────────────────────────────────────────────────────────

def build_learning(wb, d):
    ws = wb.create_sheet("LEARNING")
    ws.sheet_view.showGridLines = False

    widths = [2, 12, 12, 14, 28, 38, 28, 28, 28]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("B2:I2")
    ws["B2"].value = "🧠  BASE D'APPRENTISSAGE – SUCCÈS & ÉCHECS"
    ws["B2"].fill = fill(COLORS["header_bg"])
    ws["B2"].font = font(bold=True, color="FFFFFF", size=12)
    ws["B2"].alignment = align("center", "center")

    headers = ["DATE DÉBUT", "DATE FIN", "SUCCÈS / ÉCHEC", "CAMPAGNE", "FACTEURS DE SUCCÈS / ÉCHEC", "AUDIENCE(S)", "PUBLICITÉS", "OFFRES / FUNNEL"]
    for i, h in enumerate(headers, 2):
        c = ws.cell(row=4, column=i, value=h)
        c.fill = fill(COLORS["section_bg"])
        c.font = font(bold=True, color="FFFFFF", size=10)
        c.alignment = align("center", "center", wrap=True)
        c.border = border_thin()
    ws.row_dimensions[4].height = 28

    learning = d.get("learning", [])
    for r_off, item in enumerate(learning[:30]):
        row = 5 + r_off
        ws.row_dimensions[row].height = 45
        bg = COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF"
        write_cell(ws, row, 2, item.get("debut", ""), bg=bg, h_align="center")
        write_cell(ws, row, 3, item.get("fin", ""), bg=bg, h_align="center")
        statut = item.get("statut", "")
        write_status(ws, row, 4, statut)
        write_cell(ws, row, 5, item.get("campagne", ""), bg=bg)
        write_cell(ws, row, 6, item.get("facteurs", ""), bg=bg, wrap=True)
        write_cell(ws, row, 7, item.get("audiences", ""), bg=bg, wrap=True)
        write_cell(ws, row, 8, item.get("publicites", ""), bg=bg, wrap=True)
        write_cell(ws, row, 9, item.get("offres_funnel", ""), bg=bg, wrap=True)

    if not learning:
        for r_off in range(8):
            row = 5 + r_off
            ws.row_dimensions[row].height = 40
            bg = COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF"
            for col in range(2, 10):
                write_cell(ws, row, col, "", bg=bg)

# ─── Sheet: MÉTRIQUES DOC ─────────────────────────────────────────────────────

def build_metriques_doc(wb):
    ws = wb.create_sheet("MÉTRIQUES DOC")
    ws.sheet_view.showGridLines = False

    for i, w in enumerate([2, 20, 20, 20, 20, 2, 20, 20], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("B2:E2")
    ws["B2"].value = "📖  LÉGENDE & RÉFÉRENTIEL MÉTRIQUES"
    ws["B2"].fill = fill(COLORS["header_bg"])
    ws["B2"].font = font(bold=True, color="FFFFFF", size=12)
    ws["B2"].alignment = align("center", "center")

    # Statuts compte
    ws.cell(row=4, column=2, value="STATUT COMPTE").fill = fill(COLORS["section_bg"])
    ws["B4"].font = font(bold=True, color="FFFFFF")
    ws["B4"].alignment = align("center", "center")
    ws["B4"].border = border_thin()
    ws.cell(row=4, column=3, value="SIGNIFICATION").fill = fill(COLORS["section_bg"])
    ws["C4"].font = font(bold=True, color="FFFFFF")
    ws["C4"].alignment = align("center", "center")
    ws["C4"].border = border_thin()

    statuts = [
        ("VERT", "Compte en bonne santé, KPIs atteints"),
        ("JAUNE", "Quelques points d'attention, optimisations en cours"),
        ("ORANGE", "Problèmes identifiés, actions urgentes requises"),
        ("ROUGE", "Compte en difficulté, intervention immédiate"),
        ("NON-DÉBUTÉ", "Optimisation non encore lancée"),
        ("TERMINÉ", "Optimisation finalisée"),
    ]
    for r_off, (s, desc) in enumerate(statuts):
        row = 5 + r_off
        write_status(ws, row, 2, s)
        write_cell(ws, row, 3, desc, bg=COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF")

    # PACTO legend
    ws.cell(row=4, column=5, value="FRAMEWORK PACTO").fill = fill(COLORS["section_bg"])
    ws["E4"].font = font(bold=True, color="FFFFFF")
    ws["E4"].alignment = align("center", "center")
    ws["E4"].border = border_thin()
    ws.cell(row=4, column=6, value="DESCRIPTION").fill = fill(COLORS["section_bg"])
    ws["F4"].font = font(bold=True, color="FFFFFF")
    ws["F4"].alignment = align("center", "center")
    ws["F4"].border = border_thin()

    pacto_desc = [
        ("P", "Paramètres du compte et de la campagne (structure, budget, objectif, attribution)"),
        ("A", "Audiences – ciblage, taille, exclusions, remarketing, lookalike"),
        ("C", "Créatives – visuels, copy, format, hooks, CTA"),
        ("T", "Tunnel de vente – landing page, funnel, expérience post-clic"),
        ("O", "Offre – prix, bundle, livraison, garantie, urgence"),
    ]
    for r_off, (key, desc) in enumerate(pacto_desc):
        row = 5 + r_off
        c = ws.cell(row=row, column=5, value=PACTO_LABELS[key])
        c.fill = fill(COLORS[key])
        c.font = font(bold=True, color="FFFFFF")
        c.alignment = align("center", "center")
        c.border = border_thin()
        write_cell(ws, row, 6, desc, bg=COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF", wrap=True)

    # Seuils métriques Meta
    ws.row_dimensions[13].height = 5
    ws.merge_cells("B14:F14")
    ws["B14"].value = "SEUILS DE RÉFÉRENCE – META ADS"
    ws["B14"].fill = fill(COLORS["section_bg"])
    ws["B14"].font = font(bold=True, color="FFFFFF", size=10)
    ws["B14"].alignment = align("center", "center")

    for i, h in enumerate(["MÉTRIQUE", "BON", "ATTENTION", "CRITIQUE", "ACTION PACTO"], 2):
        c = ws.cell(row=15, column=i, value=h)
        c.fill = fill(COLORS["section_bg"])
        c.font = font(bold=True, color="FFFFFF", size=9)
        c.alignment = align("center", "center")
        c.border = border_thin()

    seuils = [
        ("CTR", "≥ 1,0%", "0,5% – 1,0%", "< 0,5%", "C – Nouveaux hooks/angles"),
        ("Fréquence", "< 2,0", "2,0 – 3,5", "> 3,5", "C – Décliner créatifs / P – Réduire budget"),
        ("CPM", "Stable", "+20%", "+40% WoW", "A – Élargir audience / P – Réduire budget"),
        ("CPA", "≤ cible", "cible +20%", "cible +40%", "P/A/C selon diagnostic"),
        ("CPC", "< moyenne", "moyenne +30%", "moyenne +60%", "C – Améliorer accroche / A – Exclusions"),
        ("Audience overlap", "< 15%", "15–30%", "> 30%", "A – Exclusion d'audiences / CBO"),
        ("Budget delivery", "90–110%", "80–90%", "< 80% ou > 110%", "P – Vérifier paramétrage et enchères"),
    ]
    for r_off, row_data in enumerate(seuils):
        row = 16 + r_off
        ws.row_dimensions[row].height = 22
        bg = COLORS["alt_row"] if r_off % 2 == 0 else "FFFFFF"
        for col, val in enumerate(row_data, 2):
            c = ws.cell(row=row, column=col, value=val)
            cell_bg = bg
            if col == 3:
                cell_bg = "E2EFDA"
            elif col == 4:
                cell_bg = "FFEB9C"
            elif col == 5:
                cell_bg = "FFC7CE"
            c.fill = fill(cell_bg)
            c.font = font(size=9)
            c.alignment = align("center", "center", wrap=True)
            c.border = border_thin()

# ─── Main ──────────────────────────────────────────────────────────────────────

def generate(data_path: str, output_path: str = None):
    with open(data_path, encoding="utf-8") as f:
        d = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    build_dashboard(wb, d)
    build_rapport(wb, d)
    build_enjeux(wb, d)
    build_pacto(wb, d)
    build_learning(wb, d)
    build_metriques_doc(wb)

    if not output_path:
        date_str = d.get("report_date", datetime.today().strftime("%Y-%m-%d")).replace("/", "-")
        output_path = Path("reports") / f"PACTO-Bienpréter-{date_str}.xlsx"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    print(f"[OK] Rapport genere : {output_path}")
    return str(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Chemin vers le fichier JSON de données")
    parser.add_argument("--output", default=None, help="Chemin de sortie du fichier Excel")
    args = parser.parse_args()
    generate(args.data, args.output)
