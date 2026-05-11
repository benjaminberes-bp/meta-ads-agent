---
name: meta-ads-apply
description: Applies approved Meta Ads recommendations from the meta-ads-agent report. Translates approved recommendation items (R1, R2...) into Meta Marketing API calls. Requires META_ACCESS_TOKEN env var. If token not set, generates executable Python script instead. Always invoked after /meta-ads-agent and user approval — never run independently.
metadata:
  platform: Meta
  account_id: "683334547372319"
  requires_env: META_ACCESS_TOKEN
---

# Meta Ads Apply — Approved Changes Executor

Executes the recommendations approved by the user after the `/meta-ads-agent` report. This skill only applies changes that were explicitly approved.

---

## Pre-flight Checks

Before applying anything:

1. **Confirm approved list** — Echo back exactly which recommendations will be applied and what they change. Ask "Confirmes-tu ces [N] modifications ?" if more than 3 changes.

2. **Check META_ACCESS_TOKEN** — Run:
   ```powershell
   $env:META_ACCESS_TOKEN
   ```
   - If set → apply changes directly via PowerShell `Invoke-RestMethod`
   - If not set → generate `apply_changes.py` script and instruct user to run it

3. **Validate IDs** — Confirm campaign/adset/ad IDs from the Windsor.ai data pulled in Phase 1. Never hardcode IDs — always use IDs fetched from the session.

---

## Meta API Reference

Base URL: `https://graph.facebook.com/v21.0/`
Auth: `?access_token=$env:META_ACCESS_TOKEN`

### Supported Change Types

#### 1. Pause an ad / ad set / campaign
```
POST /{object_id}
Body: { "status": "PAUSED" }
```

#### 2. Activate an ad / ad set / campaign
```
POST /{object_id}
Body: { "status": "ACTIVE" }
```

#### 3. Update daily budget (campaign or ad set)
```
POST /{object_id}
Body: { "daily_budget": <amount_in_cents> }
```
Note: Meta API uses cents. €50/day = `5000`.

#### 4. Update lifetime budget
```
POST /{object_id}
Body: { "lifetime_budget": <amount_in_cents> }
```

#### 5. Update bid amount
```
POST /{object_id}
Body: { "bid_amount": <amount_in_cents> }
```

---

## Execution — With META_ACCESS_TOKEN

For each approved change, run via PowerShell:

```powershell
$token = $env:META_ACCESS_TOKEN
$objectId = "<ID_FROM_WINDSOR_DATA>"
$body = @{ status = "PAUSED" } | ConvertTo-Json

Invoke-RestMethod `
  -Method POST `
  -Uri "https://graph.facebook.com/v21.0/$objectId" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $body
```

After each call:
- Log: `✅ [Object name] → [Change applied] (ID: [ID])`
- On error: `❌ [Object name] → [Error message]` — stop and report, don't continue

---

## Execution — Without META_ACCESS_TOKEN (Fallback)

Generate a Python script `apply_changes.py` in the project root:

```python
import requests
import os

ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise ValueError("Set META_ACCESS_TOKEN environment variable first")

BASE_URL = "https://graph.facebook.com/v21.0"
CHANGES = [
    # Generated from approved recommendations:
    # {"id": "<object_id>", "name": "<object_name>", "change": {"status": "PAUSED"}},
]

for change in CHANGES:
    resp = requests.post(
        f"{BASE_URL}/{change['id']}",
        params={"access_token": ACCESS_TOKEN},
        json=change["change"]
    )
    if resp.ok:
        print(f"✅ {change['name']} → {change['change']}")
    else:
        print(f"❌ {change['name']} → {resp.json()}")
```

Then tell the user:
```
Script généré : apply_changes.py

Pour l'exécuter :
1. Exporte ton token Meta : $env:META_ACCESS_TOKEN = "ton_token_ici"
2. Lance : python apply_changes.py

Où obtenir ton token : Meta Business Suite → Paramètres → Accès API système
```

---

## Post-Application Report

After all changes are executed, output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ MODIFICATIONS APPLIQUÉES — [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| # | Objet | Modification | Statut |
|---|-------|-------------|--------|
| R1 | [Nom] | [Avant] → [Après] | ✅ OK |
| R2 | [Nom] | [Avant] → [Après] | ✅ OK |

Impact estimé : économies potentielles de €[X]/semaine

Prochain audit automatique : lundi [date] à 9h00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Guardrails

- Never apply a change not in the approved list
- Never delete campaigns, ad sets, or ads — only pause
- Budget increases are capped at +30% of current budget in a single apply
- If an API call fails, stop all subsequent changes and report the error
- Log every applied change with before/after values

---

## Getting META_ACCESS_TOKEN

If the user doesn't have a token yet, guide them:

1. Go to [Meta Business Suite](https://business.facebook.com) → Settings → Users → System Users
2. Create a System User with "EMPLOYEE" role
3. Grant it access to the ad account (Admin or Advertiser role)
4. Generate a token with these permissions: `ads_management`, `ads_read`, `business_management`
5. Copy the token and set: `$env:META_ACCESS_TOKEN = "your_token"`
6. For persistence, add to project `.env` file (already in `.gitignore`)
