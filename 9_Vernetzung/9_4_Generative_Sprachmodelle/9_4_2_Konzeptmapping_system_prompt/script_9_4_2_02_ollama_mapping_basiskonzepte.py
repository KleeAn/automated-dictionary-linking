# ================================================================
# Script 2: Mapping lexical units to Basiskonzepte
# with a combination of system and user prompt
# ================================================================

import csv
import json
import re
from typing import Any
from pathlib import Path
from ollama import chat
from ollama import ChatResponse


# Increase field size limit
csv.field_size_limit(100_000_000)

# ------------------------------------------------------------
# Function: read_tsv
# Purpose: Load TSV file and extract relevant entries
# -------------------------------------------------------------
def read_tsv(filepath: str) -> list[tuple[str, str, str, str]]:
    entries = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            xml_id = row.get('xml:id', '').strip()
            lemma = row.get('Lemma', '').strip()
            pos = row.get('Wortart', '').strip()
            definition = row.get('Definition', '').strip()
            concept_gold = row.get('Konzept', '').strip()
            concept_root = row.get('Konzept_gemappt', '').strip()
            
            # replace "[ungültig]" with "kein_Trinken" if entry belongs to "Trinken"
            if concept_root == "[ungültig]":
                if concept_gold == "kein_Trinken":
                    pass
                else:
                    concept_root = "kein_Trinken"   
                
            if lemma and definition:
                entries.append((xml_id, lemma, pos, definition, concept_gold, concept_root))
    return entries

# ------------------------------------------------------------
# Function: load_concept_vocab
# Purpose: Load JSON vocabulary for concepts
# ------------------------------------------------------------
def load_concept_vocab(json_path: str) -> dict:
    with open(json_path, mode='r', encoding='utf-8') as f:
        return json.load(f)

# ------------------------------------------------------------
# Function: extract_concepts_and_terms
# Purpose: Recursively extract concepts and associated terms
# ------------------------------------------------------------
def extract_concepts_and_terms(json_knoten: dict, current_path=None, mapping=None) -> dict[str, list[str]]:
    if mapping is None:
        mapping = {}
    if current_path is None:
        current_path = []

    for key, value in json_knoten.items():
        new_path = current_path + [key]

        if key == "Begriffe":
            concept = ".".join(current_path)
            mapping.setdefault(concept, [])
            terms = value if isinstance(value, list) else [value]
            mapping[concept].extend(terms)

        elif isinstance(value, dict):
            extract_concepts_and_terms(value, new_path, mapping)

    return mapping

# ------------------------------------------------------------
# Function: get_all_concepts
# Purpose: Extract concept names from vocabulary
# ------------------------------------------------------------
def get_all_concepts(concept_mapping: dict[str, list[str]]) -> list[str]:
    return list(concept_mapping.keys())

# ------------------------------------------------------------
# Function: build_system_prompt
# Purpose: Create a system prompt by loading a template and
#          filling in the placeholder with the concept list. 
# ------------------------------------------------------------
def build_system_prompt(concepts_terms: dict[str, list[str]], prompt_template: str, with_terms: bool = False) -> str:
    concept_list = ""

    def flatten_terms(terms):
        flat = []
        for b in terms:
            if isinstance(b, list):
                flat.extend(flatten_terms(b))
            else:
                flat.append(str(b))
        return flat

    concept_list = ""
    for concept, terms in concepts_terms.items():
        if with_terms and terms:  # Begriffe nur, wenn Flag gesetzt
            flat_terms = flatten_terms(terms)
            terms_str = ", ".join(flat_terms)
            concept_list += f"- {concept}: {terms_str}\n"
        else:
            concept_list += f"- {concept}\n"

    prompt = prompt_template.format(
        konzeptliste=concept_list
    )
    return prompt

# ------------------------------------------------------------
# Function: build_prompt
# Purpose: Create a user prompt by loading a template and
# filling in the placeholders with lemma and definition
# ------------------------------------------------------------
def build_prompt(lemma: str, definition: str) -> str:
    template_prompt = "**Dictionary entry**:\n\nHeadword: {lemma}\nDefinition: {definition}"
    
    prompt = template_prompt.format(
        lemma=lemma,
        definition=definition
    )
    return prompt


# ------------------------------------------------------------
# Function: find_longest_substring
# Purpose: Helper function: Returns the longest substring
# from 'substrings' that is contained in 'text'.
# ------------------------------------------------------------
def find_longest_substring(text: str, substrings: list[str]) -> str:
    matches = [s for s in substrings if s.lower() in text.lower()]
    if not matches:
        return ""
    return max(matches, key=len)

