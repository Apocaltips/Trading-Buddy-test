# Getting Started (Windows)

This repo is the merge workspace. Follow the plan in docs/ to build the merged system without touching the live Mac run.

## 0) Prereqs
- Git
- Python 3.11+
- Docker Desktop (for Freqtrade)

## 1) Read the plan (order matters)
```powershell
Get-Content docs\PRD.md
Get-Content docs\BEADS.md
Get-Content docs\IMPLEMENTATION_CHECKLIST.md
```

## 2) Build in dependency order
Follow `docs/BEADS.md` and `beads/plan.yaml`:
- Start with B1 -> B2 -> B3
- Then B4/B5 in parallel
- Then B6/B7 -> B8 -> B9
- Finish with B10-B12

## 3) Run tests
- Run a 5-10 min plumbing test first
- Run the shotgun test until 10:00 AM MST after plumbing passes

## Notes
- Do not modify the Mac Tradegate repo while the 10-hour run is active.
- If you run a live test in parallel, use a different public IP than the Mac.
