# Examples

Reference implementations of the scripts referenced from [How to add a dataset](../docs/how-to-add-a-dataset.md). Both files are working code that produced the [Leiberman-Lab_ChemoPADPLStraining2026_Annotated_v1.0](../datasets/Leiberman-Lab_ChemoPADPLStraining2026_Annotated_v1.0/) entry in this registry. They are intended to be **copied and adapted** for a new dataset, not run as-is.

## What's here

- **`build_registry_release.py`** — reads a source manifest CSV + a source annotation CSV + a local PNG cache, computes md5 hashes, joins everything, canonicalises into the registry's standard 8-column metadata schema (plus optional extension columns), splits by a `split` column, and writes `metadata_dev.csv` / `metadata_val.csv` / `metadata_test.csv`, `labels.csv`, `projects.csv`, `class_distribution.csv`, `dataset_sizes.md`, and a templated `README.md` into the output directory.

- **`build_registry_plots.py`** — reads the metadata CSVs that `build_registry_release.py` produced and emits four PNG visualisations into `<dataset-dir>/figs/` (class distribution by split, camera × drug heatmap, lighting × drug heatmap, background × drug heatmap). The catalog page references these from the README so readers can assess the dataset at a glance.

## How to adapt

Both scripts mark every project-specific knob with a `# PROJECT-SPECIFIC:` comment. The expected adaptation pattern:

1. Copy both files into your project's repo (e.g. under a `scripts/` directory).
2. Update the `SAMPLE_NAME_MAP` constant in `build_registry_release.py` to map your source-side API / class names to registry-side lowercase-hyphenated labels.
3. Update the default `--manifest`, `--source-csv`, `--images-root` paths to match your repo layout.
4. Rewrite the README template in `write_readme()` to describe your corpus (the chemopad version mentions HPLC, specific drugs, and project history that won't apply elsewhere).
5. Adjust the extension-column choices in `build_release()` if you ship a different set of annotation columns.
6. For plots: drop or rename the categorical-axis calls in `build_registry_plots.py` if your CSVs don't carry the same extension columns.

Once both scripts run cleanly on your inputs, the rest of the submission procedure is independent of these scripts — generate `croissant.jsonld` via `docs/_scripts/create_croissant.py`, validate, and PR.

## See also

- [How to add a dataset](../docs/how-to-add-a-dataset.md) — the canonical procedural reference.
- [`docs/_scripts/`](../docs/_scripts/) — the registry's own pipeline scripts (Croissant generation, validation, catalog generation). These are run by CI, not by contributors.
- The original chemopad submission used [these exact scripts in their unmodified form](https://github.com/PaperAnalyticalDeviceND/annotated_chemopad) (the source repo's checkout includes them under `scripts/`); the copies here are the public-facing template.
