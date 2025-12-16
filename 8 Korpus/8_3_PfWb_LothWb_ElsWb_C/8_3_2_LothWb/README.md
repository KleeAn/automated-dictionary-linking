# 8_3_3_zufallsauswahl_lothwb

## Overview
The folder contains the data and scripts used for extracting random entries from LothWb-TEI-XML files (Lothringisches Wörterbuch).

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `output_edited/` - manually edited output

## Script
| Script | Description |
|--------|-------------|
| `script_8_3_2_zufallsauswahl_lothwb` | Extracts random entries from LothWb |


## Input
- `LothWb_Daten/` - XML files Lothringisches Wörterbuch [prepared folder]

## Output
- `LothWb_C_Zufall.tsv` - Random LothWb entries for subcorpus C


## Output edited
Result file: After manual checking and correction: entries from LothWb, subcorpus C: 
- `output_edited/LothWb_C_Zufall.tsv`


## Requirements
- Python 3.10.9
- Packages:
    - random
    - csv
    - os
    - html
    - re
    - requests
    - lxml


## How to Run
1. Ensure Python 3.10.9 and required packages are installed.
2. Define the number of random entries you want to extract (variable num_entries).
3. Place the XML files of Lothringisches Wörterbuch in the prepared folder `input/LothWb_Daten/`.
4. Run script_8_3_2_zufallsauswahl_lothwb.py