# 8_1_PfWb_A_B

## Overview
The folder contains the data and scripts used to build the corpus based on dictionary entries from Pfälzisches Wörterbuch (Parts A + B).

Rudolf Post kindly provided me with his data from the Pfälzisches Wörterbuch for my project, including the Sachgruppen annotation he had created. These are used in the corpus construction to narrow down the dictionary data for an exemplary analysis of the semantic field of drinking. As the data cannot be published here, a dummy file is provided to illustrate how the scripts work.

Further input comes from the dictionary data of the Pfälzisches Wörterbuch. The relevant information required (ID, lemma, level, definition) was systematically prepared in the form of a TSV. The repository provides a sample file.

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `output_edited/` - manually edited output

## Scripts
| Script | Description |
|--------|-------------|
| `script_8_1_00_run` | Runs the pipeline |
| `script_8_1_01_txt2tsv` | Conversion of Post-data from TXT to TSV format |
| `script_8_1_02_xml_mapping` | Matching the Post data with XML data of Pfälzisches Wörterbuch
| `script_8_1_03_normalize_pos.py` | mapping grammatical information to POS 

## Input
- `pfwb_xml_example_data.tsv` - Dictionary example data of Pfälzisches Wörterbuch: TSV file with Wörterbuchnetz-ID, headword, level and definiton
- `Sachgruppe_5920_dummy.txt` - Example TXT-file: Pfälzisches Wörterbuch entries with annotation of 5920-Sachgruppe by Rudolf Post

## Output
- `Sachgruppe_5920_dummy.tsv` - TXT input file converted into TSV
- `Sachgruppe_5920_dummy_mapped.tsv` - Entries mapped to Wörterbuchnetz IDs
- `Sachgruppe_5920_dummy_prepared.tsv` - prepared files with POS annotation; file serves as the basis for manual assignment to subcorpora A and B.

## Output edited
Result files: entries from the Pfälzisches Wörterbuch, subcorpora A and B: 
- `output_edited/PfWb_A_Trinken`
- `output_edited/PfWb_B_Verwandt` 

## Requirements
- Python 3.10.9
- Packages:
    - re
    - csv
    - pandas


## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Define the Post-Sachgruppe in script_8_1_00_run.py (variable "prefix")
3. Run script_8_1_00_run.py to execute the pipeline.