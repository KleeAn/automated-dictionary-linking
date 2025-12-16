# 9_3 ModernGBERT

## Overview

This folder documents the fine-tuning of the SentenceTransformer model ModernGBERT for mapping lemma-meaning pairs to concepts.

The training is carried out in the framework of a cross-fold validation. 

The basis for fine-tuning is the model ModernGBERT_1B (https://huggingface.co/LSX-UniWue/ModernGBERT_1B). 

Since the finetuned models are too large, they cannot be stored in this repository. They are published on Zenodo (https://doi.org/10.5281/zenodo.17953944).

The folders contain the scripts, the corpus data as well as the mapping predictions and statistical evaluations for the various trained models.

## Folder Structure

- `9_3_1_Binäre_Klassifikation/` - Fine-tuning the model for binary classification (Trinken vs. kein_Trinken)
- `9_3_2_Mulitklassen_Konzeptklassifikation/` - Fine-tuning the model for multi-class classification on concepts
- `9_3_3_Begriffsklassifikation/` - Fine-tuning the model for multi-class classification on terms
- `9_3_4_Zusammenführung` - Merging the results from binary and multi-class classification
