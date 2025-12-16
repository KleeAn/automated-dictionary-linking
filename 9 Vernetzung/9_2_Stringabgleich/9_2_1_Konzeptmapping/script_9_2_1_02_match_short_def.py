# ================================================================
# Script 2: Mapping short single-word definitions to concepts
# ================================================================

import pandas as pd
import os
import ast
from collections import defaultdict

# ------------------------------------------------------------
# Function: match_def_short
# Purpose: Map single-token short definitions to concepts using provided concept mapping
# ------------------------------------------------------------
def match_def_short(input_path, concept_mapping, output_dir):
    # Map terms to concepts
    term_to_concept = defaultdict(list)
    for concept, terms in concept_mapping.items():
        for t in terms:
            term_to_concept[t].append(concept)

    # Load input file
    df = pd.read_csv(input_path, sep='\t')

    # Parse 'Definition_gesplittet' entries as lists
    def parse_definition_list(entry):
        try:
            parsed = ast.literal_eval(entry)
            return parsed if isinstance(parsed, list) else []
        except:
            return []

    df['Definition_gesplittet'] = df['Definition_gesplittet'].apply(parse_definition_list)

    # Assign short definition and concept (only if exactly one token)
    def process_entry(teile):
        if isinstance(teile, list) and len(teile) == 1:
            entry = teile[0].strip()
            if len(entry.split()) == 1:
                # Single-word definition: check mapping
                if entry in term_to_concept:
                    concepts = term_to_concept[entry]
                    if len(concepts) == 1:
                        return pd.Series([entry, concepts[0]])
                    else:
                        return pd.Series([entry, None])  # Ambiguous
                else:
                    return pd.Series([entry, "kein_Trinken"])
        return pd.Series(['', ''])

    df[['Def_kurz_gemappt', 'Konzept_Def_kurz']] = df['Definition_gesplittet'].apply(process_entry)

    # Combine concepts from lemma and short definition
    def combine_concepts(lemma, short_def):
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

    df['Konzept_gemappt'] = df.apply(
        lambda row: combine_concepts(row.get('Konzept_Lemma'), row.get('Konzept_Def_kurz')),
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

    print("Script 2 completed: Short definitions (1 Token) mapped.")
    print(f"– Entries with exactly 1 single-word definition: {df['Def_kurz_gemappt'].astype(bool).sum()}")
    print(f"– Definitions matched:              {df['Konzept_Def_kurz'].astype(bool).sum()}")
    print(f"Result saved: {output_file}\n")

    return output_file
