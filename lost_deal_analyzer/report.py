"""Deterministic reports with explicit provenance and measurement limits."""
import json


def banner(result):
    sources = result["sources"]
    if not sources:
        return "DATA PROVENANCE: No input records or files."
    return "DATA PROVENANCE: " + "; ".join(f"{s['file']}: {s['provenance']} (synthetic: {str(s['synthetic']).lower()}, as_of: {s['as_of']})" for s in sources)


def render(result, format):
    if format == "json":
        return json.dumps({"provenance_banner": banner(result), **result}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    lines = ["# Lost Deal Analyzer", "", banner(result), "", result["honesty"], "", f"Records: {result['total_records']}", f"Status counts: lost {result['status_counts']['lost']}, won {result['status_counts']['won']}, open {result['status_counts']['open']}", f"Currency: {result['currency'] or 'none'}", f"Total opportunity value (minor units): {result['total_amount_minor']}", f"Lost opportunity value (minor units): {result['lost_amount_minor']}", "", "| Recorded reason | Count | Opportunity value (minor units) | Record IDs |", "| --- | ---: | ---: | --- |"]
    for reason, value in result["reasons"].items():
        ids = ", ".join(value["record_ids"]).replace("|", "\\|").replace("<", "&lt;")
        lines.append(f"| {reason} | {value['count']} | {value['amount_minor']} | {ids} |")
    return "\n".join(lines) + "\n"
