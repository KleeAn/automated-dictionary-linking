# 8_2_1_api_request

## Overview
The folder contains the data and scripts used for querying the Woerterbuchnetz API and extracting the linked entries from Lothringisches Wörterbuch (LothWB) and Elsässisches Wörterbuch (ElsWB)

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `output_edited/` - manually edited output

## Script
| Script | Description |
|--------|-------------|
| `script_8_2_1_get_wbnetz_links` | Queries the Wörterbuchnetz API |


## Input
- `PfWb_A_Trinken` - Subcorpus A with entries from Pfälzisches Wörterbuch (PfWB)
- `PfWb_B_Verwandt` - Subcorpus B with entries from Pfälzisches Wörterbuch(PfWB)

## Output
- `ElsWB_A_API.tsv` - Linked ElsWB entries to PfWb (subcorpus A)
- `ElsWB_B_API.tsv` - Linked ElsWB entries to PfWb (subcorpus B)
- `LothWB_A_API.tsv` - Linked LothWB entries to PfWb (subcorpus A)
- `LothWB_B_API.tsv` - Linked LothWB entries to PfWb (subcorpus A)

## Output edited
Result files: after manual checking and correction: entries from the ElsWb and LothWb, subcorpora A and B: 
- `output_edited/ElsWB_A_API.tsv`
- `output_edited/ElsWB_B_API.tsv` 
- `output_edited/LothWB_A_API.tsv`
- `output_edited/LothWB_B_API.tsv`

## Requirements
- Python 3.10.9
- Packages:
    - requests
    - csv
    - os


## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Run script_8_2_1_get_wbnetz_links.py