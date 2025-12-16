# ================================================================
# Script 1: Mapping Lemmata with a given vocabulary list
# ================================================================

import pandas as pd
import os


# ---------------------------------------------------------------
# Function: match_lemma
# Purpose: Map Lemmata from a dictionary file against a given
#          vocabulary list and collect all matching lemmata.
# ---------------------------------------------------------------
def match_lemma(dictionary_path, vocabulary_list, output_dir, small_vocab=False):
    # Convert vocabulary list to set for efficient lookup
    vocabulary_set = set(vocabulary_list)

    # Load dictionary data
    df = pd.read_csv(dictionary_path, sep="\t")
    df['Lemma_gemappt'] = None

    # Iterate over dictionary entries and find all matching lemmata
    for index, row in df.iterrows():
        lemmata_raw = row.get('Lemma_bereinigt', "")
        lemmata = [l.strip() for l in str(lemmata_raw).split(',')] if isinstance(lemmata_raw, str) else []

        # Collect all lemmata present in the vocabulary set
        matched = [lemma for lemma in lemmata if lemma in vocabulary_set]

        if matched:
            df.at[index, 'Lemma_gemappt'] = ", ".join(matched)
    
    # Prepare output filename
    basename = os.path.splitext(os.path.basename(dictionary_path))[0]
    basename = basename.replace("_gesplittet", "")
    basename = basename[2:]  # Remove leading "0_"
    
    if small_vocab:
        basename = f"{basename}_OT"
    
    output_file = os.path.join(output_dir, f"1_{basename}_matches_lemma.tsv")

    # Save results
    df.to_csv(output_file, sep='\t', index=False)

    # Print summary
    print("Script 1 completed: Lemmata mapped.") 
    print(f"– Mapped entries: {df['Lemma_gemappt'].notna().sum()} / {len(df)}")
    print(f"Result saved: {output_file}\n")

    return output_file
