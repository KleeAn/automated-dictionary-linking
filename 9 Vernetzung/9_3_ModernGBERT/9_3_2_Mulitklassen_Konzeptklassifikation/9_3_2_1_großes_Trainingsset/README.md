# 9_3_2_1 Multiklassen-Klassifikation - Großes Trainingsset

## Overview
The folder contains the scripts and files that were used to fine-tune the SentenceTransformer model ModernGBERT and subsequently map lemma-meaning pairs to concepts.

The training is carried out in the framework of a cross-fold validation. The dataset is divided into 10 folds. For each training run, 9 folds are used for training and 1 fold is used for testing.

The basis for fine-tuning is the model ModernGBERT_1B (https://huggingface.co/LSX-UniWue/ModernGBERT_1B). 

Since the fine-tuned models are too large, they cannot be stored in this repository. The folders contain the corpus data as well as the mapping predictions and statistical evaluations for the various trained models.

## Folder Structure

- `input/` - contains input files
- `results/` - contains various outputs for different training variants and training parameters
    - `Komplettes Vokabular/` - whole concept vocabulary is used
    - `Reduziertes Vokabular/` - reduced concept vocabulary is used
    - `Vokabular ohne Begriffe/` - whole vocabulary but without terms
    - `Variante ModernGBERT/` - finetuning of ModernBERT (multilingual model)


## Scripts
| Script | Description |
|--------|-------------|
| `script_9_3_2_1_multiclass_large` | Finetuning of ModernGBERT and evaluating cross-valited multiclass classification |


## Input
- TSV file subcorpus A (with concept annotations; expanded version: multi-concept assignments are expanded into separated rows):
    - `A_Trinken_expanded.tsv`
- JSON file: vocabulary:
    - `trinken_vokabulary.json` (whole vocabulary)
    - `trinken_vokabulary_nur_OT.json` (reduced vocabulary)
- ModernGBERT model (LSX-UniWue/ModernGBERT_1B) will automatically be downloaded from the Hugging Face Model Hub

## Results
Within the folders for the individual fine-tuning variants: 
Each folder is named according to the parameters used during training, e.g. "10f_32bs_3e" - meaning: the model was trained in a cross-fold validation with 10 folds, a batch size of 32, and in 3 epochs.

Each folder contains:
- the mapping results of the test folds (`fold_1_predictions.tsv` etc.) 
- statistics on the entire cross-fold validation (`cv_summary.json`)
- in case of the model used for classification in chapter 9 (10f_32bs_4e): 
    - a file containing the results of all test folds (= mapping results for the entire corpus,`"A_Trinken_multiclass_10f_32bs_4e.tsv"`)
    - the predictions of the model for the subcorpora B and C (`"B_Verwandt_multiclass_10f_4e_32bs.tsv"` and `"C_Zufall_multiclass_10f_4e_32bs.tsv"`)

## Requirements
- Python 3.10.11
- Packages:
    - pandas
    - numpy
    - torch
    - sentence_transformers (used version 5.1.0)
    - scikit-learn (used version 1.7.2)
    - time
    - os
    - json
    - math
    - logging
    - random
    - typing

## How to Run
1. Ensure Python 3.10.11 and required packages are installed.
2. Make sure you have internet access so that the ModenGBERT model can be downloaded.
3. Define the parameters for the finetuning (section "Main execution" - especially batch_size, num_epochs and folds).
4. Run script_9_3_2_1_multiclass_large.py.