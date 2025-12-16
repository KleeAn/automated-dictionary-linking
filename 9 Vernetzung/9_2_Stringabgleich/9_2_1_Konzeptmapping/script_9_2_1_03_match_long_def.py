# ================================================================
# Script 3: Mapping long definitions (>1 token) to concepts
# ================================================================

import pandas as pd
from collections import defaultdict
import os
import ast

# ------------------------------------------------------------
# Function: find_concepts
# Purpose: Find exact concept matches for a given definition string
# ------------------------------------------------------------
def find_concepts(konzept_mapping, def_string):
    def_string_clean = def_string.strip().lower()
    for concept, terms in konzept_mapping.items():
        for term in terms:
            if isinstance(term, list):
                for t in term:
                    if t.strip().lower() == def_string_clean:
                        return concept
            else:
                if term.strip().lower() == def_string_clean:
                    return concept
    return None

# ------------------------------------------------------------
# Function: update_mapped_concept
# Purpose: Update the mapped concepts by merging old and new values
# ------------------------------------------------------------
def update_mapped_concept(current, new):
    if pd.isna(new) or new == '':
        return current if pd.notna(current) else None
    if pd.isna(current) or current == '':
        return new

    current_set = set(filter(None, map(str.strip, str(current).split(';'))))
    new_set = set(filter(None, map(str.strip, str(new).split(';'))))

    gesamt = sorted(current_set.union(new_set))
    return '; '.join(gesamt)

# ------------------------------------------------------------
# Function: match_def_long
# Purpose: Match long definitions (more than one token) to concepts and update dataframe
# ------------------------------------------------------------
def match_def_long(input_path, konzept_mapping, output_dir):
    print(f"🔍 Starting matching on split definitions: {input_path}")
    
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

    # Initialize additional columns
    df['Def_lang_gemappt'] = ''
    df['Def_lang_ungemappt'] = ''
    df['Konzept_Def_lang'] = ''

    match_count = 0

    # Iterate over rows and match long definitions
    for index, row in df.iterrows():
        if pd.notna(row.get('Konzept_Def_kurz')):
            continue  # Skip if already matched with short definition

        def_list = row['Definition_gesplittet']
        if not isinstance(def_list, list) or len(def_list) <= 1:
            continue  # Only consider rows with more than one definition

        matched_strings = []
        unmatched_strings = []
        matched_concepts = []

        for entry in def_list:
            if isinstance(entry, str) and entry.strip():
                entry_clean = entry.replace('(', '').replace(')', '').strip()
                konzept = find_concepts(konzept_mapping, entry_clean)
                if konzept:
                    matched_strings.append(entry.strip())
                    matched_concepts.append(konzept)
                else:
                    unmatched_strings.append(entry.strip())

        if matched_concepts:
            match_count += 1
            df.at[index, 'Def_lang_gemappt'] = '; '.join(matched_strings)
            df.at[index, 'Konzept_Def_lang'] = '; '.join(sorted(set(matched_concepts)))
            df.at[index, 'Def_lang_ungemappt'] = '; '.join(unmatched_strings)

    # Ensure 'Konzept_gemappt' column exists
    if 'Konzept_gemappt' not in df.columns:
        df['Konzept_gemappt'] = None

    # Update overall mapped concepts by merging old and new values
    df['Konzept_gemappt'] = df.apply(
        lambda row: update_mapped_concept(row.get('Konzept_gemappt'), row.get('Konzept_Def_lang')),
        axis=1
    )

    # Move 'Konzept_gemappt' to the last column
    last_column = df.pop('Konzept_gemappt')
    df['Konzept_gemappt'] = last_column

    # Determine output file path
    basename = os.path.basename(input_path)
    if basename.startswith("2_") and basename.endswith("_matches_short_def.tsv"):
        output_path = os.path.join(
            output_dir,
            "3_" + basename[2:].replace("_matches_short_def.tsv", "_matches_long_def.tsv")
        )
    else:
        output_path = os.path.join(output_dir, "output_matches_long_def.tsv")

    # Save result
    df.to_csv(output_path, sep='\t', index=False)
    
    print("Script 3 completed: Long definitions (>1 Token) mapped.")
    print(f"– Entries with  matches (multiple splits): {match_count}")
    print(f"Results saved to: {output_path}\n")

    return output_path
