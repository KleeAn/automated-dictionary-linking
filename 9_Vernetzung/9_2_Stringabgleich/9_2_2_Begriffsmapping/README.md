# 9_2_1 Stringabgleich - Begriffsmapping

## Overview
The folder contains the data and scripts used to perform the term mapping as part of the string matching method (Stringabgleich).

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- scripts

## Scripts
| Script | Description |
|--------|-------------|
| `script_9_2_2_00_run_stringabgleich` | Runs the pipeline |
| `script_9_2_2_01_match_lemma` | Mapping Lemmata |
| `script_9_2_2_01_match_lemma` | Mapping short single-word definitions |
| `script_9_2_2_03_match_long_def` | Mapping long definitions (>1 token) |
| `script_9_2_2_04_match_def_root` | Mapping sentence roots of definitions |
| `script_9_2_2_helpers` | helping fucntions |

## Input
- corpus files:
    - `A_Getränke.tsv`
- JSON files Trinken vocabulary:
    - `trinken_vokabular.json`
    - `trinken_vokabular_nur_OT.json` - variant smaller vocabular 

## Output
In each processing step, an output file is generated (5 in total) and a final result file (without intermediate results).

| File | Description |
|--------|-------------|
| `0_A_Getränke_gesplittet.tsv` | corpus with splitted definitions |
| `1_A_Getränke_matches_lemma.tsv` | mapping results after lemma matching |
| `2_A_Getränke_matches_short_def.tsv` | mapping results after matching of single-word definitions |
| `3_A_Getränke_matches_long_def.tsv` | mapping results after matching of long definitions |
| `4_A_Getränke_matches_root.tsv` | mapping results after matching of sentence roots |
|`4_A_Getränke_matches_final.tsv` | compact file with final mapping result |


## Requirements
- Python 3.10.9
- Packages:
    - pandas
    - stanza 
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
3. Run script_9_2_2_00_run_stringabgleich.py to execute the pipeline.