#!/usr/bin/env python3
"""Per-chapter page counts from master.pdf, against the 2 to 3 page budget."""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

def from_aux():
    """Chapter -> first physical page, taken from the .toc file."""
    toc = HERE / "master.toc"
    if not toc.exists():
        sys.exit("no master.toc; run make first")
    rows = []
    # memoir emits \chapternumberline, not \numberline
    pat = re.compile(r"\\contentsline \{chapter\}"
                     r"\{(?:\\chapternumberline \{([^}]*)\}\s*)?(.+?)\}\{(\d+)\}")
    for line in toc.read_text(errors="replace").splitlines():
        m = pat.search(line)
        if m:
            num = (m.group(1) or "").strip()
            title = re.sub(r"\\[a-zA-Z]+\s*|[{}]", "", m.group(2)).strip()
            rows.append((f"{num} {title}".strip(), int(m.group(3))))
    return rows

def total_pages():
    r = subprocess.run(["pdfinfo", str(HERE / "master.pdf")], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0

rows = from_aux()
last = total_pages()
print(f"{'chapter':52s} {'start':>5s} {'pages':>5s}  budget")
bad = []
for i, (title, start) in enumerate(rows):
    end = rows[i + 1][1] if i + 1 < len(rows) else last + 1
    n = end - start
    # chapters 2..12 are the eleven lectures; 1 is the overview, 13+ tutorials and synthesis
    num = int(mm.group(1)) if (mm := re.match(r"^(\d+) ", title)) else 0
    is_lecture = 2 <= num <= 12
    flag = ""
    if is_lecture:
        flag = "ok" if 2 <= n <= 3 else ("OVER" if n > 3 else "under")
        if flag != "ok":
            bad.append((title, n))
    print(f"{title[:52]:52s} {start:5d} {n:5d}  {flag}")
print(f"\ntotal pages: {last}")
if bad:
    print("\noutside the 2 to 3 page target:")
    for t, n in bad:
        print(f"  {n} pp  {t}")
