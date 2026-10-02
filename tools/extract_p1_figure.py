"""Re-create assets/figures/p1_original_figure2.png from P1 (Figure 2, PDF page 6) at high resolution.

Requires the Poppler tool `pdftoppm` (e.g. `brew install poppler`). The crop box is given as
fractions of the page, so it does not depend on the rendering resolution.
"""
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "MetAgePaper_submitted.pdf"
OUT = ROOT / "assets" / "figures" / "p1_original_figure2.png"
WORK = ROOT / ".work"
DPI = 400
BOX = (0.2378, 0.0641, 0.7740, 0.4125)   # left, top, right, bottom as page fractions

pdftoppm = shutil.which("pdftoppm") or "/usr/local/bin/pdftoppm"
if not Path(pdftoppm).exists():
    sys.exit("pdftoppm (Poppler) not found; the existing figure file is kept.")
WORK.mkdir(exist_ok=True)
subprocess.run([pdftoppm, "-r", str(DPI), "-f", "6", "-l", "6", "-png", "-singlefile",
                str(PDF), str(WORK / "p1-page6")], check=True)
page = Image.open(WORK / "p1-page6.png").convert("RGB")
W, H = page.size
crop = page.crop((int(BOX[0] * W), int(BOX[1] * H), int(BOX[2] * W), int(BOX[3] * H)))
crop.save(OUT, dpi=(DPI, DPI), optimize=True)
print(f"Saved {OUT.relative_to(ROOT)} at {crop.size[0]}x{crop.size[1]} px")
