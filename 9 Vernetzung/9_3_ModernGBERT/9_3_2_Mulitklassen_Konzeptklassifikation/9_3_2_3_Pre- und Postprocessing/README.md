# 9_3_2_3 Multiklassen-Klassifikation - Pre- und Postprocessing

## Overview
This folder contains the scripts used for pre- and post-processing as part of ModernGBERT fine-tuning for multi-class classification of lemma-meaning pairs.

## Scripts

### script_9_3_2_3_01_expand_multilabels

- *Function*: Expands multi-concept assignments into separate rows. Used to prepare the input for the cross-validated training of a SentenceTransformer model for a multiclass classification of lemma-definition pairs to concepts (see: 9_3_2_Multiklassen_Konzeptklassifikation).
- *Input*: Corpus file "A_Trinken.tsv"
- *Output*: "A_Trinken_expanded.tsv"

### script_9_3_2_3_02_apply_model

- *Function*: Application of a fine-tuned SentenceTransformer model to lemma-meaning pairs for concept prediction. Used to predict the concepts of the lemma-meaning pairs of the subcorpora B and C.
- *Input*: Corpus file "B_Verwandt.tsv", "C_Zufall.tsv"
- The path to to the fine-tuned model hast to be defined in model_path (see section "Execution").
- *Output*: "B_Verwandt_10f_32bs_4e.tsv", "C_Zufall_10f_32bs_4e.tsv" (depending on the model that is used for prediction)

### script_9_3_2_3_03_merge_files_multiclass_large

- *Function*: The predictions for the individual test folds from the cross-validation are merged into a single file.
- *Input*: The input is expected to be TSV files generated as output during the fine-tuning of the ModernGBERT model for multiclass classification with a large training set (1 Fold for testing, rest for training).
- *Output*: The script generates a single output file containing one prediction for each corpus entry.

### script_9_3_2_3_01_merge_files_multiclass_small

- *Function*: The predictions for the individual test folds from the cross-validation are merged into a single file. Duplicates are resolved.
- *Input*: The input is expected to be TSV files generated as output during the fine-tuning of the ModernGBERT model for multiclass classification with a small training set (1 Fold for training, rest for testing).
- *Output*: The script generates a single output file containing one prediction for each corpus entry.

## Requirements
- Python 3.10.11
- Packages:
    - sentence-transformers
    - json
    - pandas
    - glob
    - numpy
    - os


