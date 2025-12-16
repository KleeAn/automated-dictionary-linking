# ================================================================
# Script 1: Mapping lexical units to Basiskonzepte
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
            term = row.get('Begriff', '').strip()
            
            if lemma and definition:
                entries.append((xml_id, lemma, pos, definition, concept_gold, term))
    return entries

# ------------------------------------------------------------
# Function: load_concept_vocab
# Purpose: Load JSON vocabulary for concepts
# ------------------------------------------------------------
def load_concept_vocab(json_path: str) -> dict:
    with open(json_path, mode='r', encoding='utf-8') as f:
        return json.load(f)

# ------------------------------------------------------------
# Function: extract_concepts
# Purpose: Recursively extract concept names
# ------------------------------------------------------------
def extract_concepts(json_knoten: dict, current_path=None, concepts=None) -> list[str]:
    if concepts is None:
        concepts = []
    if current_path is None:
        current_path = []

    for key, value in json_knoten.items():
        if key == "Begriffe":
            continue
        elif isinstance(value, dict):
            new_path = current_path + [key]
            # current concept
            concept_name = ".".join(new_path)
            concepts.append(concept_name)
            extract_concepts(value, new_path, concepts)

    return concepts

# ------------------------------------------------------------
# Function: get_all_concepts
# Purpose: Extract concept names from vocabulary
# ------------------------------------------------------------
def get_all_concepts(concept_mapping: dict[str, list[str]]) -> list[str]:
    return list(concept_mapping.keys())

# ------------------------------------------------------------
# Function: build_prompt
# Purpose: Create a prompt
# ------------------------------------------------------------
def build_prompt(lemma: str, definition: str, concepts_terms: dict[str, list[str]], prompt_template: str) -> str:
    concept_list = ""
    for concept in concepts_terms.keys():
        concept_list += f"- {concept}\n"

    prompt = prompt_template.format(
        lemma=lemma,
        definition=definition,
        konzeptliste=concept_list
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
def validate_answer(answer: str, allowed_concepts: list[str]) -> str:
    if not answer:
        return "[ungültig]"
    
    split_pattern = r"[;\n,]| und | oder "
    parts = [p.strip() for p in re.split(split_pattern, answer) if p.strip()]
    
    allowed_concepts_lower = {c.lower(): c for c in allowed_concepts}
    valid_parts = []
    
    for part in parts:
        key = part.lower()
        if key in allowed_concepts_lower:
            valid_parts.append(allowed_concepts_lower[key])
        else:
            match = find_longest_substring(part, allowed_concepts)
            if match:
                valid_parts.append(match)
    
    if len(valid_parts) == 1:
        return valid_parts[0]
    else:
        return "[ungültig]"

def is_multiple_choice(answer: str) -> bool:
    return any(kw in answer.lower() for kw in [" und ", " oder ", ",", ";"])

# ------------------------------------------------------------
# Function: get_answer
# Purpose: Query LLM using Ollama
# ------------------------------------------------------------
def get_answer(prompt: str, model_name: str) -> str:
    try:
        response: ChatResponse = chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        answer = response.message.content.strip()
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
def run_mapping_basiskonzepte(files: list[str], input_folder: Path, output_folder: Path,
                              json_path: Path, model_name: str,
                              prompt_text: str) -> list[Path]:
    json_data = load_concept_vocab(json_path)
    all_concepts = extract_concepts(json_data)

    generated_files = []

    for file_name in files:
        tsv_file = input_folder / file_name
        output_file = output_folder / (tsv_file.stem + "_basiskonzepte" + tsv_file.suffix)  
        if not tsv_file.exists():
            print(f"File not found: {tsv_file}")
            continue

        print(f"Processing file: {tsv_file.name}")
        entries = read_tsv(tsv_file)
        results = []

        for xml_id, lemma, pos, definition, concept_gold, term in entries:
            concept_list = "".join([f"- {c}\n" for c in all_concepts])
            prompt = prompt_text.format(
                lemma=lemma,
                definition=definition,
                konzeptliste=concept_list
            )

            answer_model = get_answer(prompt, model_name)
            answer_verified = validate_answer(answer_model, all_concepts)

            concept_basic = answer_verified or ""
            answer_column = "" if answer_verified else answer_model

            results.append({
                "xml:id": xml_id,
                "Lemma": lemma,
                "Wortart": pos,
                "Definition": definition,
                "Konzept": concept_gold,
                "Begriff": term,
                "Konzept_gemappt": concept_basic,
                "Antwort_Modell": answer_model
            })

            print(f"{xml_id} | {lemma} → {concept_basic or '[ungültig]'}")

        write_results(output_file, results)
        generated_files.append(output_file)
        print(f"Results saved in: {output_file}\n")

    return generated_files
