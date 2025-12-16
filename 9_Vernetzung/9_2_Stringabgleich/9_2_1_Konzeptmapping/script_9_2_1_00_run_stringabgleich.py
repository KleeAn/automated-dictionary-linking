# ================================================================
# Script for executing a 4-step pipeline that maps lexical units
# to drinking vocabulary concepts based on string matching.
# ================================================================

import os
import json
import time

from script_9_2_1_01_match_lemma import match_lemma_concepts
from script_9_2_1_02_match_short_def import match_def_short
from script_9_2_1_03_match_long_def import match_def_long
from script_9_2_1_04_match_def_root import match_def_root
from script_9_2_1_helpers import extract_concepts_and_terms
from script_9_2_1_helpers import process_tsv_file 

# === Directories ===
input_dir = "input"
output_dir = "output"

# === Input files ===
dictionary_files = [
   "A_Trinken.tsv", "B_Verwandt.tsv", "C_Zufall.tsv" , "A_B_C_gesamt.tsv"
]

concept_file = "trinken_vokabular_nur_OT.json" #"trinken_vokabular.json"  #trinken_vokabular_nur_OT.json

# ================================================================
# Function: main
# Purpose: Coordinates execution of the processing pipeline
# ================================================================
def main():
    print("Starting Pipeline")

    concept_path = os.path.join(input_dir, concept_file)
    
    small_vocab = "nur_OT" in concept_file

    # === Load concept file and extract concepts ===
    with open(concept_path, "r", encoding="utf-8") as f:
        concept_mapping = extract_concepts_and_terms(json.load(f))

    # ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for file in dictionary_files:
        print(f"\n Processing file: {file}\n")

        input_dict = os.path.join(input_dir, file)
        splitted_file = os.path.join(output_dir, f"0_{os.path.splitext(file)[0]}_gesplittet.tsv")

        # Step 0: Split definitions
        print("Step 0: Splitting definitions\n")
        process_tsv_file(input_dict, splitted_file)

        # Steps 1–4: Matching
        print("Steps 1–4: Starting matching ...\n")
        output_step1 = match_lemma_concepts(splitted_file, concept_mapping, output_dir, small_vocab)
        output_step2 = match_def_short(output_step1, concept_mapping, output_dir)
        output_step3 = match_def_long(output_step2, concept_mapping, output_dir)
        output_step4 = match_def_root(output_step3, concept_mapping, output_dir)

        print(f"Processing of {file} completed.")

    print("\n All files processed.")

# ================================================================
# Main execution
# ================================================================
if __name__ == "__main__":
    start_time = time.perf_counter()  # Startzeit
    main()
    end_time = time.perf_counter()    # Endzeit
    elapsed = end_time - start_time

    print(f"\nRunning time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
