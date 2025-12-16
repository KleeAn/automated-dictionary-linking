# ================================================================
# Script 4: Mapping sentence roots of definitions to vocabulary terms
# ================================================================

import os
import pandas as pd
import stanza
import ast

# stanza.download('de')  # only needed on first run
nlp = stanza.Pipeline('de')

# ------------------------------------------------------------
# Function: match_vocabulary
# Purpose: Check if a given term is in the vocabulary set
# ------------------------------------------------------------
def match_vocabulary(vocabulary_set, word):
    if word in vocabulary_set:
        return word
    return None

# ------------------------------------------------------------
# Function: match_def_root
# Purpose: Match sentence roots of definitions to vocabulary entries and update dataframe
# ------------------------------------------------------------
def match_def_root(input_path, vocabulary_list, output_dir):
    vocabulary_set = set(vocabulary_list)

    # Determine output path based on input filename pattern
    basename = os.path.basename(input_path)
    if basename.startswith("3_") and basename.endswith("_matches_long_def.tsv"):
        output_path = os.path.join(
            output_dir,
            "4_" + basename[2:].replace("_matches_long_def.tsv", "_matches_root.tsv")
        )
    else:
        output_path = os.path.join(output_dir, "output_matches_root.tsv")

    # Load data
    df = pd.read_csv(input_path, sep='\t')

    # Initialize columns and counter
    df['Satzwurzel'] = None
    df['Begriff_Satzwurzel'] = None
    counter = 0

    # Iterate over rows for matching roots
    for index, row in df.iterrows():
        # Skip rows where both short and long vocabulary mappings exist
        if pd.notna(row.get('Begriff_Def_kurz')) and pd.notna(row.get('Begriff_Def_lang')):
            continue

        definition_list = row.get('Definition_gesplittet', '')

        # Parse definition list if necessary
        if not isinstance(definition_list, list):
            try:
                definition_list = ast.literal_eval(definition_list)
            except:
                print(f"Parsing error at line {index}")
                continue

        roots = set()
        vocabularies = set()

        print(f"\nProcessing line {index}")
        for definition in definition_list:
            if not isinstance(definition, str) or not definition.strip():
                continue

            doc = nlp(definition.replace('(', '').replace(')', ''))
            for sentence in doc.sentences:
                for word in sentence.words:
                    if word.head == 0:
                        lemma = word.lemma
                        vocab = match_vocabulary(vocabulary_set, lemma)
                        if vocab:
                            roots.add(lemma)
                            vocabularies.add(vocab)
                            counter += 1
                        break  # only first root per sentence
                break  # only first sentence per definition

        df.at[index, 'Satzwurzel'] = '; '.join(sorted(roots)) if roots else None
        df.at[index, 'Begriff_Satzwurzel'] = '; '.join(sorted(vocabularies)) if vocabularies else None

    # ------------------------------------------------------------
    # Helper: update_mapped_vocabulary
    # Purpose: Merge existing and new mapped vocabulary strings
    # ------------------------------------------------------------
    def update_mapped_vocabulary(current, new):
        if pd.isna(new) or new is None or str(new).strip() == '':
            return current
        if pd.isna(current) or current is None or str(current).strip() == '':
            return new.strip()

        current_set = set(map(str.strip, str(current).split(';')))
        new_set = set(map(str.strip, str(new).split(';')))
        combined = sorted(current_set.union(new_set))
        return '; '.join([k for k in combined if k])  # no empty parts

    # Create or update 'Begriff_gemappt' column
    if 'Begriff_gemappt' not in df.columns:
        df['Begriff_gemappt'] = None

    df['Begriff_gemappt'] = df.apply(
        lambda row: update_mapped_vocabulary(row.get('Begriff_gemappt'), row.get('Begriff_Satzwurzel')),
        axis=1
    )

    # Move 'Begriff_gemappt' column to the end
    last_column = df.pop('Begriff_gemappt')
    df['Begriff_gemappt'] = last_column

    # Fill missing mappings with 'kein_Trinken'
    df['Begriff_gemappt'] = df['Begriff_gemappt'].fillna('kein_Trinken')
    df.loc[df['Begriff_gemappt'].astype(str).str.strip() == '', 'Begriff_gemappt'] = 'kein_Trinken'

    # ------------------------------------------------------------
    # Helper: remove_keintrinken_if_multiple
    # Purpose: Remove 'kein_Trinken' if multiple vocabulary mappings exist
    # ------------------------------------------------------------
    def remove_kein_trinken(entries):
        if not isinstance(entries, str):
            return entries
        parts = [k.strip() for k in entries.split(';') if k.strip()]
        if len(parts) > 1 and 'kein_Trinken' in parts:
            parts = [k for k in parts if k != 'kein_Trinken']
        return '; '.join(parts)

    df['Begriff_gemappt'] = df['Begriff_gemappt'].apply(remove_kein_trinken)

    # Save intermediate result
    df.to_csv(output_path, sep='\t', index=False)
    print(f"Results saved to '{output_path}'")
    print("Number of newly mapped vocabulary entries via sentence roots:", counter)

    # ------------------------------------------------------------
    # Create final output file (_matches_final.tsv) without intermediate columns
    # ------------------------------------------------------------
    final_output_path = output_path.replace("_matches_root.tsv", "_matches_final.tsv")

    # Remove columns
    columns_to_remove = ["Lemma_bereinigt", "Definition_gesplittet"]

    if 'Lemma_gemappt' in df.columns and 'Begriff_Satzwurzel' in df.columns:
        start_idx = df.columns.get_loc('Lemma_gemappt')
        end_idx = df.columns.get_loc('Begriff_Satzwurzel')
        columns_to_remove.extend(df.columns[start_idx:end_idx+1].tolist())

    df_final = df.drop(columns=[sp for sp in columns_to_remove if sp in df.columns])

    df_final.to_csv(final_output_path, sep='\t', index=False)
    print(f"Final result saved to '{final_output_path}'\n")

    return output_path

