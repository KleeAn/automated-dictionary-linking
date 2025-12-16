# 8_2_1_1_create_definitionlist

## Overview
The folder contains the data and scripts used for creating a list of definitions and assigned concepts based on the existing corpus entries. 

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output


## Script
| Script | Description |
|--------|-------------|
| `script_8_2_1_1_get_definition_list` | Creates a list of definitions and assigned concepts |


## Input
TSV files with current corpus content: entries from Pälzisches Wörterbuch and entries from the Lothringisches and Elsässisches Wörterbuch obtained via API query.

## Output
For each of the subcorpora A and B: a list with definitions and assigned concepts
- `definitionen_A.tsv`
- `definitionen_B.tsv`


## Requirements
- Python 3.10.9
- Packages:
    - pandas
    - re
    - os
    - glob


## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Run script_8_2_1_1_get_definition_list.py