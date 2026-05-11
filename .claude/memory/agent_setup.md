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
1. Agent fetches data & runs 5 analyses (anomaly, fatigue, pacing, wasted spend, scaling)
2. Generates numbered recommendations R1, R2... ranked by financial impact in €
3. STOPS — presents report to user for approval
4. User approves specific items: "Applique R1, R3"
5. `/meta-ads-apply` executes approved changes

## Meta API for Apply Step
- Requires env var: `META_ACCESS_TOKEN`
- Supports: pause/activate objects, update daily/lifetime budget (+30% max), update bid amount
- Fallback if no token: generates `apply_changes.py` script

## Key Windsor.ai Fields (confirmed valid)
campaign_name, campaign_id, campaign_status, adset_name, adset_id, adset_status, ad_name, ad_id, status, date, spend, impressions, reach, frequency, clicks, ctr, cpm, cpc, actions_purchase, actions_lead, cost_per_action_type_purchase, cost_per_action_type_lead, objective
