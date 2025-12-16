# 9_3_4 Zusammenführung

## Overview
The folder contains the scripts and files that were used to merge the predictions of the binary and multiclass classification.

If the binary classification predicts 0 (no affiliation with the field “Drinking” = class "kein_Trinken), the prediction of the multi-class classification is also set to “kein_Trinken".

## Folder Structure

- `input/` - contains input files
- `output/` - contains the output files
- `results_chapter_9.3/` - contains the merged files and mapping predictions that were analysed in chapter 9.3
    - `Komplettes Vokabular/`
    - `Reduziertes Vokabular/`
    - `Vokabular ohne Begriffe/`

The mapping results evaluated in Chapter 9.3 are based on models with the following parameter settings:
- binary classifcation: 10 folds, batch size 32, 3 epochs
- multiclass classification: 10 folds, batch size 32, 4 epochs

## Scripts
| Script | Description |
|--------|-------------|
| `script_9_3_4_merge_binary_multiclass` | Merges predictions of binary and multiclass classification |


## Input
- corpus file with binary classification predictions:
    - `A_B_C_gesamt_binär_10f_32bs_3e.tsv`
- files for subcorpora with multiclass classification predictions:
    - `A_Trinken_multiclass_10f_32bs_4e.tsv`
    - `B_Verwandt_multiclass_10f_32bs_4e.tsv`
    - `C_Zufall_multiclass_10f_32bs_4e.tsv`


## Output

- The script generates one output file for each subcorpus file with merged predictions, e.g. `A_Trinken_10f_32bs_4e_final.tsv`.

## Requirements
Ensure Python 3.10.11 and required packages are installed.

- Python 3.10.11
- Packages:
    - pandas
    - pathlib
