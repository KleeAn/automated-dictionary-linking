# 11  – DiaLexBase

## Overview
The folder for chapter 11 contains the data and scripts used to build up the Wikibase instance DiaLexBase (https://dialexbase.wikibase.cloud).

## Scripts
| Script | Description |
|--------|-------------|
| `script_11_1_bot_create_lexemes` | Creates new lexemes in the Wikibase instance DiaLexBase |
| `script_11_2_generate_quickstatements` | Prepares statements about lemmas as quick statements for import into a Wikibase |


## Files
- `A_Trinken_mapping_gesamt.tsv` - Input file: TSV, contains subcorpus A with mapping results of all methods
- `A_Trinken_mapping_gesamt.txt` - Output file to script_11_2: TXT, prepared quick statements

## Requirements
- Python 3.10.9
- Packages:
    - wikidataintegrator (used version 0.9.30, see: https://pypi.org/project/wikidataintegrator/)
    - json
    - csv
    - requests
    - os


## How to Run

### script_11_1_bot_create_lexemes
1. Ensure Python 3.10.9 and required packages are installed.
2. Define your username and password of the wikibase instance, you would like to update.
3. Run script_11_1_bot_create_lexemes.py to execute the pipeline.

### script_11_2_generate_quickstatements
1. Ensure Python 3.10.9 and required packages are installed.
2. Run script_11_11_2_generate_quickstatements.py.
