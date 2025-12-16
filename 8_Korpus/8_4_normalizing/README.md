# 8_4_normalizing

## Overview
The folder contains the data and scripts used for normalizing the corpus entries from different dictionary sources.

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output

## Script
| Script | Description |
|--------|-------------|
| `script_8_4_normalize.py` | Normalizes corpus entries (especially lemma and definition) |


## Input
- `A_Trinken.tsv` - complete subcorpus A
- `B_Verwandt.tsv` - complete subcorpus B
- `C_Zufall.tsv` - complete subcorpus C

## Output
- `A_Trinken_normalized.tsv` - normalized subcorpus A
- `B_Verwandt_normalized.tsv` - normalized subcorpus B
- `C_Zufall_normalized.tsv` - normalized subcorpus C

## Requirements
- Python 3.10.9
- Packages:
    - pandas
    - os
    - re


## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Run script_8_4_normalize.py