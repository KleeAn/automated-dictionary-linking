# ================================================================
# Script 3: Mapping long definitions (>1 token) to vocabulary terms
# ================================================================

import pandas as pd
import os
import ast

# ------------------------------------------------------------
# Function: match_term
# Purpose: Find exact matches of a definition string in vocabulary list
# ------------------------------------------------------------
def match_term(vocabulary_list, def_string):
    def_string_clean = def_string.strip().lower()
    for term in vocabulary_list:
        if term.strip().lower() == def_string_clean:
            return term
    return None

# ------------------------------------------------------------
# Function: update_mapped_terms
# Purpose: Merge previously mapped terms with new ones
# ------------------------------------------------------------
def update_mapped_terms(current, new):
    if pd.isna(new) or new == '':
        return current if pd.notna(current) else None
    if pd.isna(current) or current == '':
        return new

    current_set = set(filter(None, map(str.strip, str(current).split(';'))))
    new_set = set(filter(None, map(str.strip, str(new).split(';'))))

    combined = sorted(current_set.union(new_set))
    return '; '.join(combined)

# ------------------------------------------------------------
# Function: match_long_def
# Purpose: Match long definitions (>1 token) exactly with vocabulary list and update dataframe
# ------------------------------------------------------------
def match_long_def(input_path, vocabulary_list, output_dir):
    print(f"Starting exact matching with vocabulary on file: {input_path}")

    # Load data
    df = pd.read_csv(input_path, sep='\t')

    # Parse 'Definition_gesplittet' as list
    def parse_definition_list(entry):
        try:
            parsed = ast.literal_eval(entry)
            return parsed if isinstance(parsed, list) else []
        except:
            return []

    df['Definition_gesplittet'] = df['Definition_gesplittet'].apply(parse_definition_list)

    # Initialize columns
    df['Def_lang_gemappt'] = ''
    df['Begriff_Def_lang'] = ''

    match_count = 0

    # Iterate rows and perform exact matching on long definitions
    for index, row in df.iterrows():
        if pd.notna(row.get('Begriff_Def_kurz')):
            continue  # Skip if already matched by short definition

        def_list = row['Definition_gesplittet']
        if not isinstance(def_list, list) or len(def_list) <= 1:
            continue  # Only consider rows with multiple splits

        matched_strings = []
        matched_terms = []

        for entry in def_list:
            if isinstance(entry, str) and entry.strip():
                entry_clean = entry.replace('(', '').replace(')', '').strip()
                term = match_term(vocabulary_list, entry_clean)
                if term:
                    matched_strings.append(entry.strip())
                    matched_terms.append(term)

        if matched_terms:
            match_count += 1
            df.at[index, 'Def_lang_gemappt'] = '; '.join(matched_strings)
            df.at[index, 'Begriff_Def_lang'] = '; '.join(sorted(set(matched_terms)))

    # Ensure 'Vokabel_gemappt' column exists
    if 'Begriff_gemappt' not in df.columns:
        df['Begriff_gemappt'] = None

    # Update overall mapped vocabulary by merging old and new values
    df['Begriff_gemappt'] = df.apply(
        lambda row: update_mapped_terms(row.get('Begriff_gemappt'), row.get('Begriff_Def_lang')),
        axis=1
    )

    # Move 'Vokabel_gemappt' to last column
    last_col = df.pop('Begriff_gemappt')
    df['Begriff_gemappt'] = last_col

    # Define output file path
    basename = os.path.basename(input_path)
    if basename.startswith("2_") and basename.endswith("_matches_short_def.tsv"):
        output_path = os.path.join(
            output_dir,
            "3_" + basename[2:].replace("_matches_short_def.tsv", "_matches_long_def.tsv")
        )
    else:
        output_path = os.path.join(output_dir, "output_matches_long_def.tsv")

    # Save output
    df.to_csv(output_path, sep='\t', index=False)

    print("Script 3 completed: Exact matching of long definitions.")
    print(f"– Rows with matches (multiple splits): {match_count}")
    print(f"Results saved to: {output_path}\n")

    return output_path
