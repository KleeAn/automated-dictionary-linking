# 8_2_1_2_match_definitions_LothWb

## Overview
The folder contains the data and scripts used for matching definitions with LothWb-XML entries

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `output_edited/` - manually edited output


## Script
| Script | Description |
|--------|-------------|
| `script_8_2_1_2_lothwb_compare_defs` | Matches definitions with ElsWb-XML entries. |


## Input
- `LothWB_Daten/` - XML files Lothringisches Wörterbuch [prepared folder]
- `definitionen_A.tsv` - definitions and assigned concepts (corpus A)
- `definitionen_B.tsv` - definitions and assigned concepts (corpus B)


## Output
For each of the subcorpora A and B: a list of related ElsWb entries found through definition matching
- `abgleich_lothwb_A.tsv`
- `abgleich_lothwb_B.tsv`

## Output edited
Result files: after manual checking and correction: entries from Elsässisches Wörterbuch found through definition matching, subcorpora A and B: 
- `output_edited/LothWB_A_Defabgleich.tsv`
- `output_edited/LothWB_B_Defabgleich.tsv` 


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
1. Ensure Python 3.10.9 and required packages are installed.
2. Make sure to store the XML files of Lothringisches Wörterbuch in the folder `input/LothWB_Daten/`.
3. Run script_8_2_1_2_lothwb_compare_defs.py