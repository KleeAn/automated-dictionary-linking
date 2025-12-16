# ================================================================
# Script for matching the Post data with XML data of Pfälzisches
# Wörterbuch based on lemma and definition.
# ================================================================

import pandas as pd

# ================================================================
# Function: match_entries
# Purpose: Matches Post data with XML-based lemma data
# ================================================================

def match_entries(pfwb_xml_data_path, post_data_path, output_path):
    """
    Matches entries from XML dataset with post-processed TSV data,
    assigning XML ids where matches are found.

    Parameters:
        pfwb_xml_data_path (str): Path to the XML data TSV file.
        post_data_path (str): Path to the post-processed TSV file.
        output_path (str): Path where the matched output TSV will be saved.
    """
    # Load data
    xml_data = pd.read_csv(pfwb_xml_data_path, sep='\t')
    post_data = pd.read_csv(post_data_path, sep='\t')
    post_data.insert(0, 'xml:id', None)

    # Iterate through Post data
    for idx, row in post_data.iterrows():
        lemma = row['Lemma']
        definition = row['Definition']

        # Find lemma matches
        matches = xml_data[xml_data['Lemma'] == lemma]

        # Exactly one definition match
        if len(matches) == 1:
            match = matches.iloc[0]
            post_data.at[idx, 'xml:id'] = match['xml:id']

        # Multiple lemma matches, refine by definition
        elif len(matches) > 1:
            def_matches = matches[matches['Definition'] == definition]

            # Exactly one definition match
            if len(def_matches) == 1:
                def_match = def_matches.iloc[0]
                post_data.at[idx, 'xml:id'] = def_match['xml:id']
                
            # Multiple definition matches found; choose first by default
            elif len(def_matches) > 1:
                def_match = def_matches.iloc[0]
                post_data.at[idx, 'xml:id'] = def_match['xml:id']

            # No match by definition
            elif len(def_matches) == 0:
                # check if all lemma matches refer to same entry
                xml_ids = list(matches['xml:id'].unique())
                # lemmas all belong to the same entry
                if len(xml_ids) == 1:
                    match = matches.iloc[0]
                    post_data.at[idx, 'xml:id'] = match['xml:id']

    # Save results
    post_data.to_csv(output_path, sep='\t', index=False)
    print(f"Matching completed. File saved to: '{output_path}'")

# ================================================================
# Main execution
# ================================================================
def main(prefix):
    """
    Runs the matching process for a given prefix.
    """
    pfwb_xml_data_path = "input/pfwb_xml_example_data.tsv"
    post_data_path = f"output/{prefix}.tsv"
    output_path = f"output/{prefix}_mapped.tsv"

    match_entries(pfwb_xml_data_path, post_data_path, output_path)

# ================================================================
# Script entry point
# ================================================================
if __name__ == '__main__':
    prefix = "auswahl_pfwb_1000"  # define prefix here or pass dynamically
    main(prefix)
