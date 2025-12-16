# ================================================================
# Script 1: Mapping lexical units to Wurzelkonzepte (trinken, Getränk, Durst, kein_Trinken) with LLM support
# ================================================================

import csv
import json
import re
import os
from ollama import chat, ChatResponse
from pathlib import Path

# ------------------------------------------------------------
# Function: read_tsv
# Purpose: Load TSV file and extract relevant entries
# -------------------------------------------------------------
def read_tsv(filepath: str) -> list[tuple[str, str, str, str, str, str]]:
    entries = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            xml_id = row.get('xml:id', '').strip()
            lemma = row.get('Lemma', '').strip()
            pos = row.get('Wortart', '').strip()
            definition = row.get('Definition', '').strip()
            concept = row.get('Konzept', '').strip()
            if lemma and definition:
                entries.append((xml_id, lemma, pos, definition, concept))
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
            if concept not in mapping or not isinstance(mapping[concept], dict):
                mapping[concept] = {}

            terms = value if isinstance(value, list) else [value]
            for t in terms:
                if isinstance(t, list):
                    for item in t:
                        mapping[concept][str(item)] = None
                else:
                    mapping[concept][str(t)] = None

        elif isinstance(value, dict):
            extract_concepts_and_terms(value, new_path, mapping)

    for k in mapping:
        if isinstance(mapping[k], dict):
            mapping[k] = list(mapping[k].keys())

    return mapping

# ------------------------------------------------------------
# Function: build_prompt
# Purpose: Create a prompt by loading a template and filling in the placeholders with lemma, definition, and concept list. 
# ------------------------------------------------------------
def build_promp(template: str, lemma: str, definition: str, concepts_terms: dict[str, list[str]]) -> str:
    vocab_list = ""
    for concept, terms in concepts_terms.items():
        terms_str = ", ".join(terms) if terms else "[keine Begriffe]"
        vocab_list += f"- {concept}: {terms_str}\n"
    
    prompt = template.format(
        lemma=lemma,
        definition=definition,
        konzeptliste=vocab_list
    )
    return prompt

# ------------------------------------------------------------
# Function: validate_answer
# Purpose: Validate if LLM answer contains allowed concepts
# ------------------------------------------------------------
def validate_answer(answer: str) -> str | None:
    valid_classes = ["trinken", "Durst", "Getränk", "other"]
    if not answer:
        return None
    
    # normalization
    normalized = answer.strip()
    # remove possible markdown bold (**...**)
    normalized = re.sub(r"\*\*(.*?)\*\*", r"\1", normalized)
    # remove surrounding whitespace
    normalized = normalized.strip()
    
    # handle boxed notation (z.B. $\boxed{other}$)
    match_boxed = re.search(r"\\boxed\{(.*?)\}", normalized)
    if match_boxed:
        content = match_boxed.group(1).strip().strip('"\''"“”‘’")
        for cls in valid_classes:
            if content.lower() == cls.lower():
                return cls
    
    # remove possible quote marks
    stripped_quotes = normalized.strip('"\''"“”‘’")
    # check exact match
    for cls in valid_classes:
        if stripped_quotes.lower() == cls.lower():
            return cls
        
    # check whether response ends on a class
    for cls in valid_classes:
        if stripped_quotes.lower().endswith(cls.lower()):
            return cls
        # final "." allowed
        if stripped_quotes.lower().endswith(cls.lower() + "."):
            return cls
     
    return None

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
        # Delete <think>-parts if existing (escpecially in deepseek-answers)
        answer_cleaned = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL)
        return answer_cleaned.strip()
    except Exception as e:
        return f"[Error when calling model: {e}]"

# ------------------------------------------------------------
# Function: write_results
# Purpose: Write results to TSV file
# ------------------------------------------------------------
def write_results(filename: str, results: list[tuple[str, str, str, str, str, str, str]]):
    results = [
        (
            xml_id,
            lemma,
            pos,
            definition,
            concept_gold,
            "kein_Trinken" if mapped_concept == "other" else mapped_concept,
            answer_model
        )
        for xml_id, lemma, pos, definition, concept_gold, mapped_concept, answer_model in results
    ]

    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['xml:id', 'Lemma', 'Wortart', 'Definition', 'Konzept', 'Konzept_gemappt', 'Antwort_Modell'])
        writer.writerows(results)

# ------------------------------------------------------------
# Function: run_mapping_basiskonzepte
# Purpose: Main process: Calling up all files and mapping lexical units
# ------------------------------------------------------------
def run_mapping_wurzelkonzepte(input_folder: Path, output_folder: Path,
                               json_path: Path, model_name: str,
                               files_to_process: list[str] | None = None,
                               prompt_text: str = None) -> list[Path]:

    if prompt_text is None:
        raise ValueError("prompt_text muss be passed!")

    json_daten = load_concept_vocab(json_path)
    concept_mapping = extract_concepts_and_terms(json_daten)

    all_files = [f for f in os.listdir(input_folder) if f.endswith(".tsv")]
    files = files_to_process if files_to_process else all_files
    
    generated_files: list[Path] = []
    
    # Mapping model name
    model_map = {
        "llama3.3:70b": "llama_70b",
        "qwen2.5:72b": "qwen_72b",
        "deepseek-r1:70b": "deepseek_70b",
        "llama3.1:8b": "llama_8b",
        "qwen2.5:32b": "qwen_32b",
        "deepseek-r1:32b": "deepseek_32b",
    }
    model_hint = model_map.get(model_name, "unknown")

    for file in files:
        tsv_path = Path(input_folder) / file
        output_path = Path(output_folder) / f"{Path(file).stem}_{model_hint}_wurzelkonzepte.tsv"
        
        entries = read_tsv(tsv_path)
        results = []

        for xml_id, lemma, pos, definition, concept_gold in entries:
            # generate prompt
            prompt = build_promp(prompt_text, lemma, definition, concept_mapping)
            answer_model = get_answer(prompt, model_name)
            answer_verfied = validate_answer(answer_model)

            if answer_verfied is None:
                print(f"Invalid response for {lemma}: {answer_model}")
                answer_verfied = "[ungültig]"

            results.append((xml_id, lemma, pos, definition, concept_gold, answer_verfied, answer_model))
            print(f"{xml_id} | {lemma} ({definition}) → {answer_verfied}")

        write_results(output_path, results)
        generated_files.append(output_path)
        print(f"Results saved in: {output_path}")

    return generated_files

