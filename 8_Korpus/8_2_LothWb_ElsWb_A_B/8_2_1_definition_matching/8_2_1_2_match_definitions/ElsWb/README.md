# 8_2_1_2_match_definitions_ElsWb

## Overview
The folder contains the data and scripts used for matching definitions with ElsWb-XML entries

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `output_edited/` - manually edited output


## Script
| Script | Description |
|--------|-------------|
| `script_8_2_1_2_elswb_compare_defs` | Matches definitions with ElsWb-XML entries. |


## Input
- `ElsWB_Daten/` - XML files Elsässisches Wörterbuch [prepared folder]
- `definitionen_A.tsv` - definitions and assigned concepts (corpus A)
- `definitionen_B.tsv` - definitions and assigned concepts (corpus B)


## Output
For each of the subcorpora A and B: a list of related ElsWb entries found through definition matching
- `abgleich_elswb_A.tsv`
- `abgleich_elswb_B.tsv`

## Output edited
Result files: after manual checking and correction: entries from Elsässisches Wörterbuch found through definition matching, subcorpora A and B: 
- `output_edited/ElsWB_A_Defabgleich.tsv`
- `output_edited/ElsWB_B_Defabgleich.tsv` 


## Requirements
- Python 3.10.9
- Packages:
    - scv
    - html
    - os
    - string
    - re
    - lxml

## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Make sure to store the XML files of Elsässisches Wörterbuch in the folder `input/ElsWB_Daten/`.
3. Run script_8_2_1_2_elswb_compare_defs.py