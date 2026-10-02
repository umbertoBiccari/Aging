"""Run from a fresh workspace-local kernel, validate, and export the full and colloquium HTML editions."""
from pathlib import Path
import os
import sys
import json
import hashlib
import re
ROOT = Path(__file__).resolve().parents[1]
for key, name in [("MPLCONFIGDIR", "matplotlib"), ("IPYTHONDIR", "ipython"),
                  ("JUPYTER_RUNTIME_DIR", "jupyter-runtime"), ("JUPYTER_CONFIG_DIR", "jupyter-config")]:
    os.environ.setdefault(key, str(ROOT / ".work" / name))
    Path(os.environ[key]).mkdir(parents=True, exist_ok=True)
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

kernel_root = ROOT / ".work" / "kernels"
kernel_dir = kernel_root / "bioage"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(json.dumps({
    "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
    "display_name": "Bioage validation", "language": "python"}))
ksm = KernelSpecManager(kernel_dirs=[str(kernel_root)])
km = KernelManager(kernel_name="bioage", kernel_spec_manager=ksm)
path = ROOT / "Bioage_Machine_Learning.ipynb"
notebook = nbformat.read(path, as_version=4)

def report(cell, cell_index, **kwargs):
    if cell.cell_type == "code":
        print(f"Executing cell {cell_index + 1}/{len(notebook.cells)}", flush=True)

if "--export-only" not in sys.argv:
    client = NotebookClient(notebook, km=km, timeout=300,
                            resources={"metadata": {"path": str(ROOT)}}, on_cell_start=report)
    try:
        client.execute()
    finally:
        if km.has_kernel:
            km.shutdown_kernel(now=True)
nbformat.validate(notebook)
errors = [out for cell in notebook.cells if cell.cell_type == "code"
          for out in cell.outputs if out.output_type == "error"]
if errors:
    raise RuntimeError(errors)
nbformat.write(notebook, path)

# Reading editions. Kernel widgets are omitted because a static file cannot run Python
# callbacks; every interactive window also stores a static figure, which is kept.
from bs4 import BeautifulSoup

STYLE = """
html {scroll-behavior:smooth} body {background:#f1f5f7 !important;color:#193446}
main {max-width:1120px;margin:32px auto;background:white;padding:32px 48px;
      border-radius:14px;box-shadow:0 10px 40px #15344a0b}
.jp-RenderedMarkdown {font-size:16px;line-height:1.68;color:#253c48}
.jp-RenderedMarkdown h2 {border-top:1px solid #dae5e9;padding-top:26px;margin-top:30px;color:#123047}
.jp-RenderedMarkdown h3 {color:#16877c} .jp-RenderedMarkdown table {font-size:14px !important;line-height:1.5}
.jp-RenderedMarkdown th {background:#eaf3f5 !important;color:#123047}
.jp-RenderedMarkdown td, .jp-RenderedMarkdown th {padding:10px !important}
.jp-OutputArea-output {overflow-x:auto} .jp-OutputArea-output img {max-width:100%;height:auto}
video {max-width:100%;border-radius:8px;background:#edf5f5}
.code-panel {margin:8px 0 18px;border:1px solid #dce6ea;border-radius:7px;background:#f7fafb}
.code-panel summary {padding:9px 14px;color:#52717e;font-size:13px;cursor:pointer;
      font-family:var(--jp-ui-font-family,system-ui,-apple-system,"Segoe UI",sans-serif)}
.jp-Cell {padding:4px 0} a {color:#087f83} mjx-container {overflow-x:auto;overflow-y:hidden;max-width:100%}
@media(max-width:750px){main{margin:0;padding:18px 16px}.jp-RenderedMarkdown{font-size:15px}}
@media print {body{background:white !important} main{box-shadow:none;margin:0;padding:0} .code-panel{display:none}}
"""
MATHJAX_CONFIG = (r"window.MathJax={tex:{inlineMath:[['$','$'],['\\(','\\)']],displayMath:[['$$','$$'],['\\[','\\]']]},"
                  r"svg:{fontCache:'local'},options:{enableMenu:false,skipHtmlTags:['script','noscript','style','textarea','pre','code']}};")


