# 9_4_3 Generative_Sprachmodelle - Begriffsmapping

## Overview
The folder contains the data and scripts used to perform the term mapping as part of the method using Large Language Models.

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `results/` - contains various outputs for the use of different vocabulary variants 

## Scripts
| Script | Description |
|--------|-------------|
| `script_9_4_3_00_run_llm_mapping` | Runs the pipeline |
| `script_9_4_3_01_ollama_mapping_basiskonzepte` | Performs mapping at the base concept level |
| `script_9_4_3_02_ollama_mapping_begriffe` | Performs mapping at the term level |


## Input
- corpus files:
    - `A_Getränke.tsv`
- JSON files Trinken vocabulary:
    - `getränke_vokabular.json`
    - `getränke_vokabular_nur_OT.json` - variant smaller vocabular 
- TXT files with different prompts:
    - `getränke_prompt.txt`
    - `getränke_terms_prompt.txt`
    - `getränke_concepts_prompt.txt`
   

## Output
Two output file are generated.
- `A_Getränke_basiskonzepte.tsv`  - Mapping results at the base concept level
- `A_Getränke_begriffe.tsv` - Mapping results at the term level

## Requirements
- Python 3.10.11
- Packages:
    - ollama (version used: 0.5.2)
    - pathlib
    - re
    - json
    - csv
    - os
    - time
    - typing

## How to Run
1. Ensure Python 3.10.11 and required packages are installed.
2. Make sure Ollama is installed and running (download: https://ollama.com/download)
3. Make sure the model you want to use is pulled (e.g. llama3)
4. In script_9_4_1_00_run_llm_mapping.py set the parameters in CONFIG:
    - json_vocab: choose the version of the vocabulary
    - model_name: choose the model
    - file_to_process
    - prompts: choose the prompt
5. Run script_9_4_3_00_run_llm_mapping.py to execute the pipeline.