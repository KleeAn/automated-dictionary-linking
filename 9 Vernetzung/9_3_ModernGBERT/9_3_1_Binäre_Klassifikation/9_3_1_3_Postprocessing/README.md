# 9_3_1_3 Binäre Klassifikation - Postprocessing

## Overview
The folder contains the scripts used to postprocess the concept predictions of the binary classification of lemma-meaning pairs.

The predictions for the individual test folds from the cross-validation are merged into a single file.

Special treatment for fine-tuning with smaller training datasets (1 fold for training, the rest for testing = multiple predictions for each data point): Resolving duplicates. If there are different predictions per data point, the most frequent label is preferred. If several labels occur with equal frequency, one is selected at random.


## Scripts
| Script | Description |
|--------|-------------|
| `script_9_3_1_3_01_merge_files_binary_large` | Merging for finetuning with large training set |
| `script_9_3_1_3_02_merge_files_binary_small` | Merging for finetuning with small training set |

## Input
The input is expected to be TSV files generated as output during the fine-tuning of the ModernGBERT model for binary classification (see e.g. `9_3_1_1_großes_Trainingsset/results/10f_32bs_3e/`).

## Output
The scripts generate a single output file containing one prediction for each corpus entry.

The generated file used in Chapter 9 (binary classifcation with parameters 10f, 2bs, 4e) is located in the corresponding result folder `9_3_ModernGBERT\9_3_1_Binäre_Klassifikation\9_3_1_1_großes_Trainingsset\results\10f_32bs_4e\A_B_C_gesamt_binär_10f_32bs_4e.tsv'.

## Requirements
- Python 3.10.11
- Packages:
    - pandas
    - glob
    - os
    - random

## How to Run
1. Ensure Python 3.10.11 and required packages are installed.
2. Ensure that the script and the files to be merged are located in the same folder.
3. Run the script.