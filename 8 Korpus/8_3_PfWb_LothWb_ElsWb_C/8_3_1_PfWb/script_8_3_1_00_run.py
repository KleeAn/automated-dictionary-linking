# ================================================================
# Script for executing a 4-step pipeline to generate a random sample
# of PfWb entries.
# ================================================================

import script_8_3_1_01_random_sample_pfwb
import script_8_3_1_02_txt2tsv
import script_8_3_1_03_xml_mapping
import script_8_3_1_04_normalize_pos
import os

# ================================================================
# Function: main
# Purpose: Coordinates execution of the processing pipeline
# ================================================================
def main(prefix):
    """
    Executes a processing pipeline consisting of 4 sequential scripts:
    1. Random selection and filtering of entries
    2. TXT to TSV conversion
    3. XML data matching
    4. POS normalization

    Parameters:
        prefix (str): Prefix for input/output file naming
    """

    print("Script 01: Random Sampling and Filtering")

    # Define paths
    input_data_path = "input/PfWb_Post"
    output_path = f"output/{prefix}.txt"

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Run Script 01
    script_8_3_1_01_random_sample_pfwb.main(output_path, input_data_path)

    # Check if output was successfully created
    if not os.path.exists(output_path):
        print(f"Datei '{output_path}' was not created")
        return

    print("Script 02: TXT → TSV conversion")
    script_8_3_1_02_txt2tsv.main(prefix)
    
    print("Script 03: Matching with XML data")
    script_8_3_1_03_xml_mapping.main(prefix)
    
    print("Script 04: POS mapping")
    script_8_3_1_04_normalize_pos.main(prefix)

    print("All steps completed successfully.")

# ================================================================
# Main execution
# ================================================================
if __name__ == '__main__':
    prefix = "zufallsauswahl_pfwb"
    main(prefix)
