"""One static HTML page: summary, the bays over their limit, and every level."""

from collections.abc import Sequence
from html import escape

from rack_check.check import Result, Summary

STYLE = """
body{background:#111111;color:#EDEAE2;font:15px/1.5 Inter,system-ui,sans-serif;margin:2rem auto;
max-width:68rem;padding:0 1rem}h1{font-family:"Playfair Display",Georgia,serif;font-weight:400;
font-size:2.6rem;margin:0}h1+p{color:#8A8A8A}.big{color:#D4AF37;font-size:1.6rem}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{padding:.25rem .6rem;border-bottom:1px solid #2A2A2A;text-align:right}
th:first-child,td:first-child{text-align:left}tr.fail td{color:#111111;background:#D4AF37}
.note{color:#8A8A8A;font-size:.85rem}
"""

NOTE = (
    "Beam properties, steel grade, limits and prices are illustrative. This is not a structural "
    "design standard. Real rack capacity comes from the manufacturer's load tables, checked by a "
    "qualified engineer."
)


def render(results: Sequence[Result], s: Summary, title: str = "rack-check") -> str:
    rows = []
    for r in results:
        lv = r.level
        cells = [
            escape(lv.bay),
            str(lv.level),
            f"{lv.span_m:.1f}",
            escape(lv.profile),
            f"{lv.load_kg:,.0f}",
            f"{r.capacity_kg:,.0f}",
            f"{r.utilisation:.0%}",
            f"{r.sag_mm:.1f} / {r.limit_mm:.1f}",
            "pass" if r.ok else "FAIL",
            escape(r.upgrade) or ("-" if r.ok else "reduce load"),
        ]
        cls = "" if r.ok else ' class="fail"'
        rows.append(f"<tr{cls}>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    head = ["Bay", "Level", "Span m", "Beam", "Load kg", "Safe kg", "Use", "Sag mm", "", "Fix"]
    over = ", ".join(escape(b) for b in s.bays_over) or "none"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{escape(title)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>{STYLE}</style></head>
<body><h1>{escape(title)}</h1><p>{NOTE}</p>
<p class="big">{len(s.bays_over)} of {s.bays} bays over their limit,
{s.failing} of {s.levels} levels</p>
<p>Bays over: {over}. Beam pairs to replace: {s.failing - s.no_fix}, illustrative cost
BRL {s.fix_cost:,}. Levels no listed beam can carry: {s.no_fix}.</p>
<table><thead><tr>{"".join(f"<th>{h}</th>" for h in head)}</tr></thead>
<tbody>{"".join(rows)}</tbody></table>
<p class="note">{NOTE}</p></body></html>
"""
