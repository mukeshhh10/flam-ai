# Audit submission

Runbook:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r your-submission/partA/requirements.txt
.\.venv\Scripts\python.exe your-submission/partA/analyze.py --out your-submission/partA/results.json
.\.venv\Scripts\python.exe your-submission/partA/audit_v0.py | Tee-Object your-submission/partA/audit_v0_output.txt
.\.venv\Scripts\python.exe your-submission/partB/capacity.py | Tee-Object your-submission/partB/capacity_output.txt
```

Start with `partA/analysis.md`, `partB/answers.md`, and `partC/memo.md`.
`NOTEBOOK.md` records the chronology and `AI_USAGE.md` discloses AI assistance.
