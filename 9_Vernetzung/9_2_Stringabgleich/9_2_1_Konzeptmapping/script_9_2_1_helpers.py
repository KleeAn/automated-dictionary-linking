# ================================================================
# Functions for processing string matching.
# ================================================================

import csv
import re

# ------------------------------------------------------------
# Function: extract_concepts_and_terms
# Purpose: Recursively extract concepts and associated terms from nested JSON nodes
# ------------------------------------------------------------
def extract_concepts_and_terms(json_nodes, current_path=None, mapping=None):
    if mapping is None:
        mapping = {}
    if current_path is None:
        current_path = []


    # Regex pattern for articles, pronouns, and "sich" at sentence start
    articles_and_pronouns = [
        r"(?:ein(?:e|en|em|es)?|der|die|das|dem|den|des|sein(?:e|en|em|es)?|"
        r"ihr(?:e|en|em|es)?|mein(?:e|en|em|es)?|dein(?:e|en|em|es)?|"
        r"unser(?:e|en|em|es)?|euer(?:e|en|em|es)?)"
    ]
    pattern = re.compile(rf"^(sich(?:\s+))?({'|'.join(articles_and_pronouns)}(?:\s+))*", re.IGNORECASE)

    for key, value in json_nodes.items():
        if key == "Begriffe":
            concept = ".".join(current_path)

            # Ensure concept is initialized as a dict
            if concept not in mapping or not isinstance(mapping[concept], dict):
                mapping[concept] = {}

            terms = value if isinstance(value, list) else [value]
            for term in terms:
                single_terms = term if isinstance(term, list) else [term]

                for t in single_terms:
                    # Add original term
                    mapping[concept][t] = None

                    # Clean term by removing articles/pronouns and add it if different
                    cleaned = pattern.sub("", t).strip()
                    if cleaned and cleaned.lower() != t.lower():
                        mapping[concept][cleaned] = None
        elif isinstance(value, dict):
            # Recursive call for nested dicts
            extract_concepts_and_terms(value, current_path + [key], mapping)

    # After recursion: convert dictionaries to lists of keys
    for k in mapping:
        if isinstance(mapping[k], dict):
            mapping[k] = list(mapping[k].keys())

    return mapping

# ------------------------------------------------------------
# Function: split_at_semicolon
# Purpose: Split a definition string at semicolons
# ------------------------------------------------------------
def split_at_semicolon(definition):
    return [part.strip() for part in definition.split(';') if part.strip()]

# ------------------------------------------------------------
# Function: split_at_comma
# Purpose: Split text at commas, respecting relative pronouns to avoid incorrect splits
# ------------------------------------------------------------
def split_at_comma(text):
    relative_pronouns = ['der', 'die', 'das', 'welcher', 'welche', 'welches', 'dem', 'den', 'dessen', 'deren']
    parts = []
    current = ''
    tokens = re.split(r'(,\s*)', text)
    for i in range(0, len(tokens), 2):
        part = tokens[i]
        sep = tokens[i + 1] if i + 1 < len(tokens) else ''
        lookahead = tokens[i + 2] if i + 2 < len(tokens) else ''
        lookahead_word = lookahead.strip().split(' ')[0] if lookahead else ''
        if lookahead_word.lower() in relative_pronouns:
            # Do not split at this comma if followed by a relative pronoun
            current += part + sep
        else:
            if current:
                current += part
                parts.append(current.strip())
                current = ''
            else:
                parts.append(part.strip())
    if current:
        parts.append(current.strip())
    return parts

# ------------------------------------------------------------
# Function: process_definition
# Purpose: Split a definition string first at semicolons, then at commas
# ------------------------------------------------------------
def process_definition(definition):
    if not definition:
        return []
    semicolon_parts = split_at_semicolon(definition)
    final_parts = []
    for part in semicolon_parts:
        final_parts.extend(split_at_comma(part))
    return [p for p in final_parts if p]


# ------------------------------------------------------------
# Function: insert_column_after
# Purpose: Insert a new column into a list of field names after a specified existing column
# ------------------------------------------------------------
def insert_column_after(fields, insert_after, new_column):
    new_fields = []
    for field in fields:
        new_fields.append(field)
        if field == insert_after:
            new_fields.append(new_column)
    return new_fields


# ------------------------------------------------------------
# Function: process_tsv_file
# Purpose: Read a TSV file, process definitions by splitting them, and write output with additional column
# ------------------------------------------------------------
def process_tsv_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', newline='') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile, delimiter='\t')
        original_fieldnames = reader.fieldnames

        if 'Definition' not in original_fieldnames:
            raise ValueError("Spalte 'Definition' nicht gefunden!")

        fieldnames = insert_column_after(original_fieldnames, 'Definition', 'Definition_gesplittet')
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        for row in reader:
            definition = row.get('Definition', '')
            splitted = process_definition(definition)
            row['Definition_gesplittet'] = str(splitted)
            reordered_row = {key: row.get(key, '') for key in fieldnames}
            writer.writerow(reordered_row)
