#!/usr/bin/env python3
"""Worked example: emit `figs/` analysis plots for a registry release directory.

Reads the metadata CSVs produced by `build_registry_release.py` and writes four
PNGs into `<dataset-dir>/figs/` that the catalog page references from the
README:

    class_distribution.png       - per-class image counts split by dev/val/test
    camera_drug_heatmap.png      - upstream camera string × drug class
    lighting_drug_heatmap.png    - lighting × drug class (annotation-only column)
    background_drug_heatmap.png  - background × drug class (annotation-only column)

WHAT YOU NEED TO ADAPT for your dataset:

- The class-distribution and camera × drug plots assume the standard 8-column
  metadata schema and work without changes.
- The lighting × drug and background × drug plots assume your CSVs carry the
  matching extension columns (`lighting`, `background`). Drop the calls for
  any extension columns you don't ship, or substitute your own categorical axes.
- The visual style (size, colormap, label rotation) is tuned for ~10 classes
  and 3-bucket categorical axes. For a 20-class dataset you may want larger
  figure sizes.

See `docs/how-to-add-a-dataset.html` for the canonical procedure this script
fits into.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SPLIT_FILES = {
    "dev": "metadata_dev.csv",
    "val": "metadata_val.csv",
    "test": "metadata_test.csv",
}


def load_combined(dataset_dir: Path) -> pd.DataFrame:
    parts = []
    for split, filename in SPLIT_FILES.items():
        df = pd.read_csv(dataset_dir / filename)
        df["split"] = split
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def plot_class_distribution(df: pd.DataFrame, out_path: Path) -> None:
    counts = df.groupby(["sample_name", "split"]).size().unstack(fill_value=0)
    counts = counts.reindex(columns=["dev", "val", "test"]).fillna(0).astype(int)
    counts["total"] = counts.sum(axis=1)
    counts = counts.sort_values("total", ascending=True)
    counts = counts.drop(columns="total")

    fig, ax = plt.subplots(figsize=(8, 6))
    bottoms = np.zeros(len(counts))
    colors = {"dev": "#4C72B0", "val": "#DD8452", "test": "#55A467"}
    for col in ["dev", "val", "test"]:
        ax.barh(counts.index, counts[col], left=bottoms, label=col, color=colors[col])
        bottoms += counts[col].values
    ax.set_xlabel("Image count")
    ax.set_title("Class distribution by split")
    ax.legend(loc="lower right", title="split")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_categorical_heatmap(df: pd.DataFrame, x_col: str, title: str, out_path: Path) -> None:
    pivot = pd.crosstab(df["sample_name"], df[x_col])
    pivot = pivot.reindex(sorted(pivot.index))
    fig, ax = plt.subplots(figsize=(max(6, 0.9 * len(pivot.columns) + 4), 0.55 * len(pivot.index) + 2))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlGnBu")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = int(pivot.values[i, j])
            color = "white" if v > pivot.values.max() / 2 else "black"
            ax.text(j, i, str(v), ha="center", va="center", color=color, fontsize=9)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label="Image count")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, required=True)
    args = parser.parse_args()
    dataset_dir: Path = args.dataset_dir
    figs_dir = dataset_dir / "figs"
    figs_dir.mkdir(exist_ok=True)

    df = load_combined(dataset_dir)
    print(f"Loaded {len(df)} rows across {df['split'].nunique()} splits")

    plot_class_distribution(df, figs_dir / "class_distribution.png")
    print(f"wrote {figs_dir / 'class_distribution.png'}")

    plot_categorical_heatmap(df, "camera_type_1",
                             "Upstream camera × drug class", figs_dir / "camera_drug_heatmap.png")
    print(f"wrote {figs_dir / 'camera_drug_heatmap.png'}")

    plot_categorical_heatmap(df, "lighting",
                             "Lighting × drug class (annotation column)",
                             figs_dir / "lighting_drug_heatmap.png")
    print(f"wrote {figs_dir / 'lighting_drug_heatmap.png'}")

    plot_categorical_heatmap(df, "background",
                             "Background × drug class (annotation column)",
                             figs_dir / "background_drug_heatmap.png")
    print(f"wrote {figs_dir / 'background_drug_heatmap.png'}")


if __name__ == "__main__":
    main()
