"""Generate metrics: word‑count per agency & yearly change counts."""

import json, re, time, pandas as pd
from pathlib import Path
from collections import deque, defaultdict
import logging

DATA_DIR = Path("data")
regs = json.loads((DATA_DIR / "regulations.json").read_text())
vers = json.loads((DATA_DIR / "versions.json").read_text())

word_re = re.compile(r"\w+")
word_records = []
change_counter = defaultdict(int)

# ---------- word counts ----------
for title_num, struct in regs.items():
    dq = deque([struct])
    while dq:
        node = dq.popleft()
        if not isinstance(node, dict):
            continue
        if node.get("type") == "section":
            txt = f"{node.get('identifier', '')} {node.get('label', '')}"
            agency = node.get("label_description") or "Unknown"
            word_records.append({"agency": agency, "words": len(word_re.findall(txt))})
        dq.extend(node.get("children", []))

word_df = pd.DataFrame(word_records)
word_metrics = (
    word_df.groupby("agency")["words"].sum().sort_values(ascending=False).to_dict()
)

# ---------- change counts ----------
for _, version_list in vers.items():
    for item in version_list:
        # Skip anything that isn't a proper dict (some titles may embed notes)
        if not isinstance(item, dict):
            continue
        if item.get("removed"):
            continue
        date_val = item.get("date")
        if not date_val:
            continue
        yr = date_val.split("-")[0]
        change_counter[yr] += 1

metrics_out = {
    "generated": int(time.time()),
    "word_count_per_agency": word_metrics,
    "changes_per_year": dict(sorted(change_counter.items())),
}
(DATA_DIR / "metrics.json").write_text(json.dumps(metrics_out, indent=2))
print("✅ metrics.json ready")
