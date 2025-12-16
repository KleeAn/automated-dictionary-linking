# ================================================================
# Script for creating a list of definitions and assigned concepts
# based on the existing corpus entries
# ================================================================

import pandas as pd
import re
import os
import glob

input_dir = "input"
output_dir = "output"

# ================================================================
# Function: read_tsv
# Purpose:  Reads a TSV file into a pandas DataFrame
# ================================================================
def read_tsv(input_file):
    """
    Reads a TSV file with UTF-8 encoding into a DataFrame.
    """
    return pd.read_csv(input_file, sep='\t', encoding='utf-8', dtype=str)

# ================================================================
# Function: expand_parentheses_ordered
# Purpose:  Returns a list of word variants by expanding parentheses
# ================================================================
def expand_parentheses_ordered(word):
    """
    If the word contains parentheses, returns two variants:
    one with the parentheses content included, one without.
    """
    match = re.search(r'^(.*)\(([^)]+)\)(.*)$', word)
    if match:
        prefix, insert, suffix = match.groups()
        return [prefix + insert + suffix, prefix + suffix]
    else:
        return [word]

# ================================================================
# Function: remove_roman_numerals
# Purpose:  Removes Roman numerals (I, II, III) in homograph entries at the end of a string
# ================================================================
def remove_roman_numerals(word):
    """
    Strips Roman numerals I, II, III at the end of the string.
    """
    return re.sub(r'\s*(I{1,3})$', '', word.strip())

# ================================================================
# Function: normalize_lemmata
# Purpose:  Processes 'Lemma' column to produce normalized lemmata variants
# ================================================================
def normalize_lemmata(df):
    """
    Normalizes the lemmata according to defined rules, expands variants,
    removes Roman numerals, and handles prefixes/suffixes.
    """
    df.insert(2, "Lemma_bereinigt", None)

    for index, row in df.iterrows():
        lemma_string = str(row['Lemma'])
        lemma_list = [w.strip() for w in re.split(r'[;,]', lemma_string)]

        normalized = []
        i = 0
        while i < len(lemma_list):
            current = remove_roman_numerals(lemma_list[i])

            # Case 1: Broken first part (e.g. "Bampel-, Bämpeles-wirtschaft")
            if current.endswith('-') and i + 1 < len(lemma_list):
                next_ = lemma_list[i + 1].strip()
                suffix = next_.split('-', 1)[1] if '-' in next_ else next_
                combined = current[:-1] + suffix
                combined = combined.replace('--', '-')
                for lemma in [combined, next_.replace('-', '')]:
                    for expanded in expand_parentheses_ordered(lemma):
                        if expanded not in normalized:
                            normalized.append(expanded)
                i += 2
                continue

            # Case 2: Broken first part at end (e.g. "Holderblüten-tee, Holunderblüten-")
            elif current.endswith('-') and i == len(lemma_list) - 1 and i > 0:
                previous = lemma_list[i - 1]
                if '-' in previous:
                    suffix = previous.split('-', 1)[1]
                    combined = current[:-1] + suffix
                    for expanded in expand_parentheses_ordered(combined):
                        if expanded not in normalized:
                            normalized.append(expanded)
                i += 1
                continue

            # Case 3: Suffix starting with '-' (e.g. "-schluck")
            elif current.startswith('-') and i > 0:
                base = lemma_list[i - 1].split('-')[0].strip()
                combined = base + current[1:]
                for expanded in expand_parentheses_ordered(combined):
                    if expanded not in normalized:
                        normalized.append(expanded)
                i += 1
                continue

            # Normal case: delete '-'
            else:
                cleaned = current.replace('-', '')
                for expanded in expand_parentheses_ordered(cleaned):
                    if expanded not in normalized:
                        normalized.append(expanded)
                i += 1

        df.at[index, 'Lemma_bereinigt'] = ', '.join(normalized)

    return df

