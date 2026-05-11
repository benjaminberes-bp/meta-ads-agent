---
name: meta-ads-agent-setup
description: Architecture and configuration of the autonomous Meta Ads weekly agent for Bienprêter #2
type: project
---

Autonomous Meta Ads agent fully configured for weekly operation.

**Why:** Automate weekly Meta Ads analysis with human approval gate before applying any changes.

**How to apply:** Reference this when improving the agent, debugging, or onboarding on a new device.

## Windsor.ai Account
- Connector: `facebook`
- Account ID: `683334547372319` (Bienprêter #2 - Compte Publicitaire)
- MCP connector ID: `mcp__6d014ba9-b778-4e58-9cfe-b24735571e43`
- Windsor user: `benjamin.beres@bienpreter.com`

## Skills
- `.claude/skills/meta-ads-agent/SKILL.md` — orchestrator: fetches Windsor.ai data → 5 analyses → structured report → waits for approval
- `.claude/skills/meta-ads-apply/SKILL.md` — executor: applies approved recommendations via Meta Marketing API v21.0

## Scheduled Task
- Path: `C:\Users\bbere\.claude\scheduled-tasks\meta-ads-weekly-agent\SKILL.md`
- Cron: `0 9 * * 1` (every Monday 9am local time)
- First run: 2026-05-18

## Approval Workflow (semi-automatic)
1. Agent fetches Windsor.ai data (14 days campaign, 7 days adset+ad)
2. Runs PACTO analysis (P/A/C/T/O — each gets VERT/JAUNE/ORANGE/ROUGE status)
3. Writes `data/report_data.json` with full analysis
4. Generates Excel report: `python scripts/generate_pacto_report.py --data data/report_data.json`
5. Presents numbered recommendations R1, R2... STOPS and waits for approval
6. User approves: "Applique R1, R3"
7. `/meta-ads-apply` executes approved changes

## PACTO Framework
- **P** – Paramètres : structure, budget, attribution, objectifs, diffusion
- **A** – Audiences : fréquence, CPM WoW, saturation, overlap, exclusions
- **C** – Créatives : CTR WoW, fatigue créative, formats, hooks
- **T** – Tunnel : cohérence pub/LP, taux de conversion, expérience post-clic
- **O** – Offre : valeur de conversion, ROAS, compétitivité

## Excel Report Generator
- Script: `scripts/generate_pacto_report.py`
- Input: `data/report_data.json`
- Output: `reports/PACTO-Bienpréter-YYYY-MM-DD.xlsx`
- Sheets: DASHBOARD, RAPPORT, ENJEUX, OPTIMISATIONS PACTO, LEARNING, MÉTRIQUES DOC
- Requires: `pip install openpyxl` (already installed)
- Test: `python scripts/generate_pacto_report.py --data data/report_example.json`

## Meta API for Apply Step
- Requires env var: `META_ACCESS_TOKEN`
- Supports: pause/activate objects, update daily/lifetime budget (+30% max), update bid amount
- Fallback if no token: generates `apply_changes.py` script

## Key Windsor.ai Fields (confirmed valid)
campaign_name, campaign_id, campaign_status, adset_name, adset_id, adset_status, ad_name, ad_id, status, date, spend, impressions, reach, frequency, clicks, ctr, cpm, cpc, actions_purchase, actions_lead, cost_per_action_type_purchase, cost_per_action_type_lead, objective