# ------------------------------------------------------------
# Function: validate_answer
# Purpose: Validate if LLM answer contains allowed concepts
# ------------------------------------------------------------
def validate_answer(answer: str, allowed_concepts: list[str]) -> str | None:
    if not answer:
        return "[ungültig]"
    parts = [p.strip() for p in answer.split(';') if p.strip()]
    if not parts:
        return "[ungültig]"

    allowed_concepts_lower = {c.lower(): c for c in allowed_concepts}
    valid_parts = []
    for part in parts:
        key = part.lower()
        if key in allowed_concepts_lower:
            valid_parts.append(allowed_concepts_lower[key])
        else:
            # check for substrings
            match = find_longest_substring(part, allowed_concepts)
            if match:
                valid_parts.append(match)
            else:
                print(f"No valid concept: '{part}'")
    
    # check whether response ends on a concept name
    if not valid_parts:
        cleaned_answer = answer.strip().strip('". ')
        cleaned_answer_lower = cleaned_answer.lower()
        for concept in allowed_concepts:
            if (cleaned_answer_lower.endswith(concept.lower()) or
                cleaned_answer_lower == concept.lower()):
                return concept

        return "[ungültig]"
    
    valid_parts = list(dict.fromkeys(valid_parts))  
    return "; ".join(valid_parts)

def is_multiple_choice(answer: str) -> bool:
    return any(kw in answer.lower() for kw in [" und ", " oder ", ",", ";"])


# ------------------------------------------------------------
# Function: get_answer
# Purpose: Query LLM using Ollama
# ------------------------------------------------------------
def get_answer(system_prompt: str, prompt: str, model_name: str) -> str:
    try:
        response: ChatResponse = chat(
            model=model_name,
            messages=[{'role': 'system', 'content': system_prompt} ,{'role': 'user', 'content': prompt}]
        )
        answer = response.message.content.strip()
        # Delete <think>-parts if existing (escpecially in deepseek-answers)
        answer_cleaned = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL)
        return answer_cleaned.strip()
    except Exception as e:
        return f"[Error when calling model: {e}]"

# ------------------------------------------------------------
# Function: write_results
# Purpose: Write results to TSV file
# ------------------------------------------------------------
def write_results(filename: Path, results: list[dict[str, str]]):
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

# ------------------------------------------------------------
# Function: run_mapping_basiskonzepte
# Purpose: Main process: Calling up all files and mapping lexical units
# ------------------------------------------------------------
def run_mapping_basiskonzepte(files: list[str], input_folder: Path,
                              json_path: Path, model_name: str,
                              system_prompt_text: str, with_terms: bool = False) -> list[Path]:
    json_data = load_concept_vocab(json_path)
    concept_mapping = extract_concepts_and_terms(json_data)
    all_concepts = list(concept_mapping.keys())

    generated_files = []

    for file_name in files:
        tsv_file = input_folder / file_name
        if not tsv_file.exists():
            print(f"File not found: {tsv_file}")
            continue

        print(f"Processing file: {tsv_file.name}")
        entries = read_tsv(tsv_file)
        results = []

        for xml_id, lemma, pos, definition, concept_gold, concept_root in entries:
            if concept_root in ("kein_Trinken", "[ungültig]"):
                results.append({
                    "xml:id": xml_id,
                    "Lemma": lemma,
                    "Wortart": pos, 
                    "Definition": definition,
                    "Konzept": concept_gold,
                    "Konzept_gemappt": concept_root,
                    "Antwort_Modell": ""
                })
                continue

            system_prompt = build_system_prompt(concept_mapping, system_prompt_text, with_terms=with_terms)
            prompt = build_prompt(lemma, definition)
            
            answer_model = get_answer(system_prompt, prompt, model_name)
            answer_verfied = validate_answer(answer_model, all_concepts)

            concept_basic = answer_verfied or ""
            answer_column = "" if answer_verfied else answer_model

            results.append({
                "xml:id": xml_id,
                "Lemma": lemma,
                "Wortart": pos,
                "Definition": definition,
                "Konzept": concept_gold,
                "Konzept_gemappt": concept_basic,
                "Antwort_Modell": answer_model
            })

            print(f"{xml_id} | {lemma} → {concept_basic or '[ungültig]'}")

        output_file_name = tsv_file.name.replace("_wurzelkonzepte", "_basiskonzepte")
        output_file = input_folder / output_file_name
        write_results(output_file, results)
        generated_files.append(output_file)
        print(f"Results saved in: {output_file}\n")

    return generated_files

