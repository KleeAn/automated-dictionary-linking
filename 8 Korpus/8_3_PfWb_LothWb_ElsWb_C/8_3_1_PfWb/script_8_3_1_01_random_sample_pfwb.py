# ================================================================
# Script for random selection and filtering of valid lines from
# PfWb Post data.
# ================================================================

import os
import random
import re

# ================================================================
# Constants
# Purpose: Define exclusion criteria for filtering
# ================================================================
excluded_semantic_groups = {'5920', '5925', '7455', '7470'}

excluded_grammatical_elements = [
    "Adv", "adv", "Art", "Fragepron", "Indefinitpro", "Inter",
    "Konj", "Koselaut", "Negationspartikel", "Num", "Partikel",
    "Possessivpro", "Pron", "Präfix", "Präp", "Reflexivpron",
    "Schallw", "Zahlwort"
]

# ================================================================
# Function: is_valid_line
# Purpose: Checks if a line passes grammatical and semantic filters
# ================================================================
def is_valid_line(line):
    """
    Determines whether a line is valid based on grammatical and
    semantic exclusion criteria.
    """
    grammar_match = re.search(r'\|(.*?)\\', line)
    if not grammar_match:
        return False
    grammar = grammar_match.group(1).lower()
    if any(excluded in grammar for excluded in excluded_grammatical_elements):
        return False

    semantic_match = re.search(r'#(\d+)', line)
    if not semantic_match:
        return False
    semantic_group = semantic_match.group(1)
    return semantic_group not in excluded_semantic_groups

# ================================================================
# Function: main
# Purpose: Selects valid lines from input files and
#          writes them to a single output file.
# ================================================================
def main(output_path, input_dir):
    """
    Collects and filters lines from all .txt files in a directory,
    randomly samples valid entries, and writes them to
    an output file.
    """
    files = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if f.endswith('.txt')
    ]

    valid_lines = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and is_valid_line(line):
                    valid_lines.append(line)

    if len(valid_lines) < 1000:
        print(f"Only {len(valid_lines)} valid lines found.")
        selected_lines = valid_lines
    else:
        selected_lines = random.sample(valid_lines, 1000)

    with open(output_path, 'w', encoding='utf-8') as f:
        for line in selected_lines:
            f.write(line + '\n')

    print(f"{len(selected_lines)} lines written to '{output_path}'")



