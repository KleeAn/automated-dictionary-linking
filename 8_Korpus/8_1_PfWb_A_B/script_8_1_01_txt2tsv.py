# ================================================================
# Script for the conversion of Post-data in TXT to TSV format.
# ================================================================

import re
import csv

# ================================================================
# Function: parse_line
# Purpose: Extracts components from a structured line using regex
# ================================================================
def parse_line(line):
    """
    Parses a single line of the input file and extracts:
    - lemma
    - structural level
    - grammatical information
    - definition

    Parameters:
        line (str): A line of text from the input file.

    Returns:
        tuple or None: A tuple with 4 extracted fields, or None if no match.
    """
    pattern = r"^(.*?)\s{2}(\S+)\s+\. (.*?) \.\s+(.*?)\s+#.*$"
    match = re.match(pattern, line)

    if match:
        lemma = match.group(1).strip()
        structure_level = match.group(2).strip()
        grammar_info = match.group(3).strip()
        definition = match.group(4).strip()
        return lemma, grammar_info, structure_level, definition
    return None

# ================================================================
# Function: process_file
# Purpose: Reads a file line-by-line and writes parsed results to TSV
# ================================================================
def process_file(input_file, output_file):
    """
    Processes the input text file and writes extracted entries to a TSV file.

    Parameters:
        input_file (str): Path to the input .txt file
        output_file (str): Path to the output .tsv file
    """
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8", newline="") as outfile:

        writer = csv.writer(outfile, delimiter="\t")
        # Write header row
        writer.writerow(["Lemma", "POS", "Level", "Definition"])

        for line in infile:
            parsed = parse_line(line)
            if parsed:
                writer.writerow(parsed)

# ================================================================
# Main execution
# ================================================================
def main(prefix):
    
    # File paths
    input_file = f"input/{prefix}.txt" 
    output_file = f"output/{prefix}.tsv"
    
    process_file(input_file, output_file)
    
    print(f"File successfully converted and saved to: '{output_file}'")

#main()
