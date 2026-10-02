"""Render original, captioned teaching animations (FFmpeg is required only to rebuild them).

Captions are drawn in a strip above the bottom quarter of each frame, so the HTML5 video
control bar never covers them. The game used in video 3 must match the conditional
Gaussian game of the notebook's rigidity-theorem lab (B, sigma, x below). Videos are numbered
in reading order: 1 age gap (section 6), 2 collinearity (section 7), 3 Shapley orders (section 9).
"""
from pathlib import Path
import os
import sys
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".work" / "matplotlib"))
import itertools
import shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, writers

for candidate in [shutil.which("ffmpeg"), "/usr/local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]:
    if candidate and Path(candidate).exists():
        plt.rcParams["animation.ffmpeg_path"] = candidate
        break
if not writers.is_available("ffmpeg"):
    sys.exit("FFmpeg not found. Install it (e.g. `brew install ffmpeg`) or put it on PATH. "
             "The notebook itself runs without FFmpeg.")

OUT = ROOT / "assets" / "videos"
OUT.mkdir(parents=True, exist_ok=True)
TEAL, CORAL, NAVY, GOLD, GREY = "#16877c", "#d8614b", "#183b56", "#be8725", "#7d8b93"
CAPTION_BOX = {"facecolor": "#eef6f7", "edgecolor": "none", "pad": 6}
plt.rcParams.update({"font.size": 12, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold"})


def new_writer(fps):
    return FFMpegWriter(fps=fps, codec="libx264", bitrate=900,
                        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])


# ------------------------------------------------------------------ video 1
fig, axes = plt.subplots(1, 2, figsize=(10, 5.6))
fig.subplots_adjust(left=.09, right=.96, bottom=.36, top=.77, wspace=.27)
a = np.linspace(20, 85, 100)
line, = axes[0].plot(a, a, color=TEAL, lw=3)
axes[0].plot(a, a, "--", color=NAVY, alpha=.7)
gap, = axes[1].plot(a, np.zeros_like(a), color=CORAL, lw=3)
axes[1].axhline(0, color=NAVY, ls="--")
axes[0].set(xlabel="Chronological age (years)", ylabel="Predicted age (years)",
            ylim=(15, 90), title="A shrinking prediction range")
axes[1].set(xlabel="Chronological age (years)", ylabel="Raw age gap (years)",
            ylim=(-35, 35), title="An age gap without disease")
fig.text(.05, .94, "01 / WHY AGE GAPS NEED A REFERENCE", color=NAVY, weight="bold", fontsize=18)
subtitle = fig.text(.5, .17, "", ha="center", va="center", color=NAVY, fontsize=12, bbox=CAPTION_BOX)
slope_text = fig.text(.5, .84, "", ha="center", color=TEAL, weight="bold")
writer = new_writer(10)
with writer.saving(fig, str(OUT / "01_age_gap.mp4"), dpi=110):
    for slope in np.r_[np.ones(20), np.linspace(1, .15, 100), np.full(30, .15)]:
        prediction = 52.5 + slope * (a - 52.5)
        line.set_ydata(prediction)
        gap.set_ydata(prediction - a)
        slope_text.set_text(f"Prediction = 52.5 + {slope:.2f} × (age − 52.5)")
        subtitle.set_text("SYNTHETIC CONSTRUCTION · No disease or intervention is introduced.\n"
                          "As predictions shrink toward the mean, the raw gap acquires an age trend.")
        writer.grab_frame()
plt.close(fig)
print("Rendered 01_age_gap.mp4", flush=True)

# ------------------------------------------------------------------ video 3
B = np.array([6., 4., -3.])                      # age-like column of the notebook's B
sigma = np.array([[1., .8, .2], [.8, 1., .1], [.2, .1, 1.]])
x = np.array([1.2, .8, -.5])
values = np.zeros(8)
for mask in range(1, 8):
    S = [j for j in range(3) if mask & (1 << j)]
    mean = sigma[:, S] @ np.linalg.solve(sigma[np.ix_(S, S)], x[S])
    values[mask] = mean @ B
names = ["Inflammation", "Renal", "Energy"]
colors = [NAVY, GOLD, GREY]                      # identity colours, not sign colours
fig, axes = plt.subplots(1, 2, figsize=(10, 5.6))
fig.subplots_adjust(left=.08, right=.97, bottom=.38, top=.76, wspace=.30)
bars = axes[0].bar(names, [0., 0., 0.], color=colors)
means = axes[1].bar(names, [0., 0., 0.], color=colors)
labels = [[ax.text(i, 0, "", ha="center", va="bottom", fontsize=11, color=NAVY) for i in range(3)]
          for ax in axes]
for ax in axes:
    ax.set_ylim(-3, 14)
    ax.axhline(0, color=NAVY, lw=.7)
    ax.set_ylabel("Age-like contribution (years)")
axes[0].set_title("Allocation in the current order")
axes[1].set_title("Average of completed orders")
fig.text(.05, .94, "03 / SHAPLEY VALUES AVERAGE OVER ORDERS", color=NAVY, weight="bold", fontsize=17)
order_text = fig.text(.5, .84, "", ha="center", color=TEAL, weight="bold")
subtitle = fig.text(.5, .17, "", ha="center", va="center", color=NAVY, fontsize=11, bbox=CAPTION_BOX)


def set_bars(container, texts, heights):
    for bar, text, value in zip(container, texts, heights):
        bar.set_height(value)
        text.set_position((bar.get_x() + bar.get_width() / 2, max(value, 0) + .2))
        text.set_text(f"{value:.2f}" if value else "")


allocations = []
writer = new_writer(8)
with writer.saving(fig, str(OUT / "03_shapley_orders.mp4"), dpi=110):
    for number, order in enumerate(itertools.permutations(range(3)), 1):
        allocation = np.zeros(3)
        mask = 0
        order_text.set_text(f"Order {number}/6: " + " → ".join(names[j] for j in order))
        for stage, j in enumerate(order, 1):
            new_mask = mask | (1 << j)
            allocation[j] = values[new_mask] - values[mask]
            mask = new_mask
            set_bars(bars, labels[0], allocation)
            if stage == 3:
                allocations.append(allocation.copy())
                set_bars(means, labels[1], np.mean(allocations, axis=0))
            subtitle.set_text(f"SYNTHETIC CONDITIONAL GAME · Reveal {names[j].lower()}.\n"
                              f"Current coalition explains {values[mask]:.2f} years above baseline; "
                              f"the full prediction difference is {values[-1]:.2f} years.")
            for _ in range(16):
                writer.grab_frame()
    exact = np.mean(allocations, axis=0)
    subtitle.set_text("After all six orders the average is the exact Shapley allocation: "
                      + " / ".join(f"{v:.2f}" for v in exact) + " years\n"
                      "(the age column of the table in the rigidity lab). "
                      "Repeat for each output, in that output's units.")
    for _ in range(48):
        writer.grab_frame()
plt.close(fig)
print("Rendered 03_shapley_orders.mp4 · exact allocation", np.round(exact, 3), flush=True)

# ------------------------------------------------------------------ video 2
rng = np.random.default_rng(2029)
n = 350
z1 = rng.normal(size=n)
Z = np.column_stack([z1, z1 + rng.normal(0, .015, n)])
Z = (Z - Z.mean(0)) / Z.std(0)
y = 3 * z1 + rng.normal(0, .8, n)
y = y - y.mean()
boots = [rng.integers(0, n, n) for _ in range(120)]
fig, axes = plt.subplots(1, 2, figsize=(10, 5.6))
fig.subplots_adjust(left=.09, right=.96, bottom=.38, top=.77, wspace=.30)
cloud = axes[0].scatter([], [], s=16, alpha=.55, color=CORAL)
axes[0].plot([-7, 10], [10, -7], ":", color=GREY, lw=1)
axes[0].text(-6.5, -7.2, "dotted: weight 1 + weight 2 ≈ 3", color=GREY, fontsize=10)
axes[0].set(xlim=(-7, 11), ylim=(-8, 11), xlabel="Weight on marker 1", ylabel="Weight on marker 2",
            title="Credit moves between twins")
hist_bins = np.linspace(2.6, 3.3, 29)
axes[1].set(xlim=(2.6, 3.3), ylim=(0, 40), xlabel="Prediction at the typical profile (1, 1)",
            ylabel="Bootstrap replicates", title="…the prediction does not")
fig.text(.05, .94, "02 / COLLINEARITY: CREDIT MOVES, PREDICTION STAYS", color=NAVY, weight="bold",
         fontsize=16)
lam_text = fig.text(.5, .84, "", ha="center", color=TEAL, weight="bold")
subtitle = fig.text(.5, .17, "", ha="center", va="center", color=NAVY, fontsize=11, bbox=CAPTION_BOX)
writer = new_writer(10)
with writer.saving(fig, str(OUT / "02_collinearity.mp4"), dpi=110):
    for lam in np.r_[np.zeros(15), np.geomspace(1e-3, 30, 90), np.full(25, 30.)]:
        betas = np.array([np.linalg.solve(Z[b].T @ Z[b] + lam * np.eye(2), Z[b].T @ y[b]) for b in boots])
        cloud.set_offsets(betas)
        for patch in list(axes[1].patches):
            patch.remove()
        axes[1].hist(betas.sum(1), bins=hist_bins, color=TEAL, alpha=.8)
        kappa = np.linalg.cond(Z.T @ Z + lam * np.eye(2))
        lam_text.set_text(f"ridge λ = {lam:.3g}  ·  cond(ZᵀZ + λI) = {kappa:,.0f}  (= κ(Z)² at λ = 0)")
        subtitle.set_text("SYNTHETIC · two almost identical markers, 120 bootstrap refits.\n"
                          "As λ grows the weights settle on equal shares; the prediction barely moves (ridge adds a small bias).")
        writer.grab_frame()
plt.close(fig)
print("Rendered 02_collinearity.mp4", flush=True)
