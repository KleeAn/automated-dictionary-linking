# 9_3_3_2 Begriffsklassifikation - Pre- und Postprocessing

## Overview
This folder contains the scripts used for pre- and post-processing as part of ModernGBERT fine-tuning for multi-class classification of lemma-meaning pairsto terms.


## Scripts

### script_9_3_3_2_01_expand_multilabels_terms

- *Function*: Expands multi-concept assignments into separate rows. Used to prepare the input for the cross-validated training of a SentenceTransformer model for a multiclass classification of lemma-definition pairs to terms (see: 9_3_3_Begriffsklassifikation).
- *Input*: Corpus file "A_Getränk.tsv"
- *Output*: "A_Getränk_expanded.tsv"


### script_9_3_3_2_02_merge_files_terms

- *Function*: The predictions for the individual test folds from the cross-validation are merged into a single file.
- *Input*: The input is expected to be TSV files generated as output during the fine-tuning of the ModernGBERT model for multiclass classification.
- Ensure that the script and the files to be processed are located in the same folder.
- *Output*: The script generates a single output file containing one prediction for each corpus entry.


## Requirements
- Python 3.10.11
- Packages:
    - pandas
    - glob
    - os
    - random
