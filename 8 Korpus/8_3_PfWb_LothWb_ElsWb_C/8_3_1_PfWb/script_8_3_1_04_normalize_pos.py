# ================================================================
# Script for mapping grammatical information to POS.
# ================================================================

import pandas as pd

# ================================================================
# Mapping: Grammatical indications to POS
# ================================================================
pos_mapping = {
    '(f)': 'Substantiv',
    'f': 'Substantiv',
    '(m)': 'Substantiv',
    'm': 'Substantiv',
    'm?': 'Substantiv',
    'n': 'Substantiv',
    'Pl': 'Substantiv',
    'subst': 'Substantiv',
    'Adj': 'Adjektiv',
    'Adv': 'Adverb',
    'Gen?': 'Substantiv',
    'schw': 'Verb',
    'st': 'Verb',
    'st (schw)': 'Verb',
}

# ================================================================
# Function: determine_pos
# Purpose: Maps grammatical info to POS
# ================================================================
def determine_pos(entry):
    entry = str(entry).strip()
    for key, pos in pos_mapping.items():
        if key in entry:
            return pos
    return ''

# ================================================================
# Function: process_file_pandas
# Purpose: Reads TSV input into DataFrame, inserts 'Wortart' column
# ================================================================
def process_file_pandas(input_path, output_path):
    df = pd.read_csv(input_path, delimiter='\t', encoding='utf-8')

    if 'POS' not in df.columns:
        raise Exception("Column 'POS' not found!")

    # New column 'Wortart'
    df['Wortart'] = df['POS'].apply(determine_pos)

    # Place column 'Wortart' after 'POS'
    cols = list(df.columns)
    pos_index = cols.index('POS')
    cols.remove('Wortart')
    cols.insert(pos_index + 1, 'Wortart')
    df = df[cols]

    # Delete column 'POS'
    df = df.drop(columns=['POS'])

    # Save to TSV
    df.to_csv(output_path, sep='\t', index=False, encoding='utf-8')

# ================================================================
# Main execution
# ================================================================
def main(prefix):
    input_file = f"output/{prefix}_mapped.tsv"
    output_file = f"output/{prefix}_prepared.tsv"
    process_file_pandas(input_file, output_file)
    print(f"File successfully processed and saved as '{output_file}'.")

#main()
