#!/usr/bin/env python3
"""Worked example: build pad_dataset_registry release artefacts for a PAD dataset.

This script is the working template used to produce the entry
`Leiberman-Lab_ChemoPADPLStraining2026_Annotated_v1.0`. It is shipped in this
repo as a reference implementation that a new contributor can copy and adapt.

What it does:

- Reads a source manifest CSV + a source annotation CSV (for raw camera string
  and any annotation-only columns) + a local image cache.
- Joins them on the per-image identifier, canonicalises into the registry's
  standard 8-column metadata schema (id, sample_id, sample_name, quantity,
  camera_type_1, url, hashlib_md5, image_name), plus optional extension
  columns.
- Computes md5 hashes from the local PNG cache.
- Splits into per-split metadata CSVs by a `split` column on the manifest.
- Writes `labels.csv`, `projects.csv`, `class_distribution.csv`,
  `dataset_sizes.md`, and a templated `README.md`.

The `croissant.jsonld` is generated separately via `docs/_scripts/create_croissant.py`
once this scaffold is in place. See `docs/how-to-add-a-dataset.html` for the
full procedure.

WHAT YOU NEED TO ADAPT for your dataset:

- PROJECT-SPECIFIC: `SAMPLE_NAME_MAP` (API → registry label, drug-set-dependent)
- PROJECT-SPECIFIC: default `--manifest`, `--source-csv`, `--images-root` paths
- PROJECT-SPECIFIC: column name constants (`LIGHTING_COL`, `MG_CONC_COL`) and
  the extension-column choices in `build_release`
- PROJECT-SPECIFIC: the README template in `write_readme` (corpus stats, what's
  distinctive about the dataset, the citation block)
- PROJECT-SPECIFIC: the `projects.csv` value in `build_release`

The skeleton (md5 / join / canonicalise / split / write) generalises across
PAD datasets; the project-specific knobs above are flagged inline in the code
with `# PROJECT-SPECIFIC:` comments.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

# --- column-name conventions ---

# PROJECT-SPECIFIC: source-side column names. Match what's in your manifest.
LIGHTING_COL = "Lighting (lightbox, benchtop, benchtop dark)"
MG_CONC_COL = "mg concentration (w/w mg/mg or w/v mg/mL)"

# PROJECT-SPECIFIC: source-API → registry-label mapping.
# Registry uses lowercase, hyphen-separated drug names.
# The convention drops the "(oral)" suffix for Hydroxyurea but keeps "-oral"
# for Methotrexate. Matches the existing
# Leiberman-Lab_ChemoPADNNtraining2024_Partial-Drug-Set_v1.0 entry.
# When adapting: build a map of your source-CSV API names to registry labels.
SAMPLE_NAME_MAP = {
    "Blank": "blank",
    "Cisplatin": "cisplatin",
    "Doxorubicin": "doxorubicin",
    "Hydroxyurea (oral)": "hydroxyurea",
    "Lactose": "lactose",
    "Mesna": "mesna",
    "Methotrexate": "mtx-injectable",
    "Methotrexate (oral)": "mtx-oral",
    "Oxaliplatin 2mg/mL": "oxaliplatin-2-mg-ml",
    "Oxaliplatin 5mg/mL": "oxaliplatin-5-mg-ml",
}

SPLIT_TO_FILENAME = {
    "train": "metadata_dev.csv",
    "val": "metadata_val.csv",
    "test": "metadata_test.csv",
}


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_release(manifest_path: Path, source_csv: Path, images_root: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading manifest: {manifest_path}")
    m = pd.read_csv(manifest_path)
    print(f"  {len(m)} rows, {m['PAD#'].nunique()} unique PAD#s")

    print(f"Reading source CSV for raw camera + missing_card: {source_csv}")
    src = pd.read_csv(source_csv)
    src_cols = src[["matched_id", "matched_camera_type_1", "missing_card"]].copy()
    src_cols["matched_id"] = pd.to_numeric(src_cols["matched_id"], errors="coerce").astype("Int64")
    src_cols = src_cols.dropna(subset=["matched_id"]).drop_duplicates("matched_id")
    print(f"  {len(src_cols)} unique matched_id entries")

    print("Joining manifest with source on matched_id_int = matched_id...")
    m = m.merge(src_cols, left_on="matched_id_int", right_on="matched_id", how="left")
    missing = m["matched_camera_type_1"].isna().sum()
    print(f"  rows missing raw camera after join: {missing}")

    print(f"Computing md5 over {len(m)} cached PNGs...")
    hashes = []
    skipped = 0
    for i, row in enumerate(m.itertuples(index=False)):
        local_path = Path(row.local_image_path)
        if not local_path.is_absolute():
            local_path = images_root.parent.parent / local_path
        if local_path.exists():
            hashes.append(md5_of(local_path))
        else:
            hashes.append("")
            skipped += 1
        if (i + 1) % 500 == 0:
            print(f"  hashed {i + 1}/{len(m)}")
    m["hashlib_md5"] = hashes
    print(f"  skipped {skipped} rows (no cached PNG)")

    print("Transforming columns into the registry schema...")
    out = pd.DataFrame({
        "id": m["matched_id_int"].astype("Int64"),
        "sample_id": m["PAD#"].astype("Int64"),
        "sample_name": m["API"].map(SAMPLE_NAME_MAP),
        "quantity": m["% Conc"].round(1),
        "camera_type_1": m["matched_camera_type_1"],
        "url": m["matched_url"],
        "hashlib_md5": m["hashlib_md5"],
        # extended columns (right of the standard schema)
        "camera_bucket": m["Camera"],
        "lighting": m[LIGHTING_COL],
        "background": m["black/white background"],
        "status": m["status"],
        "missing_card": m["missing_card"],
    })
    # Lactose and Blank are 0% drug by definition; match the prior Lieberman convention.
    is_zero = out["sample_name"].isin(["lactose", "blank"])
    out.loc[is_zero & out["quantity"].isna(), "quantity"] = 0
    # Encode quantity as integer if it has no fractional part, else keep the decimal.
    def _qfmt(q):
        if pd.isna(q):
            return ""
        q = float(q)
        return str(int(q)) if q.is_integer() else f"{q:.1f}"
    out["quantity_str"] = out["quantity"].apply(_qfmt)
    out["image_name"] = (
        out["id"].astype("Int64").astype("string") + "__"
        + out["sample_id"].astype("Int64").astype("string") + "__"
        + out["sample_name"].astype("string") + "__"
        + out["quantity_str"] + ".png"
    )
    out = out.drop(columns=["quantity_str"])
    # standard schema order followed by extensions
    out = out[[
        "id", "sample_id", "sample_name", "quantity", "camera_type_1",
        "url", "hashlib_md5", "image_name",
        "camera_bucket", "lighting", "background", "status", "missing_card",
    ]]
    unmapped = out["sample_name"].isna().sum()
    if unmapped:
        raise SystemExit(f"unmapped API labels: {unmapped} rows. SAMPLE_NAME_MAP is incomplete.")

    print("Writing per-split metadata CSVs...")
    splits_seen = {}
    for split_name, filename in SPLIT_TO_FILENAME.items():
        mask = m["split"] == split_name
        n_split = int(mask.sum())
        splits_seen[split_name] = n_split
        out_path = out_dir / filename
        out.loc[mask].to_csv(out_path, index=False)
        print(f"  {filename}: {n_split} rows")
    total = sum(splits_seen.values())
    if total != len(m):
        raise SystemExit(f"split mismatch: manifest has {len(m)} rows but splits sum to {total}")

    print("Writing labels.csv (alphabetical, matching the prior Lieberman convention)...")
    labels = sorted(SAMPLE_NAME_MAP.values())
    (out_dir / "labels.csv").write_text(",".join(labels) + "\n")

    print("Writing projects.csv...")
    # PROJECT-SPECIFIC: replace with your project family name.
    (out_dir / "projects.csv").write_text("ChemoPADPLStraining2026\n")

    print("Writing class_distribution.csv and dataset_sizes.md...")
    write_class_distribution(out, out_dir, splits_seen)

    print("Writing README.md...")
    write_readme(out, out_dir, splits_seen)

    print(f"Done. Output: {out_dir}")


def write_class_distribution(out: pd.DataFrame, out_dir: Path, splits_seen: dict[str, int]) -> None:
    dev = out[out.index.isin(out.index[: splits_seen["train"]])]  # rebuilt below using marker
    # The cleanest approach: derive counts directly from the per-split CSVs we just wrote.
    counts = {}
    for split_name, filename in SPLIT_TO_FILENAME.items():
        sub = pd.read_csv(out_dir / filename)
        counts[split_name] = sub["sample_name"].value_counts()
    rows = []
    for cls in sorted(set().union(*[c.index for c in counts.values()])):
        row = {
            "class": cls,
            "#dev": int(counts["train"].get(cls, 0)),
            "#val": int(counts["val"].get(cls, 0)),
            "#test": int(counts["test"].get(cls, 0)),
        }
        row["#total"] = row["#dev"] + row["#val"] + row["#test"]
        rows.append(row)
    dist = pd.DataFrame(rows)
    dist = dist.sort_values("#total", ascending=False).reset_index(drop=True)
    total_row = {
        "class": "#total",
        "#dev": int(dist["#dev"].sum()),
        "#val": int(dist["#val"].sum()),
        "#test": int(dist["#test"].sum()),
        "#total": int(dist["#total"].sum()),
    }
    dist_with_total = pd.concat([dist, pd.DataFrame([total_row])], ignore_index=True)
    dist_with_total.to_csv(out_dir / "class_distribution.csv", index=False)

    n_unique_pads = {}
    for split_name, filename in SPLIT_TO_FILENAME.items():
        sub = pd.read_csv(out_dir / filename)
        n_unique_pads[split_name] = sub["sample_id"].nunique()

    lines = [
        "### Dataset Sizes",
        "",
        "| Set | All Images | Unique Sample IDs |",
        "|-----|------------|------------------|",
        f"| Train/Val | {splits_seen['train'] + splits_seen['val']} | {n_unique_pads['train'] + n_unique_pads['val']} |",
        f"| Test | {splits_seen['test']} | {n_unique_pads['test']} |",
        f"| Total | {sum(splits_seen.values())} | {sum(n_unique_pads.values())} |",
    ]
    (out_dir / "dataset_sizes.md").write_text("\n".join(lines) + "\n")


def write_readme(out: pd.DataFrame, out_dir: Path, splits_seen: dict[str, int]) -> None:
    total = sum(splits_seen.values())
    n_pads = out["sample_id"].nunique()

    n_pads_per_split = {}
    for split_name, filename in SPLIT_TO_FILENAME.items():
        sub = pd.read_csv(out_dir / filename)
        n_pads_per_split[split_name] = sub["sample_id"].nunique()

    dist = pd.read_csv(out_dir / "class_distribution.csv")

    rows_md = [
        "|    | class               |   #dev |   #val |   #test |   #total |",
        "|:---|:--------------------|-------:|-------:|--------:|---------:|",
    ]
    for i, r in dist.iloc[:-1].iterrows():
        rows_md.append(
            f"| {i}  | {r['class']:<20s}|  {int(r['#dev']):>5d} |  {int(r['#val']):>5d} |   {int(r['#test']):>5d} |    {int(r['#total']):>5d} |"
        )
    tot = dist.iloc[-1]
    rows_md.append(
        f"| -  | #total              |  {int(tot['#dev']):>5d} |  {int(tot['#val']):>5d} |   {int(tot['#test']):>5d} |    {int(tot['#total']):>5d} |"
    )
    class_table = "\n".join(rows_md)

    # PROJECT-SPECIFIC: rewrite the whole README template for your dataset.
    # The block below is the chemopad-flavoured original (mentions HPLC, the
    # specific drugs, the project history). For a new dataset, replace it
    # with text that describes your corpus, citation, and what's distinctive.
    readme = f"""# `ChemoPADPLStraining2026_Annotated` Dataset

