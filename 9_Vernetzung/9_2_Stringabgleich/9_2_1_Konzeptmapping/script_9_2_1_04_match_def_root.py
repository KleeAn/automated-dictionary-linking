# ================================================================
# Script 4: Mapping sentence roots of definitions to concepts
# ================================================================

import os
import pandas as pd
import stanza
from collections import defaultdict
import ast

# stanza.download('de')  # necessary in the first run
nlp = stanza.Pipeline('de')

# ------------------------------------------------------------
# Function: find_mappings
# Purpose: Find unique concept mapping for a given definition string
# ------------------------------------------------------------
def find_mappings(concept_mapping, def_string):
    begriff_zu_konzept = defaultdict(list)
    for konzept, begriffe in concept_mapping.items():
        for b in begriffe:
            if isinstance(b, list):
                for eintrag in b:
                    begriff_zu_konzept[eintrag].append(konzept)
            else:
                begriff_zu_konzept[b].append(konzept)

    if def_string in begriff_zu_konzept:
        zuordnungen = begriff_zu_konzept[def_string]
        if len(zuordnungen) == 1:
            return zuordnungen[0]
    else:
        return None

# ------------------------------------------------------------
# Function: match_def_root
# Purpose: Match sentence roots of definitions to concepts and update dataframe
# ------------------------------------------------------------
def match_def_root(input_path, concept_dict, output_dir):
    print(f"Starting matching on sentence roots of definitions: {input_path}")

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
    df['Konzept_Satzwurzel'] = None
    counter = 0

     # Iterate over rows for matching roots
    for index, row in df.iterrows():
        # Helper to check if a value is empty or NA
        def is_empty(wert):
            return (
                pd.isna(wert)
                or str(wert).strip().lower() in ['', 'none', 'nan']
            )

        def_unmapped = row.get('Def_lang_ungemappt', '')
        to_process = (
            (is_empty(row.get('Konzept_Def_kurz')) and is_empty(row.get('Konzept_Def_lang')))
            or (isinstance(def_unmapped, str) and def_unmapped.strip() != '')
        )

        if not to_process:
            continue

        # Prefer ungemapped long definitions if available, else use raw 'Definition_gesplittet'
        definition_list = []
        if isinstance(def_unmapped, str) and def_unmapped.strip():
            definition_list = [d.strip() for d in def_unmapped.split(';') if d.strip()]
        else:
            rohdaten = row.get('Definition_gesplittet', '')
            if not isinstance(rohdaten, list):
                try:
                    definition_list = ast.literal_eval(rohdaten)
                except:
                    continue

        roots = set()
        concepts = set()

        # Process each definition: get sentence root and map it
        print(f"\nProcessing line {index}")
        for definition in definition_list:
            if not isinstance(definition, str) or not definition.strip():
                continue

            doc = nlp(definition.replace('(', '').replace(')', ''))
            for sentence in doc.sentences:
                for word in sentence.words:
                    if word.head == 0:
                        lemma = word.lemma
                        gemapptes_konzept = find_mappings(concept_dict, lemma)
                        if gemapptes_konzept:
                            roots.add(lemma)
                            concepts.add(gemapptes_konzept)
                            counter += 1
                        break
                break  # only first sentence per definition

        df.at[index, 'Satzwurzel'] = '; '.join(sorted(roots)) if roots else None
        df.at[index, 'Konzept_Satzwurzel'] = '; '.join(sorted(concepts)) if concepts else None

    # ------------------------------------------------------------
    # Helper: update_mapped_concept
    # Purpose: Update mapped concepts by merging old and new values
    # ------------------------------------------------------------
    def update_mapped_concept(current, new):
        if pd.isna(new) or new is None or str(new).strip() == '':
            return current
        if pd.isna(current) or current is None or str(current).strip() == '':
            return new.strip()

        current_set = set(map(str.strip, str(current).split(';')))
        new_set = set(map(str.strip, str(new).split(';')))

        combined = sorted(current_set.union(new_set))
        return '; '.join([k for k in combined if k])  # keine leeren Teile

    # Create or update 'Konzept_gemappt' column
    if 'Konzept_gemappt' not in df.columns:
        df['Konzept_gemappt'] = None

    df['Konzept_gemappt'] = df.apply(
        lambda row: update_mapped_concept(row.get('Konzept_gemappt'), row.get('Konzept_Satzwurzel')),
        axis=1
    )

    # Move 'Konzept_gemappt' column to the end
    last_column = df.pop('Konzept_gemappt')
    df['Konzept_gemappt'] = last_column

    # Fill missing concept mappings with 'kein_Trinken'
    df['Konzept_gemappt'] = df['Konzept_gemappt'].fillna('kein_Trinken')
    df.loc[df['Konzept_gemappt'].astype(str).str.strip() == '', 'Konzept_gemappt'] = 'kein_Trinken'

    # Remove 'kein_Trinken' if multiple concepts exist
    def remove_kein_trinken(concepts):
        if not isinstance(concepts, str):
            return concepts
        teile = [k.strip() for k in concepts.split(';') if k.strip()]
        if len(teile) > 1 and 'kein_Trinken' in teile:
            teile = [k for k in teile if k != 'kein_Trinken']
        return '; '.join(teile)

    df['Konzept_gemappt'] = df['Konzept_gemappt'].apply(remove_kein_trinken)

    # Save intermediate result
    df.to_csv(output_path, sep='\t', index=False)
    print(f"Results saved to '{output_path}'")
    print("Number of newly mapped concepts via sentence roots:", counter)

    # ------------------------------------------------------------
    # Create final output file (_matches_final.tsv) without intermediate columns
    # ------------------------------------------------------------
    final_output_path = output_path.replace("_matches_root.tsv", "_matches_final.tsv")

    # Remove columns
    columns_to_remove = ["Lemma_bereinigt", "Definition_gesplittet"]

    if 'Lemma_gemappt' in df.columns and 'Konzept_Satzwurzel' in df.columns:
        start_idx = df.columns.get_loc('Lemma_gemappt')
        end_idx = df.columns.get_loc('Konzept_Satzwurzel')
        columns_to_remove.extend(df.columns[start_idx:end_idx+1].tolist())

    df_final = df.drop(columns=[sp for sp in columns_to_remove if sp in df.columns])

    df_final.to_csv(final_output_path, sep='\t', index=False)
    print(f"Final result saved to '{final_output_path}'\n")

    return output_path
