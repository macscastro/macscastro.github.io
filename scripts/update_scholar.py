"""Update the Google Scholar metrics (citations, h-index, i10-index) in index.html.

Reads the public Scholar profile and rewrites the <b data-scholar="..."> elements.
Run by .github/workflows/scholar.yml; can also be run by hand: python3 scripts/update_scholar.py
"""
import re
import sys
import urllib.request
from pathlib import Path

PROFILE = "https://scholar.google.com/citations?user=KkHCEkEAAAAJ&hl=en"
INDEX = Path(__file__).resolve().parent.parent / "index.html"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

req = urllib.request.Request(PROFILE, headers={"User-Agent": UA, "Accept-Language": "en"})
try:
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
except Exception as e:
    sys.exit(f"Could not fetch Scholar profile: {e}")

# The stats table has 6 cells: citations, h-index, i10-index × (all time, since year)
cells = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
if len(cells) < 6:
    sys.exit("Scholar stats not found (Google may have served a CAPTCHA); leaving index.html unchanged.")
metrics = {"citations": cells[0], "h-index": cells[2], "i10-index": cells[4]}

page = INDEX.read_text(encoding="utf-8")
for key, value in metrics.items():
    page, n = re.subn(rf'(<b data-scholar="{key}">)\d+(</b>)', rf"\g<1>{value}\g<2>", page)
    if n == 0:
        sys.exit(f'No <b data-scholar="{key}"> element found in index.html')
INDEX.write_text(page, encoding="utf-8")
print("Scholar metrics:", metrics)