The annotated successor to the `Leiberman-Lab_ChemoPADNNtraining2024_Partial-Drug-Set_v1.0` release. The project label is updated to `ChemoPADPLStraining2026` because (a) the predominant downstream method on this corpus has been per-drug PLS concentration regression and PLS-DA classification, with neural-network experiments filed as comparison points rather than the primary modelling line, and (b) the annotation pass and HPLC re-labelling completed in 2026. This version is a hand-curated extension of the original ChemoPAD corpus and ships HPLC-measured concentration labels alongside annotation-specific quality flags (Lighting, Background, upstream `status`, `missing_card`).

## Description

This dataset consists of {total} card images from {n_pads} unique samples (PAD#s), split deterministically by PAD# into development, validation, and test sets so that no card is shared between splits. The Active Pharmaceutical Ingredients (APIs) cover eight chemotherapy drugs plus Lactose and Blank, at continuous concentrations measured by HPLC (not the nominal 33 / 66 / 100 % buckets of the prior release).

### Data Distribution

| Split | Images | Unique PAD#s |
|---|---:|---:|
| Development (train) | {splits_seen['train']} | {n_pads_per_split['train']} |
| Validation | {splits_seen['val']} | {n_pads_per_split['val']} |
| Test | {splits_seen['test']} | {n_pads_per_split['test']} |
| **Total** | **{total}** | **{n_pads}** |

#### Class Distribution

{class_table}

#### Dataset Visualizations

**Class Distribution by Split**
![Class distribution by split](./figs/class_distribution.png)

**Upstream Camera × Drug**
![Camera vs drug heatmap](./figs/camera_drug_heatmap.png)

Coverage gap visible: `HMD Global Nokia 2.3` only carries Hydroxyurea (and a small Mesna slice), so any per-Nokia analysis is constrained to those two drugs. `unknown` is the bucket for the Methotrexate variants. iPad and Pixel 3a cover the rest.

**Lighting × Drug** (annotation column)
![Lighting vs drug heatmap](./figs/lighting_drug_heatmap.png)

Lighting (`lightbox`, `benchtop`, `no light`) is balanced for the four largest drug classes; lower-count drugs still have all three lightings represented.

**Background × Drug** (annotation column)
![Background vs drug heatmap](./figs/background_drug_heatmap.png)

Background (`black`, `white`) is imbalanced for several drugs: Cisplatin and Mesna lean white; Oxaliplatin 5 mg/mL leans slightly black. Useful for stratified evaluations.

### What's annotated

Each row carries the standard registry columns (`id, sample_id, sample_name, quantity, camera_type_1, url, hashlib_md5, image_name`) plus five extended columns that are the value proposition of this release:

| Column | Values | Source |
|---|---|---|
| `camera_bucket` | `ipad`, `pixel`, `nokia` | analyst-merged 3-bucket relabel of the upstream `camera_type_1` |
| `lighting` | `lightbox`, `benchtop`, `no light` | annotator-recorded capture lighting |
| `background` | `black`, `white` | annotator-recorded background colour |
| `status` | `valid`, `invalid` | joined from upstream `unmatched_cards_export.csv` |
| `missing_card` | `True`, `False` | annotator flag for cards the analyst could not visually review |

Strict-schema consumers ignore unknown columns; tools that know them can use them as capture-condition covariates or quality filters.

### What changed vs the prior `Partial-Drug-Set_v1.0` release

- **+1,206 unique cards added** (3,714 vs 2,847) and **+154 unique PAD#s** (646 vs 492) through the annotation effort.
- **HPLC-measured concentrations**. The `quantity` column carries HPLC ground-truth concentrations (rescaled per API to % of nominal strength). See the per-API scale-factor audit at `data/HPLC/per_api_scale_factors.csv` in the source repo for the derivation.
- **PAD#-grouped split discipline.** The deterministic 60 / 25 / 15 train / val / test split groups by physical card (PAD#); no card leaks across splits.
- **Camera bucketing.** Upstream camera strings are merged into three buckets (`ipad`, `pixel`, `nokia`) by the analyst; the raw upstream string is preserved in `camera_type_1`.
- **Explicit quality flags** (`status`, `missing_card`) and capture-condition covariates (`lighting`, `background`) for stratified evaluations.

### Source manifest

`data/splits/manifest.csv` (md5 `6da9b45dae27fd75e278adbaa608e808`) is the authoritative input. The deterministic split is reproducible.

### Directory Structure

```markdown
datasets/Leiberman-Lab_ChemoPADPLStraining2026_Annotated_v1.0/
├── README.md
├── class_distribution.csv
├── croissant.jsonld
├── dataset_sizes.md
├── figs/
│   ├── class_distribution.png
│   ├── camera_drug_heatmap.png
│   ├── lighting_drug_heatmap.png
│   └── background_drug_heatmap.png
├── labels.csv
├── metadata_dev.csv
├── metadata_test.csv
├── metadata_val.csv
└── projects.csv
```

### Citation

If you use this dataset, please cite:

> Wilfinger, M., Mike, M., Sweet, C. *Annotated ChemoPAD NN Training Dataset, v1.0.* Lieberman Lab, University of Notre Dame. <https://github.com/PaperAnalyticalDeviceND/annotated_chemopad>

### License

Apache License 2.0 (consistent with the parent registry).
"""
    (out_dir / "README.md").write_text(readme)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, default=Path("data/splits/manifest.csv"))
    p.add_argument("--source-csv", type=Path, default=Path("data/chemopad_export_20260522_144840.csv"))
    p.add_argument("--images-root", type=Path, default=Path("data/images"))
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()
    build_release(args.manifest, args.source_csv, args.images_root, args.out_dir)


if __name__ == "__main__":
    main()
