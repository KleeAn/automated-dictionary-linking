# 9_4_1 Generative_Sprachmodelle - Konzeptmapping

## Overview
The folder contains the data and scripts used to perform the concept mapping as part of the method using Large Language Models.

## Folder Structure

- `input/` - contains input files
- `output/` - contains script output
- `results/` - contains various outputs for different prompts and models

## Scripts
| Script | Description |
|--------|-------------|
| `script_9_4_1_00_run_llm_mapping` | Runs the pipeline |
| `script_9_4_1_01_ollama_mapping_wurzelkonzepte` | Performs mapping at the root concept level |
| `script_9_4_1_02_ollama_mapping_basiskonzepte` | Performs mapping at the base concept level |


## Input
- corpus files:
    - `A_Trinken.tsv`
    - `B_Verwandt.tsv`
    - `C_Zufall.tsv`
- JSON files Trinken vocabulary:
    - `trinken_vokabular.json`
    - `trinken_vokabular_nur_OT.json` - variant smaller vocabular 
- TXT files with different prompts:
    - `prompt_1.txt`
    - `prompt_2.txt`
    - `wurzelkonzepte_prompt_3a.txt`
    - `wurzelkonzepte_prompt_3b.txt`
    - `basiskonzepte_prompt_4a.txt`
    - `basiskonzepte_prompt_4b.txt`
    - `basiskonzepte_prompt_4b_nur_konzepte.txt`


## Output
For each of the input files, two output file are generated.
- `XX_wurzelkonzepte.tsv`  - Mapping results at the root concept level
- `XX_basiskonzepte.tsv` - Mapping results at the base concept level

The middle segment shows which model has been use, e.g.: `A_Trinken_llama_70b_basiskonzepte.tsv`

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
    - json_vocab: choose the version of the Trinken vocabulary
    - model_name: choose the model
    - file_to_process
    - prompts: choose the prompt
    - with_terms: choose whether to pass the terms for the concepts or not
5. Run script_9_4_1_00_run_llm_mapping.py to execute the pipeline.