def export(nb, html_path, title, colloquium=False):
    reading = nbformat.reads(nbformat.writes(nb), as_version=4)
    reading.metadata.pop("widgets", None)
    if colloquium:
        reading.cells = [c for c in reading.cells if "colloquium" in c.metadata.get("tags", [])]
    alts = []
    for cell in reading.cells:
        if cell.cell_type == "code":
            cell.outputs = [out for out in cell.outputs
                            if "application/vnd.jupyter.widget-view+json" not in out.get("data", {})]
            for out in cell.outputs:
                if "image/png" in out.get("data", {}):
                    alts.append(out.get("metadata", {}).get("image/png", {}).get("alt")
                                or cell.metadata.get("alt") or "")
    exporter = HTMLExporter(template_name="lab")
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    exporter.exclude_input = colloquium
    html, _ = exporter.from_notebook_node(reading)
    soup = BeautifulSoup(html, "html.parser")
    images = soup.select(".jp-OutputArea-output img")
    if len(images) == len(alts):
        for img, alt in zip(images, alts):
            if alt:
                img["alt"] = alt
    else:
        print(f"Warning: {len(images)} images but {len(alts)} image outputs; alt text left unchanged")
    for panel in soup.select(".jp-CodeCell .jp-Cell-inputWrapper"):
        details = soup.new_tag("details")
        details["class"] = "code-panel"
        summary = soup.new_tag("summary")
        summary.string = "Show / hide Python"
        details.append(summary)
        panel.wrap(details)
    for script in soup.find_all("script", src=True):
        if any(key in script["src"].lower() for key in ["mathjax", "require", "jquery"]):
            script.decompose()
    # Replace the notebook's MathJax 2 configuration with a self-contained MathJax 3 SVG renderer.
    for script in soup.find_all("script"):
        if script.get("type") == "text/x-mathjax-config" or "init_mathjax" in script.get_text():
            script.decompose()
    vendor = ROOT / "assets" / "vendor" / "mathjax-tex-svg.js"
    if not vendor.exists():
        raise FileNotFoundError("MathJax bundle is required for offline equation rendering.")
    config = soup.new_tag("script")
    config.string = MATHJAX_CONFIG
    soup.body.append(config)
    renderer = soup.new_tag("script")
    renderer.string = vendor.read_text().replace("</script", r"<\/script")
    soup.body.append(renderer)
    style = soup.new_tag("style")
    style.string = STYLE
    soup.head.append(style)
    soup.title.string = title
    html_path.write_text(str(soup), encoding="utf-8")
    return len(reading.cells), len(images)


html_path = ROOT / "Bioage_Machine_Learning.html"
n_full, img_full = export(notebook, html_path, "Learning biological age | An interdisciplinary research notebook")
colloquium_path = ROOT / "Bioage_Colloquium.html"
n_coll, img_coll = export(notebook, colloquium_path, "Learning biological age | Colloquium edition", colloquium=True)

tags = [t for c in notebook.cells for t in c.metadata.get("tags", [])]
manifest = {
    "prepared": "2026-09-29",
    "source_type": "Manuscript versions used for this lecture",
    "papers": [{"file": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in [ROOT / "MetAgePaper_submitted.pdf", ROOT / "SHAP_SIMODS_03.pdf"]],
    "synthetic_data": "Generated in notebook, seed 2026. No patient data used.",
    "not_included": ["patient-level study data", "P1 extended data and supplementary files"],
    "videos": sorted(p.name for p in (ROOT / "assets" / "videos").glob("*.mp4")),
    "validation": {"cells": len(notebook.cells), "code_cells": sum(c.cell_type=="code" for c in notebook.cells),
                   "markdown_cells": sum(c.cell_type=="markdown" for c in notebook.cells),
                   "colloquium_cells": tags.count("colloquium"),
                   "execution_errors": len(errors), "python": sys.version,
                   "html_images": img_full, "colloquium_html_cells": n_coll},
}
(ROOT / "data" / "source_manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Verified and exported {path.name} ({len(notebook.cells)} cells, {len(errors)} errors), "
      f"{html_path.name} and {colloquium_path.name} ({n_coll} cells)", flush=True)
