"""Synthetic planted ground truth; deterministic construction, no random seed needed."""
import json
from pathlib import Path
from .core import REASONS


def fixture_document():
    records = []
    for i in range(200):
        status = "lost" if i < 120 else "won" if i < 160 else "open"
        records.append({"id": f"deal-{i:03d}", "name": f"Synthetic opportunity {i:03d}", "status": status, "reason": REASONS[i // 20] if status == "lost" else None, "amount_minor": 10000, "closed_on": None if status == "open" else "2026-09-30"})
    return {"synthetic": True, "provenance": "synthetic fixture", "as_of": "2026-09-30", "currency": "GBP", "records": records}


def expectations():
    # Independently hand-computed: 6 groups x 20 losses; 40 won; 40 open.
    return {"synthetic": True, "label": "Synthetic hand-computed expectations", "total_records": 200, "status_counts": {"lost": 120, "won": 40, "open": 40}, "total_amount_minor": 2000000, "lost_amount_minor": 1200000, "reasons": {reason: {"count": 20, "amount_minor": 200000, "record_ids": [f"deal-{i:03d}" for i in range(group * 20, (group + 1) * 20)]} for group, reason in enumerate(REASONS)}}


def generate(out):
    from .cli import atomic_write
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in (("opportunities.json", fixture_document()), ("expectations.json", expectations())):
        atomic_write(out / name, json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    atomic_write(out / "SYNTHETIC.md", "<!-- Synthetic fixture set -->\n# Synthetic fixtures\nAll 200 opportunities are invented test data. No real outreach results.\n")
