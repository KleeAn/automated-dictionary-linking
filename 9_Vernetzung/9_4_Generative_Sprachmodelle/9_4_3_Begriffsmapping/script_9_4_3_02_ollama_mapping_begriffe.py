# ================================================================
# Script 2: Mapping lexical units to beverage terms
# ================================================================

import csv
import json
import re
from pathlib import Path
from ollama import chat
from ollama import ChatResponse

# Increase field size limit
csv.field_size_limit(100_000_000)

# ------------------------------------------------------------
# Function: flatten_terms
# Purpose: Helper function: recursive flattening of lists
# ------------------------------------------------------------
def flatten_terms(terms) -> list[str]:
    flat = []
    for t in terms:
        if isinstance(t, list):
            flat.extend(flatten_terms(t))
        else:
            flat.append(str(t))
    return flat

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
            term = row.get('Begriff', '').strip()

            if lemma and definition:
                entries.append((xml_id, lemma, pos, definition, concept_gold, concept_root, term))
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
# Purpose: Recursively extract concept names and terms
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
# Function: get_terms_with_subconcepts
# Purpose: Collect all terms of a concept, including sub-concepts
# ------------------------------------------------------------
def get_terms_with_subconcepts(concept_root: str, concepts_terms: dict[str, list[str]]) -> list[str]:
    """
    Liefert alle Begriffe für concept_root inklusive aller Unterkonzepte.
    """
    terms = []
    for concept, concept_terms in concepts_terms.items():
        # concept matches or is a subconcept
        if concept == concept_root or concept.startswith(concept_root + "."):
            terms.extend(flatten_terms(concept_terms))
    return terms

# ------------------------------------------------------------
# Function: build_prompt
# Purpose: Create a prompt with concepts and terms
# ------------------------------------------------------------
def build_prompt_terms_for_concept(lemma: str, definition: str,
                                   concept_root: str,
                                   concepts_terms: dict[str, list[str]],
                                   prompt_template: str) -> str:

    flat_terms = get_terms_with_subconcepts(concept_root, concepts_terms)

    term_list = "- " + "\n- ".join(sorted(set(flat_terms))) if flat_terms else "[keine Begriffe verfügbar]"

    prompt = prompt_template.format(
        lemma=lemma,
        definition=definition,
        begriffsliste=term_list
    )
    return prompt

# ------------------------------------------------------------
# Function: validate_answer_terms
# Purpose: Validate if LLM answer contains allowed terms
# ------------------------------------------------------------
def validate_answer_terms(answer: str, allowed_terms: list[str]) -> str | None:
    if not answer:
        return "[ungültig]"

    # Mehrere Antworten an ; splitten
    parts = [p.strip().strip('". ') for p in answer.split(';')]

    if not parts:
        return "[ungültig]"

    terms_lower = {t.lower(): t for t in allowed_terms}
    valid_parts = []

    for p in parts:
        if p.lower() in terms_lower:
            valid_parts.append(terms_lower[p.lower()])
        else:
            print(f"No valid term: '{p}'")

    if valid_parts:
        return "; ".join(valid_parts)
    else:
        return "[ungültig]"


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
# Function: run_mapping_begriffe
# Purpose: Main process: Calling up all files and mapping lexical units
# ------------------------------------------------------------
def run_mapping_begriffe(files: list[str], input_folder: Path,
                         json_path: Path, model_name: str,
                         prompt_text: str) -> list[Path]:
    json_data = load_concept_vocab(json_path)
    concept_mapping = extract_concepts_and_terms(json_data)
    
    vocab_terms = []
    for terms in concept_mapping.values():
        vocab_terms.extend(flatten_terms(terms))

    generated_files = []

    for file_name in files:
        tsv_file = input_folder / file_name
        if not tsv_file.exists():
            print(f"File not found: {tsv_file}")
            continue

        print(f"Processing file: {tsv_file.name}")
        entries = read_tsv(tsv_file)
        results = []

        for xml_id, lemma, pos, definition, concept_gold, concept_root, term in entries:
            if concept_root in ("kein_Trinken", "[ungültig]"):
                results.append({
                    "xml:id": xml_id,
                    "Lemma": lemma,
                    "Wortart": pos,
                    "Definition": definition,
                    "Konzept": concept_gold,
                    "Begriff": term,
                    "Konzept_gemappt": concept_root,   
                    "Begriff_gemappt": "[ungültig]",             
                    "Antwort_Modell": ""
                })
                continue

            prompt = build_prompt_terms_for_concept(lemma, definition, concept_root, concept_mapping, prompt_text)

            answer_model = get_answer(prompt, model_name)
            allowed_terms = get_terms_with_subconcepts(concept_root, concept_mapping)
            answer_verified = validate_answer_terms(answer_model, vocab_terms)

            concept_basic = answer_verified or "[ungültig]"
            results.append({
                "xml:id": xml_id,
                "Lemma": lemma,
                "Wortart": pos,
                "Definition": definition,
                "Konzept": concept_gold,
                "Begriff": term,
                "Konzept_gemappt": concept_root,
                "Begriff_gemappt": concept_basic,
                "Antwort_Modell": answer_model
            })

            print(f"{xml_id} | {lemma} → {concept_basic or '[ungültig]'}")

        output_file = input_folder / f"{tsv_file.stem.replace('_basiskonzepte','_begriffe')}.tsv"
        write_results(output_file, results)
        generated_files.append(output_file)
        print(f"Results saved in: {output_file}\n")

    return generated_files
