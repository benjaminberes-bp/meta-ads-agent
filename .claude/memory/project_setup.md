---
name: Project setup
description: How this project is structured and how memory sync works
type: project
---

Repo GitHub: https://github.com/benjaminberes-bp/meta-ads-agent (compte: benjaminberes-bp)

Le projet contient des skills Meta/Google Ads dans `.claude/skills/`.
La mémoire persistante est versionnée dans `.claude/memory/` et synchronisée via git.

**Why:** L'utilisateur veut retrouver le contexte de ses sessions sur plusieurs appareils.
**How to apply:** Toujours écrire les fichiers mémoire dans `.claude/memory/`, committer et pousser en fin de session importante.
