# 9_2_1 Stringabgleich - Konzeptmapping

## Overview
The folder contains the data and scripts used to perform the concept mapping as part of the string matching method (Stringabgleich).

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- scripts

## Scripts
| Script | Description |
|--------|-------------|
| `script_9_2_1_00_run_stringabgleich` | Runs the pipeline |
| `script_9_2_1_01_match_lemma` | Mapping Lemmata |
| `script_9_2_1_01_match_lemma` | Mapping short single-word definitions |
| `script_9_2_1_03_match_long_def` | Mapping long definitions (>1 token) |
| `script_9_2_1_04_match_def_root` | Mapping sentence roots of definitions |
| `script_9_2_1_helpers` | helping fucntions |

## Input
- corpus files:
    - `A_Trinken.tsv`
    - `B_Verwandt.tsv`
    - `C_Zufall.tsv`
    - `A_B_C_gesamt.tsv`
- JSON files Trinken vocabulary:
    - `trinken_vokabular.json`
    - `trinken_vokabular_nur_OT.json` - variant smaller vocabular 

## Output
For each of the input files, an output file is generated in each processing step (5 in total) and a final result file (without intermediate results).

| File | Description |
|--------|-------------|
| `0_XXX_gesplittet.tsv` | corpus with splitted definitions |
| `1_XXX_matches_lemma.tsv` | mapping results after lemma matching |
| `2_XXX_matches_short_def.tsv` | mapping results after matching of single-word definitions |
| `3_XXX_matches_long_def.tsv` | mapping results after matching of long definitions |
| `4_XXX_matches_root.tsv` | mapping results after matching of sentence roots |
|`4_XXX_matches_final.tsv` | compact file with final mapping result |


## Requirements
- Python 3.10.9
- Packages:
    - pandas
    - stanza (version used: 1.10.1)
    - collections
    - os
    - re
    - json
    - csv
    - time
    - ast


## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Depending on which vocabulary you want to use, define the file in the variable "concept_file" ("trinken_vokabular_nur_OT.json" is the reduced variant of "trinken_vokabular.json").
3. Run script_9_2_1_00_run_stringabgleich.py to execute the pipeline.