# ================================================================
# Embeds definitions from TSV files using a pre-trained SentenceTransformer
# and predicts top concept matches based on a vocabulary.
# ================================================================

import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import os


# ================================================================
# Recursive extraction of concepts and terms from nested JSON
# ================================================================
def extract_concepts_and_terms(json_nodes, current_path=None, mapping=None):
    if mapping is None:
        mapping = {}
    if current_path is None:
        current_path = []

    for key, value in json_nodes.items():
        if key == "Begriffe":
            concept = ".".join(current_path)
            if concept not in mapping or not isinstance(mapping[concept], dict):
                mapping[concept] = {}
            terms = value if isinstance(value, list) else [value]
            for term in terms:
                single_terms = term if isinstance(term, list) else [term]
                for t in single_terms:
                    if t is None:
                        continue
                    mapping[concept][str(t).strip()] = None
        elif isinstance(value, dict):
            extract_concepts_and_terms(value, current_path + [key], mapping)

    # Convert nested dicts to lists of unique terms
    for k in list(mapping.keys()):
        if isinstance(mapping[k], dict):
            mapping[k] = list(mapping[k].keys())

    return mapping


# ================================================================
# Apply embedding model to input TSV and generate top-k predictions
# ================================================================
def apply_model(input_tsv, model_path, vocab_json, output_tsv):
    # ------------------------------------------------------------
    # Load sentence embedding model
    # ------------------------------------------------------------
    model = SentenceTransformer(model_path)

    # ------------------------------------------------------------
    # Load vocabulary JSON and extract concepts & terms
    # ------------------------------------------------------------
    with open(vocab_json, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    mapping = extract_concepts_and_terms(vocab)

    # ------------------------------------------------------------
    # Compute embeddings for each concept
    # ------------------------------------------------------------
    concept_vecs = []
    valid_keys = []
    for ck, terms in mapping.items():
        if not terms:
            continue
        emb = model.encode(terms, convert_to_numpy=True, normalize_embeddings=True)
        avg = np.mean(emb, axis=0)
        norm = np.linalg.norm(avg)
        if norm == 0:
            continue
        concept_vecs.append(avg / norm)
        valid_keys.append(ck)
    concept_matrix = np.vstack(concept_vecs)

    # ------------------------------------------------------------
    # Load input TSV
    # ------------------------------------------------------------
    df = pd.read_csv(input_tsv, sep="\t", encoding="utf-8").fillna("")
    if "Definition" not in df.columns:
        raise ValueError(f"TSV '{input_tsv}' must contain a 'Definition' column.")

    # ------------------------------------------------------------
    # Embed definitions from TSV
    # ------------------------------------------------------------
    defs = df["Definition"].astype(str).tolist()
    def_embs = model.encode(defs, convert_to_numpy=True, normalize_embeddings=True)

    # ------------------------------------------------------------
    # Compute similarity scores with concept embeddings
    # ------------------------------------------------------------
    sims = np.matmul(def_embs, concept_matrix.T)

    # ------------------------------------------------------------
    # Determine Top-1, Top-3, Top-5 predictions
    # ------------------------------------------------------------
    top1_list, top3_list, top5_list = [], [], []
    for i in range(len(defs)):
        ranked = np.argsort(-sims[i])
        top_k = [valid_keys[idx] for idx in ranked[:5]]
        top1_list.append(top_k[0])
        top3_list.append(" ; ".join(top_k[:3]))
        top5_list.append(" ; ".join(top_k))

    # ------------------------------------------------------------
    # Add predictions to DataFrame
    # ------------------------------------------------------------
    df["Top_1"] = top1_list
    df["Top_3"] = top3_list
    df["Top_5"] = top5_list

    # ------------------------------------------------------------
    # Save output TSV
    # ------------------------------------------------------------
    df.to_csv(output_tsv, sep="\t", index=False, encoding="utf-8")
    print(f"Results saved to: {output_tsv}")


# ================================================================
# Execution
# ================================================================
if __name__ == "__main__":
    input_files = ["input/B_Verwandt.tsv", "input/C_Zufall.tsv"]
    model_path = "cv_outputs/10f_32bs_4e/fold_1"  # Define the location of the folder including the pretrained model
    model_name = "10f_32bs_4e" # define model name
    vocab_path = "input/trinken_vokabular.json"

    # Apply model to each input TSV
    for input_file in input_files:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"output/{base_name}_{model_name}.tsv"
        apply_model(input_file, model_path, vocab_path, output_file)
