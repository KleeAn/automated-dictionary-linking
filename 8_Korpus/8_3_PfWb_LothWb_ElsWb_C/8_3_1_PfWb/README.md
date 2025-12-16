# 8_3_1_PfWb

## Overview
The folder contains the data and scripts used to for executing a 4-step pipeline to generate a random sample of PfWb entries for the subcorpus C.

Rudolf Post kindly provided me with his data from the Pfälzisches Wörterbuch for my project, including the Sachgruppen annotation he had created.

These are used in the corpus construction to get a random sample of entries that don't belong to the semantic field of drinking (subcorpus C).

The data cannot be published here, a corresponding folder has been prepared.

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `output_edited/` - manually edited output

## Scripts
| Script | Description |
|--------|-------------|
| `script_8_3_1_00_run` | Runs the pipeline |
| `script_8_3_1_01_random_sample_pfwb` | Random selection and filtering of valid lines from PfWb Post data |
| `script_8_3_1_02_txt2tsv` | Conversion of Post-data in TXT to TSV format
| `script_8_3_1_03_xml_mapping.py` | Mapping the Post data with XML data of PfälzischesWörterbuch
| `script_8_3_1_04_normalize_pos.py` | Mapping grammatical information to POS 

## Input
- `PfWb_Post/` - prepared folder for files of PfWb data of Rudolf Post 
- `pfwb_xml_example_data.tsv` - Example dictionary data of Pfälzisches Wörterbuch with Wörterbuchnetz-ID, headword, level and definiton

## Output
- `zufallsauswahl_pfwb.tsv` - Random selection auf PfWb entries
- `zufallsauswahl_pfwb_mapped.tsv` - Entries mapped to Wörterbuchnetz IDs
- `zufallsauswahl_pfwb_prepared.tsv` - Prepared files with POS annotation

## Output edited
Result files: Entries from the Pfälzisches Wörterbuch, subcorpus C: 
- `output_edited/PfWb_C_Zufall`


## Requirements
- Python 3.10.9
- Packages:
    - os
    - re
    - random
    - csv
    - pandas


## How to Run
1. Ensure Python 3.10.9 and required packages are installed.
2. To obtain a random selection from the complete Pfälzisches Wörterbuch, the corresponding file with the dictionary data must be located in the input folder. 
3. Store the files of PfWb data of Rudolf Post in the corresponding folder `PfWb_Post`.
4. Run script_8_3_1_00_run.py to execute the pipeline.