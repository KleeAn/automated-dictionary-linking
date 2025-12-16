# ================================================================
# Script 1: Mapping Lemmata with corresponding concepts 
# ================================================================

import pandas as pd
import os
from collections import defaultdict

# ------------------------------------------------------------
# Function: match_lemma_concepts
# Purpose: Map Lemmata to concepts using a provided concept mapping
# ------------------------------------------------------------
def match_lemma_concepts(dictionary_path, concept_mapping, output_dir, small_vocab=False):
    # Prepare reverse mapping: term -> concept(s)
    term_to_concept = defaultdict(list)
    for concept, terms in concept_mapping.items():
        for t in terms:
            term_to_concept[t].append(concept)

    # Load dictionary data
    df = pd.read_csv(dictionary_path, sep="\t")
    df['Lemma_gemappt'] = None
    df['Konzept_Lemma'] = None

    # Iterate through entries and map lemmata to concepts if unique match
    for index, row in df.iterrows():
        lemmata_raw = row.get('Lemma_bereinigt', "")
        lemmata = [l.strip() for l in str(lemmata_raw).split(',')] if isinstance(lemmata_raw, str) else []

        for lemma in lemmata:
            if lemma in term_to_concept and len(term_to_concept[lemma]) == 1:
                df.at[index, 'Lemma_gemappt'] = lemma
                df.at[index, 'Konzept_Lemma'] = term_to_concept[lemma][0]
                break

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
    print(f"– Mapped entries: {df['Konzept_Lemma'].notna().sum()} / {len(df)}")
    print(f"Result saved: {output_file}\n")

    return output_file
