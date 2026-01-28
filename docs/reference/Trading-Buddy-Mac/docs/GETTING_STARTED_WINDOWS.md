# Getting Started (Windows Codex CLI)

This repo is **docs-only**. It tells you exactly how to build the merged system in a separate workspace without touching the live Mac run.

## 0) Prereqs
- Git
- Python 3.11+
- Docker Desktop (for Freqtrade)
- Enough disk space for a separate workspace

## 1) Clone this repo
```powershell
git clone https://github.com/Apocaltips/Trading-Buddy-Mac.git
cd Trading-Buddy-Mac
```

## 2) Read the plan (order matters)
```powershell
Get-Content docs\PRD.md
Get-Content docs\BEADS.md
Get-Content docs\IMPLEMENTATION_CHECKLIST.md
```

## 3) Create a clean workspace
```powershell
mkdir ..\merge_lab
cd ..\merge_lab
```

## 4) Pull source repos you’ll build from
```powershell
git clone https://github.com/Apocaltips/Trading-Buddy-test.git
# (If you need Tradegate code, clone it here too)
# git clone https://github.com/Apocaltips/<tradegate-repo>.git
```

## 5) Build in dependency order
Follow `docs/BEADS.md` and `beads/plan.yaml`:
- Start with **B1 → B2 → B3**
- Then B4/B5 in parallel
- Then B6/B7

## 6) Run tests
- Run a **5–10 min plumbing test** first
- Run a **2‑hour dry‑run** test only after plumbing is clean

## 7) Push results
- Push all code + reports to the GitHub repo used for the build

## Notes
- Do **not** modify the Mac Tradegate repo while the 10‑hour run is active.
- If you run a live 2‑hour test in parallel, use the Windows machine’s public IP (different from the Mac) to avoid API rate‑limit collisions.

