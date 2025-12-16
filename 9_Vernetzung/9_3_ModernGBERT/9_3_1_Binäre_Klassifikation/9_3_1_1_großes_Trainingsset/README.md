# 9_3_1_1 Binäre Klassifikation - Großes Trainingsset

## Overview
The folder contains the scripts and files that were used to fine-tune the SentenceTransformer model ModernGBERT and subsequently map lemma-meaning pairs to the two classes "Trinken" or "kein_Trinken".

The training is carried out in the framework of a cross-fold validation. The dataset is divided into 10 folds. For each training run, 9 folds are used for training and 1 fold is used for testing.

The basis for fine-tuning is the model ModernGBERT_1B (https://huggingface.co/LSX-UniWue/ModernGBERT_1B). 

Since the fine-tuned models are too large, they cannot be stored in this repository. The folders contain the corpus data as well as the mapping predictions and statistical evaluations for the various trained models.

## Folder Structure

- `input/` - contains input files
- `results/` - contains various outputs for different training parameters


## Scripts
| Script | Description |
|--------|-------------|
| `script_9_3_1_1_binary_large` | Finetuning of ModernGBERT and evaluating cross-valited binary classification |


## Input
- corpus file:
    - `A_B_C_gesamt_binär.tsv`
- ModernGBERT model (LSX-UniWue/ModernGBERT_1B) will automatically be downloaded from the Hugging Face Model Hub


## Results

Each folder is named according to the parameters used during training, e.g. "10f_32bs_3e" - meaning: the model was trained in a cross-fold validation with 10 folds, a batch size of 32, and in 3 epochs.

Each folder contains:
- the mapping results of the test folds (`fold_1_results` etc.) 
- statistics on the entire cross-fold validation (`“aggregated_results.tsv”`)
- in case of the model used for classification in chapter 9 (10f_32bs_3e): a file containing the results of all test folds (= mapping results for the entire corpus, e.g. `"A_B_C_gesamt_binär_10f_32bs_3e.tsv"`)

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

## How to Run
1. Ensure Python 3.10.11 and required packages are installed.
2. Make sure you have internet access so that the ModenGBERT model can be downloaded.
3. Define the parameters for the finetuning (section "Hyperparameters" - batch_size; num_epochs; treshold)
4. Run script_9_3_1_1_binary_large.py to execute the pipeline.