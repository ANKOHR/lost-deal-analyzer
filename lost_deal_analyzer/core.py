"""Pure validation and aggregation. Amounts are opportunity value, not savings."""
from datetime import date
import re

REASONS = ("budget", "timing", "competitor", "no_fit", "no_response", "unknown")


class InputError(ValueError):
    """A named, actionable input failure."""


def fail(source, field, detail):
    raise InputError(f"SchemaError: {source}: field {field}: {detail}")


def validate_document(doc, source):
    if not isinstance(doc, dict):
        fail(source, "document", "expected object")
    required = {"synthetic", "provenance", "as_of", "currency", "records"}
    if set(doc) != required:
        fail(source, "document", f"missing {sorted(required - set(doc))}; unexpected {sorted(set(doc) - required)}")
    if type(doc["synthetic"]) is not bool:
        fail(source, "synthetic", "expected boolean")
    expected = "synthetic fixture" if doc["synthetic"] else "Henry's own data, entered by him"
    if doc["provenance"] != expected:
        fail(source, "provenance", f"must be {expected!r}")
    cutoff = parse_date(doc["as_of"], source, "as_of")
    if not isinstance(doc["currency"], str) or not re.fullmatch(r"[A-Z]{3}", doc["currency"]):
        fail(source, "currency", "expected three uppercase letters; no currency conversion is performed")
    if not isinstance(doc["records"], list):
        fail(source, "records", "expected array")
    for index, row in enumerate(doc["records"], 1):
        loc = f"{source}: record {index}"
        fields = {"id", "name", "status", "reason", "amount_minor", "closed_on"}
        if not isinstance(row, dict) or set(row) != fields:
            fail(loc, "record", f"expected exactly {sorted(fields)}")
        for field in ("id", "name"):
            value = row[field]
            if not isinstance(value, str) or not value.strip() or len(value) > 10000 or any(ord(c) < 32 for c in value) or "\u2014" in value:
                fail(loc, field, "expected nonblank text of at most 10000 characters, without controls or em dash")
        if row["status"] not in ("lost", "won", "open"):
            fail(loc, "status", "expected lost, won, or open")
        if row["reason"] not in REASONS and row["reason"] is not None:
            fail(loc, "reason", f"expected one of {REASONS} or null")
        if (row["status"] == "lost") != (row["reason"] is not None):
            fail(loc, "reason", "lost requires a reason (unknown allowed); won/open require null")
        if type(row["amount_minor"]) is not int or not 0 <= row["amount_minor"] <= 10**15:
            fail(loc, "amount_minor", "expected integer from 0 to 1000000000000000")
        if row["status"] == "open":
            if row["closed_on"] is not None:
                fail(loc, "closed_on", "open requires null")
        elif parse_date(row["closed_on"], loc, "closed_on") > cutoff:
            fail(loc, "closed_on", "future date relative to as_of")
    return doc


def parse_date(value, source, field):
    try:
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError()
        return date.fromisoformat(value)
    except ValueError:
        fail(source, field, "expected valid YYYY-MM-DD date")


def analyze(documents):
    """Aggregate only supplied records. No prediction or causal inference."""
    rows, sources, seen, currencies = [], [], set(), set()
    for source, document in sorted(documents, key=lambda item: item[0]):
        doc = validate_document(document, source)
        currencies.add(doc["currency"])
        sources.append({"file": source, "synthetic": doc["synthetic"], "provenance": doc["provenance"], "as_of": doc["as_of"]})
        for row in doc["records"]:
            if row["id"] in seen:
                fail(source, "id", f"duplicate id {row['id']!r}")
            seen.add(row["id"])
            rows.append(row)
    if len(currencies) > 1:
        fail("inputs", "currency", "mixed currencies cannot be aggregated")
    counts = {status: sum(r["status"] == status for r in rows) for status in ("lost", "won", "open")}
    reasons = {}
    for reason in REASONS:
        selected = sorted((r for r in rows if r["status"] == "lost" and r["reason"] == reason), key=lambda r: r["id"])
        reasons[reason] = {"count": len(selected), "amount_minor": sum(r["amount_minor"] for r in selected), "record_ids": [r["id"] for r in selected]}
    return {"schema_version": 1, "sources": sources, "currency": next(iter(currencies), None), "total_records": len(rows), "status_counts": counts, "total_amount_minor": sum(r["amount_minor"] for r in rows), "lost_amount_minor": sum(v["amount_minor"] for v in reasons.values()), "reasons": reasons, "honesty": "Counts and opportunity values computed from inputs. Reasons are recorded labels, not independently verified causes. Time saved and money saved are unmeasured and are not reported."}
