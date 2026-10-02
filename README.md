# Learning biological age: metabolic clocks, fair explanations, and a new frontier for biology and mathematics

A teaching notebook on machine learning for biological-age determination, built from two papers:

- **[P1]** Ibáñez de Opakua et al., *Mapping metabolic aging and disease-associated acceleration using an interpretable NMR-based clock* (`MetAgePaper_submitted.pdf`), the MetAge serum-NMR clock and its disease maps.
- **[P2]** Biccari, Ibáñez de Opakua, Mato, Millet, Morales, Zuazua, *Fair feature attribution for multi-output prediction: a Shapley-based perspective* (`SHAP_SIMODS_03.pdf`), the rigidity theorem for multi-output SHAP.

## Audience

Researchers from genetics, metabolomics, clinical biology and mathematics who want an introduction to the challenges and opportunities of machine learning for biological age. The level suits a master's course, a doctoral course or an interdisciplinary colloquium. The notebook follows this path: problem and challenge → mathematical formulation → mathematical goals → mathematics in action (synthetic labs) → results achieved → interpretation for practitioners → take-home messages and research perspectives for each community.

## Three routes

| Route | What to use | Time |
|---|---|---|
| Colloquium | `Bioage_Colloquium.html` (code-free), or the cells tagged `colloquium` | 45–50 min + discussion |
| Master's lecture | All core text of `Bioage_Machine_Learning.ipynb`; predict each experiment before running it | 90–120 min |
| Doctoral workshop | The full notebook, including proofs (`deep-dive` cells), exact SHAP code and exercises | 3–4 h |

`Bioage_Machine_Learning.html` is the complete reading edition. It needs no kernel and contains all figures and the three videos. Keep both HTML files next to the two PDFs so that the local paper links work.

## Setup

Requires Python ≥ 3.10 (tested with 3.12).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # requirements-lock.txt pins the full validation environment
jupyter lab Bioage_Machine_Learning.ipynb
```

Then choose *Restart Kernel and Run All Cells*. The notebook uses only synthetic data (seed 2026) and runs in a few seconds on a laptop. No GPU, SHAP package, data download or FFmpeg is needed. Sliders need `ipywidgets` in a live kernel; without it, each interactive window shows a static figure. JupyterLab's Table of Contents sidebar is the easiest way to navigate.

## Rebuilding

The notebook is authored in Python; do not edit the `.ipynb` by hand.

```bash
export MPLCONFIGDIR=.work/matplotlib
.venv/bin/python tools/build_notebook.py      # 1. author Bioage_Machine_Learning.ipynb from source
.venv/bin/python tools/make_videos.py         # 2. (optional) render the MP4s; needs FFmpeg
.venv/bin/python tools/extract_p1_figure.py   #    (optional) re-crop P1 Fig. 2; needs Poppler's pdftoppm
.venv/bin/python tools/execute_notebook.py    # 3. execute in a fresh kernel, validate, export both HTML editions
```

`execute_notebook.py` stops with an error if any cell fails, and updates `data/source_manifest.json` with cell counts, execution errors and SHA-256 hashes of the two PDFs.

## File map

| Path | Content |
|---|---|
| `Bioage_Machine_Learning.ipynb` | The executed teaching notebook |
| `Bioage_Machine_Learning.html` | Complete reading edition (code in collapsible panels) |
| `Bioage_Colloquium.html` | Code-free colloquium edition (cells tagged `colloquium`) |
| `MetAgePaper_submitted.pdf`, `SHAP_SIMODS_03.pdf` | The two source papers [P1], [P2] |
| `tools/build_notebook.py` | Source of truth: all notebook text and code |
| `tools/make_videos.py` | Renders `assets/videos/01_age_gap.mp4`, `02_collinearity.mp4`, `03_shapley_orders.mp4` |
| `tools/extract_p1_figure.py` | Crops P1 Figure 2 from the PDF into `assets/figures/p1_original_figure2.png` |
| `tools/execute_notebook.py` | Executes, validates and exports |
| `roadmap/Bioage_Research_Roadmap.pdf` (`.tex`, `figures/`) | Research roadmap for collaborators: state of the art, unified framework, open problems, joint projects, paper pipeline. Rebuild with `latexmk -pdf` inside `roadmap/` |
| `assets/figures/` | Figures saved by the notebook, plus the credited P1 Figure 2 excerpt |
| `assets/videos/` | Captioned teaching animations (synthetic) |
| `assets/vendor/mathjax-tex-svg.js` | MathJax 3 bundle, inlined into the HTML for offline equations |
| `data/source_manifest.json` | Paper hashes and validation counts |
| `requirements.txt`, `requirements-lock.txt` | Direct and full pinned dependencies |
