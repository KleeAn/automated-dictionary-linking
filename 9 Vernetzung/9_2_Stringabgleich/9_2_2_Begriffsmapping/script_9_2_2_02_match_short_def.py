# ================================================================
# Script 2: Mapping single-word definitions using vocabulary list
# ================================================================

import pandas as pd
import os
import ast

# ------------------------------------------------------------
# Function: match_def_short
# Purpose: Map single-token definitions against a given vocabulary list
# ------------------------------------------------------------
def match_def_short(input_path, vocabulary_list, output_dir):
    # Convert vocabulary list to set 
    vocabulary_set = set(vocabulary_list)

    # Load input file
    df = pd.read_csv(input_path, sep='\t')

    # Parse 'Definition_gesplittet' entries safely as lists
    def parse_definition_list(entry):
        try:
            parsed = ast.literal_eval(entry)
            return parsed if isinstance(parsed, list) else []
        except:
            return []

    df['Definition_gesplittet'] = df['Definition_gesplittet'].apply(parse_definition_list)

    # Assign short definition and matched vocabulary term only if exactly one token
    def process_entry(parts):
        if isinstance(parts, list) and len(parts) == 1:
            entry = parts[0].strip()
            if len(entry.split()) == 1:
                if entry in vocabulary_set:
                    return pd.Series([entry, entry])
                else:
                    return pd.Series([entry, "kein_Trinken"])
        return pd.Series(['', ''])

    df[['Def_kurz_gemappt', 'Begriff_Def_kurz']] = df['Definition_gesplittet'].apply(process_entry)

    # Combine terms from lemma and short definition
    def combine_terms(lemma, short_def):
        if pd.notna(lemma) and pd.notna(short_def):
            if lemma == short_def:
                return lemma
            else:
                return f"{lemma}; {short_def}"
        elif pd.notna(lemma):
            return lemma
        elif pd.notna(short_def):
            return short_def
        else:
            return None

    df['Begriff_gemappt'] = df.apply(
        lambda row: combine_terms(row.get('Lemma_gemappt'), row.get('Begriff_Def_kurz')),
        axis=1
    )

    # Determine output filename
    basename = os.path.basename(input_path)
    if basename.startswith("1_") and basename.endswith("_matches_lemma.tsv"):
        output_file = os.path.join(
            output_dir,
            "2_" + basename[2:].replace("_matches_lemma.tsv", "_matches_short_def.tsv")
        )
    else:
        output_file = os.path.join(output_dir, "output_matches_short_def.tsv")

    # Save output file
    df.to_csv(output_file, sep='\t', index=False)

    # Logging output
    print("Script 2 completed: Single-word definitions matched with vocabulary.")
    print(f"– Entries with exactly 1 single-word def: {df['Def_kurz_gemappt'].astype(bool).sum()}")
    print(f"– Definitions matched:                   {df['Begriff_Def_kurz'].astype(bool).sum()}")
    print(f"Result saved: {output_file}\n")

    return output_file
