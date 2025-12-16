# 9_1_2_1 Precision_Recall - Basiskonzepte

## Overview
This folder contains the scripts and data for calculating precision, recall and f1 score of the mapping to the basic concepts (Basiskonzepte).
It is divided into subfolders according to the different methods.

Each of the subfolders contains an input and an output folder.

## Script
`script_9_1_2_1_precision_recall_basis.py`

## Input
- TSV files: mapping results (see result files in 9_2, 9_3, 9_4)

## Output
For each of the input files, one output file is generated, containing statics metrics precision, recall and f1 score in the overall view and by concept groups and word types:

`XXX_accuracy_precision_recall_basis.txt`


## Requirements
- Python 3.10.9
- Packages:
    - pandas
    - os
    - re
    - numpy
    - sklearn.metrics
    - sklearn.preprocessing
    - sklearn.exceptions
    - warnings


## How to Run
1. Ensure Python 3.10.9 and required packages are installed
2. Make sure your input files are stored in a folder named after the linking method. Define the folder name in the variable "method_dir".
3. Depending on the analyzed method, define in "mapping_choice" the which column of the input TSV contains the mapping result and should be used for evaluation (e.g. "Konzept_gemappt" oder "Top_1")
4. Run script_9_1_2_1_precision_recall_basis.py to execute the evaluation.