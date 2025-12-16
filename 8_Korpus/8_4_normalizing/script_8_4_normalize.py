# ================================================================
# Script for normalizing lemmata and definitions.
# Reads input TSV files, processes lemmata and definitions, and saves output.
# ================================================================

import pandas as pd
import re
import os

input_dir = "Input"
output_dir = "Output"

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
# Purpose:  Removes Roman numerals (I, II, III) at the end of a word
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
    'wie schd', it replaces the content with normalized lemmata.
    """
    # Base cleanup pattern: removes editorial tags and noise
    base_pattern = r'\bwie schd »?|\(sch\)|\(RA\)|\(BR\)|\(KR\)|\(W\)|\(Verb\.\)|\(\?\)|\bRA\b|\bBR\b|\bKR\b|/|\.{3}'

    # Extended pattern: removes bracketed expressions ending in "spr", "sprache", "wort"
    # and specific stylistic or derogatory labels
    remove_parentheses_pattern = (
        r'\((?:[^)]*?(spr(ache)?|wort)[^)]*?)\)'  # e.g., (Händlerspr), (Musikantensprache)
        r'|\(abfällig\)'
        r'|\(abschätzig\)'
        r'|\(scherzh\)'
        r'|\(scherzhaft\)'
        r'|\(spöttisch\)'
        r'|\(verächtlich\)'
        r'|\(abwertend\)'
    )

    # Combine both regex patterns
    combined_pattern = f'{base_pattern}|{remove_parentheses_pattern}'

    bereinigt_list = []

    for index, row in df.iterrows():
        def_string = str(row['Definition'])

        # Replace with normalized lemmata if definition starts with "wie schd"
        if def_string.strip().lower().startswith("wie schd"):
            lemmata_clean = row['Lemma_bereinigt']
            if isinstance(lemmata_clean, list):
                lemmata_str = ", ".join(lemmata_clean)
            else:
                lemmata_str = str(lemmata_clean)
            bereinigt_list.append(lemmata_str)
        else:
            # Apply cleanup regex
            cleaned = re.sub(combined_pattern, '', def_string, flags=re.IGNORECASE).strip()
            bereinigt_list.append(cleaned)

    # Insert cleaned definitions into new column
    df.insert(6, 'Definition_bereinigt', bereinigt_list)

    # Additional targeted string replacements
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
    
    Parameters:
        df (pd.DataFrame): DataFrame to save.
        output_file (str): Path to output TSV.
    """
    df.to_csv(output_file, sep='\t', index=False, encoding='utf-8')

# ================================================================
# Function: process_all_files
# Purpose:  Processes all TSV files in input directory and saves normalized versions
# ================================================================
def process_all_files():
    """
    Processes all .tsv files in the input directory:
    - Reads each file
    - Normalizes lemmata and definitions
    - Drops old 'Definition' column and renames cleaned column
    - Saves output in output directory
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".tsv"):
            input_path = os.path.join(input_dir, filename)
            output_name = filename.replace(".tsv", "_normalized.tsv")
            output_path = os.path.join(output_dir, output_name)

            print(f"Processing file: {filename}")
            df = read_tsv(input_path)
            df = normalize_lemmata(df)
            df = normalize_definition(df)

            # Remove original 'Definition' column and rename cleaned one
            df.drop(columns=['Definition'], inplace=True)
            df.rename(columns={'Definition_bereinigt': 'Definition'}, inplace=True)

            save_df(df, output_path)
            print(f"Saved as: {output_path}")

# ================================================================
# Main execution
# ================================================================
if __name__ == "__main__":
    process_all_files()


