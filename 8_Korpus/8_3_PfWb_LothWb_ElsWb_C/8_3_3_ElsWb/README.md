# 8_3_3_zufallsauswahl_elswb

## Overview
The folder contains the data and scripts used for extracting random entries from ElsWb-TEI-XML files (Elsässisches Wörterbuch)

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `output_edited/` - manually edited output

## Script
| Script | Description |
|--------|-------------|
| `script_8_3_3_zufallsauswahl_elswb` | Extracts random entries from LothWb |


## Input
- `ElsWb_Daten/` - XML files Elsässisches Wörterbuch [prepared folder]

## Output
- `ElsWb_C_Zufall.tsv` - Random ElsWb entries for subcorpus C


## Output edited
Result file: After manual checking and correction: entries from ElsWb, subcorpus C: 
- `output_edited/ElsWb_C_Zufall.tsv`


## Requirements
- Python 3.10.9
- Packages:
    - random
    - csv
    - os
    - html
    - re
    - string
    - lxml


## How to Run
1. Ensure Python 3.10.9 and required packages are installed.
2. Define the number of random entries you want to extract (variable num_entries).
3. Place the XML files of Elsässisches Wörterbuch in the prepared folder `input/ElsWb_Daten/`.
4. Run script_8_3_2_zufallsauswahl_elswb.py