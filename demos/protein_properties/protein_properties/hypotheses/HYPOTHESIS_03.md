# Hypothesis 03 — Real-World Classification and the Soluble-Domain Dilution Effect

## Status: PENDING

## Background
In Experiment 02, whole-sequence average GRAVY achieved perfect ($100.00\%$) separation on composition-biased synthetic sequences. However, real-world biology is far more complex. Transmembrane proteins often consist of narrow hydrophobic alpha-helical regions (approx. 20–25 residues) flanked by large, water-soluble, charged extracellular or cytoplasmic domains. These soluble domains will "dilute" the average hydropathy, pulling the overall sequence GRAVY score down. Consequently, simple whole-sequence averages may fail on real proteins.

## Hypothesis Statement

**Prediction**:
1. When evaluated on real Human protein sequences downloaded from UniProt (transmembrane vs. cytosolic soluble), a classifier using whole-sequence average GRAVY will exhibit **significant performance degradation** compared to the synthetic baseline (Accuracy dropping from $100\%$ to $\le 85\%$).
2. A biologically informed **sliding-window hydropathy calculator**—specifically, extracting the *maximum average hydropathy* over a sliding window of 19 residues (approximate length of a transmembrane alpha-helix)—will bypass this dilution effect. 
3. A classifier trained on this sliding-window "Max Window GRAVY" feature will significantly outperform the whole-sequence average GRAVY model, restoring classification accuracy to $\ge 90\%$.

**Rationale**:
A sliding-window search checks for the presence of a localized hydrophobic segment capable of spanning a lipid bilayer. This local segment is evolutionary required for transmembrane insertion, regardless of the size or charge of flanking soluble domains. Searching for this local segment is much more robust than averaging the entire sequence.

**Success criteria**:
- Whole-sequence average GRAVY accuracy on UniProt benchmark test split drops significantly below $100\%$ (specifically $\le 85\%$).
- The maximum 19-residue sliding-window GRAVY score ("Max Window GRAVY") is significantly higher for transmembrane proteins than for soluble proteins.
- A model using "Max Window GRAVY" achieves $\ge 90\%$ test accuracy, significantly outperforming the whole-sequence average model (representing $\ge 5\%$ absolute performance gain).

## Experimental Design

- **Script 1 (Download)**: `experiments/02_downloaded/script_03_download_benchmark.py`
  - Retrieves a set of reviewed, curated Human protein sequences from UniProt:
    - 100 reviewed transmembrane proteins (having at least 1 transmembrane region of length $\ge 20$, and excluding extremely complex membrane structures).
    - 100 reviewed soluble cytosolic proteins (having no membrane annotations).
  - Saves the structured sequences to `data/downloaded/uniprot_benchmark.csv`.
- **Script 2 (Classify & Window)**: `experiments/02_downloaded/script_04_benchmark_classification.py`
  - Computes:
    - Whole-sequence Molecular Weight, pI, and GRAVY.
    - Max 19-residue sliding window GRAVY ("Max Window GRAVY").
  - Trains and compares classifiers on a $20\%$ test split.
  - Plots comparative ROC curves and distributions of both whole-sequence and sliding-window features.
- **Data**: Verified UniProt reviewed (Swiss-Prot) Human entries.
- **Key metrics**:
  - Classification accuracy, AUROC, and F1-score for whole-sequence models vs. sliding-window models.
  - Plot of Whole-Sequence GRAVY vs. Max Window GRAVY distributions.

## Dependencies
- UniProt REST API (JSON queries via Python `urllib` or `requests`).
- Pandas, NumPy, Scikit-learn, Matplotlib.
- Modulized sequence property calculators in `scripts/shared/calculators.py`.

## Results

*(To be filled in after the benchmark classification experiment runs — see analysis/ANALYSIS_03.md)*

## Notes
- To prevent network flakiness from failing our pipelines, `script_03` should fall back to a cached local CSV copy of Swiss-Prot sequence fragments if the API is unreachable, or handle timeouts gracefully.
- Window size 19 is chosen as the biophysical standard length of a hydrophobic transmembrane alpha-helix spanning a typical eukaryotic plasma membrane bilayer (~30 Å thickness, ~1.5 Å rise per residue in an alpha helix).
