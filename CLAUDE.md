# Meta Ads Agent

## Memory
Persistent memory is stored in `.claude/memory/` (version-controlled).
Always read and write memory files to `.claude/memory/` — not to `~/.claude/projects/`.
The index is at `.claude/memory/MEMORY.md`.

## Sync workflow
After sessions with important context:
```
git add .claude/memory/
git commit -m "update memory"
git push
```
On a new device after cloning:
```
git pull
```
