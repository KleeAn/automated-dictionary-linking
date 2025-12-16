# 9_1_1_2 Accuracy - Wurzelkonzepte

## Overview
This folder contains the scripts and data for calculating the accuracy of the mapping to the root concepts (Wurzelkonzepte).
It is divided into subfolders according to the different methods.

Each of the subfolders contains an input and an output folder.

## Script
`script_9_1_1_2_accuracy_wurzel.py`

## Input
- TSV files: mapping results (see result files in 9_2, 9_3, 9_4)

## Output
For each of the input files, two output files are generated:

| File | Description |
|--------|-------------|
|`XXX_accuracy_wurzel.tsv` | Input file with additional category of alignment|
|`XXX_accuracy_wurzel_statistk.tsv` | accuracy statistics |

## Requirements
- Python 3.10.9
- Packages:
    - pandas
    - os
    - re


## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Make sure your input files are stored in a folder named after the linking method. Define the folder name in the variable "method_dir".
3. Depending on the analyzed method, define in "mapping_choice" the which column of the input TSV contains the mapping result and should be used for evaluation (e.g. "Konzept_gemappt" oder "Top_1")
4. Run script_9_1_1_2_accuracy_wurzel.py to execute the evaluation.