# ================================================================
# Functions for processing string matching.
# ================================================================

import re
import csv

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
# Function: extract_all_terms_flat
# Purpose: Convert a concept-to-terms mapping into a flat list of unique terms
# ------------------------------------------------------------
def extract_all_terms_flat(concept_mapping):
    """
    Converts a mapping of the form {Concept: [Term1, Term2, ...]} into
    a flat, deduplicated list of terms.
    """
    term_set = set()
    for term_list in concept_mapping.values():
        for term in term_list:
            term_set.add(term.strip())
    return list(term_set)

import csv
import re

# ------------------------------------------------------------
# Function: split_at_semicolon
# Purpose: Split a definition string at semicolons and remove extra spaces
# ------------------------------------------------------------
def split_at_semicolon(definition):
    return [part.strip() for part in definition.split(';') if part.strip()]


# ------------------------------------------------------------
# Function: split_at_comma_safely
# Purpose: Split text at commas, but avoid splitting before relative pronouns
# ------------------------------------------------------------
def split_at_comma_safely(text):
    relative_pronouns = [
        'der', 'die', 'das', 'welcher', 'welche', 'welches',
        'dem', 'den', 'dessen', 'deren'
    ]
    parts = []
    current = ''
    tokens = re.split(r'(,\s*)', text)

    for i in range(0, len(tokens), 2):
        part = tokens[i]
        sep = tokens[i + 1] if i + 1 < len(tokens) else ''
        lookahead = tokens[i + 2] if i + 2 < len(tokens) else ''
        lookahead_word = lookahead.strip().split(' ')[0] if lookahead else ''

        # If the next word is a relative pronoun, keep the comma
        if lookahead_word.lower() in relative_pronouns:
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
# Purpose: Split a definition string first at semicolons, then at commas safely
# ------------------------------------------------------------
def process_definition(definition):
    if not definition:
        return []
    semicolon_parts = split_at_semicolon(definition)
    final_parts = []
    for part in semicolon_parts:
        final_parts.extend(split_at_comma_safely(part))
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
# Purpose: Read a TSV file, split 'Definition' values, and add a 'Definition_gesplittet' column
# ------------------------------------------------------------
def process_tsv_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', newline='') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile, delimiter='\t')
        original_fieldnames = reader.fieldnames

        if 'Definition' not in original_fieldnames:
            raise ValueError("Column 'Definition' not found!")

        # Add new column right after 'Definition'
        fieldnames = insert_column_after(original_fieldnames, 'Definition', 'Definition_gesplittet')
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        for row in reader:
            definition = row.get('Definition', '')
            splitted = process_definition(definition)
            row['Definition_gesplittet'] = str(splitted)
            reordered_row = {key: row.get(key, '') for key in fieldnames}
            writer.writerow(reordered_row)