# ================================================================
# Function: normalize_definition
# Purpose:  Cleans the 'Definition' column according to specific rules
# ================================================================
def normalize_definition(df):
    """
    Cleans the 'Definition' column by removing annotations, specific patterns,
    and replacing abbreviations with full words. If definition starts with
    "wie schd", it replaces with normalized lemmata.
   """
    pattern = r'\((sch|RA|BR|KR|W|Verb\.)\)|\(\?\)|wie schd »?|RA|/|\(|\)|\.{3}'
    bereinigt_list = []

    for index, row in df.iterrows():
        def_string = str(row['Definition'])

        if def_string.strip().startswith("wie schd"):
            lemmata_clean = row['Lemma_bereinigt']
            if isinstance(lemmata_clean, list):
                lemmata_str = ", ".join(lemmata_clean)
            else:
                lemmata_str = str(lemmata_clean)
            bereinigt_list.append(lemmata_str)
        else:
            cleaned = re.sub(pattern, '', def_string).strip()
            bereinigt_list.append(cleaned)

    df.insert(6, 'Definition_bereinigt', bereinigt_list)

    # Additional replacements
    df['Definition_bereinigt'] = df['Definition_bereinigt'].str.replace(r'FlN', 'Flurname', regex=True)
    df['Definition_bereinigt'] = df['Definition_bereinigt'].str.replace(r'Neckn', 'Neckname', regex=True)
    df['Definition_bereinigt'] = df['Definition_bereinigt'].str.replace(r'Kr\.', 'Kreis', regex=True)

    return df

# ================================================================
# Function: save_df
# Purpose:  Saves the DataFrame to a TSV file
# ================================================================
def save_df(df, output_file):
    """
    Saves DataFrame to TSV with UTF-8 encoding.
    """
    df.to_csv(output_file, sep='\t', index=False, encoding='utf-8')

# ================================================================
# Function: process_all_files
# Purpose:  Processes all TSV files in input directory and saves normalized versions
# ================================================================
def process_all():
    # if not exists, create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Output paths
    output_file_1 = os.path.join(output_dir, "definitionen_A.tsv")
    output_file_2 = os.path.join(output_dir, "definitionen_B.tsv")

    tsv_dateien = glob.glob(os.path.join(input_dir, "*.tsv"))
    alle_daten = []

    for datei in tsv_dateien:
        try:
            df = pd.read_csv(datei, sep='\t', encoding='utf-8', dtype=str)
            alle_daten.append(df)
        except Exception as e:
            print(f"Fehler bei Datei {datei}: {e}")

    # Merge
    gesamt_df = pd.concat(alle_daten, ignore_index=True)

    # Normalize
    gesamt_df = normalize_lemmata(gesamt_df)
    gesamt_df = normalize_definition(gesamt_df)

    # Keep only column with normalized definitions
    final_df = gesamt_df[['Konzept', 'Definition_bereinigt']].rename(columns={'Definition_bereinigt': 'Definition'})

    # Remove identical rows
    final_df.drop_duplicates(subset=['Definition', 'Konzept'], inplace=True)

    # Grouping
    def vereinige_konzepte(konzept_series):
        konzept_liste = konzept_series.dropna().astype(str).tolist()
        teilstrings = set()
        for eintrag in konzept_liste:
            teile = re.split(r'[;,]', eintrag)
            teilstrings.update(t.strip() for t in teile if t.strip())
        return '; '.join(sorted(teilstrings))

    final_df = final_df.groupby('Definition', as_index=False).agg({
        'Konzept': vereinige_konzepte
    })

    # Split in concept groups
    df_kein_trinken = final_df[final_df['Konzept'].str.contains(r'kein_Trinken', na=False)]
    df_andere = final_df[~final_df['Konzept'].str.contains(r'kein_Trinken', na=False)]

    # Save in output folder
    df_andere.to_csv(output_file_1, sep='\t', index=False, encoding='utf-8')
    df_kein_trinken.to_csv(output_file_2, sep='\t', index=False, encoding='utf-8')

    print(f"Done! Files saved in folder '{output_dir}'")

# ================================================================
# Main execution
# ================================================================
if __name__ == "__main__":
    process_all()

