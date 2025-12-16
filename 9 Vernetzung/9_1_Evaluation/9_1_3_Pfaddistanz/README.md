# 9_1_3 Pfaddistanz

## Overview
This folder contains the scripts and data for calculating the path distances of the mapping to the basic concepts (Basiskonzepte).
It is divided into subfolders according to the different methods.

Each of the subfolders contains an input and an output folder.

## Script
`script_9_1_3_path_distance.py`

## Input
- TSV files: mapping results (see result files in 9_2, 9_3, 9_4)
- `trinken.ttl` - vocabulary with concept hierarchy 

## Output
For each of the input files, two output files are generated: 

| File | Description |
|--------|-------------|
|`XXX_pfaddistanzen.tsv` | Input file with additional evaluations such as shortes path, minimal and average distances |
|`XXX_pfaddistanzen.txt` | statistics with path distancen overall and by concept group and pos |


## Requirements
- Python 3.10.9
- Packages:
    - pandas
    - os
    - re
    - rdflib
    - networkx


## How to Run
1. Ensure Python 3.10.9 and required packages are installed.
2. Make sure the .ttl file is stored in the same folder as the script.
2. Make sure your mapping results files are stored in a folder named after the linking method. Define the folder name in the variable "method_dir".
3. Depending on the analyzed method, define in "mapping_choice" the which column of the input TSV contains the mapping result and should be used for evaluation (e.g. "Konzept_gemappt" oder "Top_1").re 
4. Run script_9_1_3_path_distance.py to execute the evaluation.