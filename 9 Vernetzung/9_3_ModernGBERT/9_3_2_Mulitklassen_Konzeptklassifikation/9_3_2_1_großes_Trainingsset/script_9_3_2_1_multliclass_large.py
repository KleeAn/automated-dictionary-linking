# ================================================================
# Cross-validated training and evaluation of a SentenceTransformer model
# that maps lemma–definition pairs to predefined concepts from a JSON vocabulary.
# (multiclass classification).
# ================================================================

import os
import json
import math
import logging
import random
import time
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader
from sentence_transformers import models, SentenceTransformer, InputExample, losses

# ================================================================
# Function: extract_concepts_and_terms
# Purpose: Recursively extracts all concepts and terms from JSON structure
# ================================================================
def extract_concepts_and_terms(json_nodes: Dict[str, Any], current_path: Optional[List[str]] = None, mapping: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
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

    for k in list(mapping.keys()):
        if isinstance(mapping[k], dict):
            mapping[k] = list(mapping[k].keys())

    return mapping

# ================================================================
# Function: find_concept_key
# Purpose: Matches a label to a key in the mapping, raises error if not found
# ================================================================
def find_concept_key(label: str, mapping: Dict[str, List[str]]) -> str:
    label_stripped = label.strip()
    if label_stripped in mapping:
        return label_stripped
    else:
        raise ValueError(
            f"Concept '{label}' was not found in mapping. "
            f"Example keys: {list(mapping.keys())[:10]} ..."
        )

# ================================================================
# Function: set_seed
# Purpose: Sets random seed for reproducibility
# ================================================================
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

# ================================================================
# Function: assign_hybrid_folds
# Purpose: Assigns samples to folds using hybrid stratified/random strategy
# ================================================================
def assign_hybrid_folds(samples, folds=10, seed=42):
    np.random.seed(seed)
    concepts = [s["concept_key"] for s in samples]
    counter = pd.Series(concepts).value_counts()

    small_classes = counter[counter < folds].index.tolist()
    large_classes = counter[counter >= folds].index.tolist()

    fold_ids = np.full(len(samples), -1, dtype=int)

    # Large classes: StratifiedKFold
    large_idx = [i for i, s in enumerate(samples) if s["concept_key"] in large_classes]
    large_labels = [samples[i]["concept_key"] for i in large_idx]
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    for fold, (_, test_idx) in enumerate(skf.split(np.zeros(len(large_labels)), large_labels)):
        idxs = [large_idx[i] for i in test_idx]
        fold_ids[idxs] = fold

    # Small classes: distribute randomly
    for cls in small_classes:
        cls_idx = [i for i, s in enumerate(samples) if s["concept_key"] == cls]
        np.random.shuffle(cls_idx)
        for i, idx in enumerate(cls_idx):
            fold_ids[idx] = i % folds

    assert (fold_ids >= 0).all(), "Not all samples received a fold!"
    return fold_ids

# ================================================================
# Function: run_cv
# Purpose: Performs cross-validated training, evaluation, and saving of results
# ================================================================
def run_cv(
    tsv_path: str,
    vocab_json_path: str,
    model_id: str = "LSX-UniWue/ModernGBERT_1B",
    folds: int = 10,
    epochs: int = 4,
    batch_size: int = 32,
    max_seq_length: int = 256,
    output_dir: Optional[str] = None,
    seed: int = 42,
    save_fold_models: bool = False
):
    set_seed(seed)
    logging.basicConfig(level=logging.INFO)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Device: {device}")

    # ------------------------------------------------------------
    # Step 1: Load TSV
    # ------------------------------------------------------------
    df = pd.read_csv(tsv_path, sep="\t", encoding="utf-8").fillna("")
    if "Definition" not in df.columns or "Konzept" not in df.columns:
        raise ValueError("TSV must contain columns 'Definition' and 'Konzept'.")
    if "Lemma_bereinigt" not in df.columns:
        raise ValueError("TSV must also contain the column 'Lemma_bereinigt'.")

    # ------------------------------------------------------------
    # Step 2: Load JSON vocab and extract mapping
    # ------------------------------------------------------------
    with open(vocab_json_path, "r", encoding="utf-8") as f:
        vocab_json = json.load(f)
    mapping = extract_concepts_and_terms(vocab_json)
    logging.info(f"Extracted {len(mapping)} concepts from vocab JSON.")

    # ------------------------------------------------------------
    # Step 3: Build samples from TSV
    # ------------------------------------------------------------
    samples = []
    for _, row in df.iterrows():
        definition = str(row["Definition"]).strip()
        lemma = str(row["Lemma_bereinigt"]).strip()
        concept_label = str(row["Konzept"]).strip()
        if not definition or not concept_label:
            continue
        concept_key = find_concept_key(concept_label, mapping)
        terms = mapping.get(concept_key, [])
        if not terms:
            continue
        row_dict = row.to_dict()
        samples.append({
            "definition": definition,
            "lemma": lemma,
            "concept_key": concept_key,
            "terms": terms,
            "row": row_dict
        })
    logging.info(f"Usable samples: {len(samples)}")

    # ------------------------------------------------------------
    # Step 4: Assign folds
    # ------------------------------------------------------------
    fold_ids = assign_hybrid_folds(samples, folds=folds, seed=seed)

    # ------------------------------------------------------------
    # Step 5: Cross-Validation Loop
    # ------------------------------------------------------------
    fold_metrics = []
    for fold_idx in range(folds):
        start_time = time.time()
        train_idx = [i for i, f in enumerate(fold_ids) if f != fold_idx]
        test_idx = [i for i, f in enumerate(fold_ids) if f == fold_idx]

        logging.info(f"\n--- Fold {fold_idx+1}/{folds} ---")

        train_samples = [samples[i] for i in train_idx]
        test_samples = [samples[i] for i in test_idx]

        # --------------------------------------------------------
        # Step 5a: Prepare InputExamples
        # --------------------------------------------------------
        train_examples = [
            InputExample(
                texts=[f"{s['lemma']} — {s['definition']}", " ; ".join(s["terms"])]
            )
            for s in train_samples
        ]

        # --------------------------------------------------------
        # Step 5b: Model setup
        # --------------------------------------------------------
        word_embedding_model = models.Transformer(model_id, max_seq_length=max_seq_length)
        pooling_model = models.Pooling(
            word_embedding_model.get_word_embedding_dimension(),
            pooling_mode_mean_tokens=True,
            pooling_mode_cls_token=False,
            pooling_mode_max_tokens=False
        )
        model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
        model.to(device)

        train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
        train_loss = losses.MultipleNegativesRankingLoss(model)
        warmup_steps = math.ceil(len(train_dataloader) * epochs * 0.1)

        out_path = None
        if save_fold_models and output_dir:
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, f"fold_{fold_idx+1}")

        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=warmup_steps,
            optimizer_params={'lr': 2e-5},
            show_progress_bar=True,
            output_path=out_path
        )

        # --------------------------------------------------------
        # Step 5c: Compute concept vectors
        # --------------------------------------------------------
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
        key_to_idx = {k: i for i, k in enumerate(valid_keys)}

        # --------------------------------------------------------
        # Step 5d: Evaluation and top-k metrics
        # --------------------------------------------------------
        eval_texts = [f"{s['lemma']} — {s['definition']}" for s in test_samples]
        true_keys = [s["concept_key"] for s in test_samples]
        def_embs = model.encode(eval_texts, convert_to_numpy=True, normalize_embeddings=True)
        sims = np.matmul(def_embs, concept_matrix.T)

        top1 = top3 = top5 = 0
        mrr_sum = 0.0
        valid_count = 0
        fold_predictions = []

        for i, s in enumerate(test_samples):
            true_k = s["concept_key"]
            if true_k not in key_to_idx:
                continue
            idx_true = key_to_idx[true_k]
            ranked = np.argsort(-sims[i])
            rank_pos = int(np.where(ranked == idx_true)[0][0]) + 1
            valid_count += 1

            if rank_pos == 1:
                top1 += 1
            if rank_pos <= 3:
                top3 += 1
            if rank_pos <= 5:
                top5 += 1
            mrr_sum += 1.0 / rank_pos

            top_k = 5
            ranked_idxs = ranked[:top_k]
            top_k_concepts = [valid_keys[idx] for idx in ranked_idxs]

            row_dict = s["row"].copy()
            row_dict["Top_1"] = top_k_concepts[0]
            row_dict["Top_3"] = " ; ".join(top_k_concepts[:3])
            row_dict["Top_5"] = " ; ".join(top_k_concepts)
            fold_predictions.append(row_dict)

        metrics = {
            "top1": top1 / valid_count if valid_count else None,
            "top3": top3 / valid_count if valid_count else None,
            "top5": top5 / valid_count if valid_count else None,
            "mrr": mrr_sum / valid_count if valid_count else None,
            "n_valid": valid_count
        }
        logging.info(f"Fold {fold_idx+1} metrics: {metrics}")

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            fold_df = pd.DataFrame(fold_predictions)
            fold_df.to_csv(
                os.path.join(output_dir, f"fold_{fold_idx+1}_predictions.tsv"),
                sep="\t",
                index=False,
                encoding="utf-8"
            )

        end_time = time.time()
        fold_duration = end_time - start_time
        logging.info(f"Fold {fold_idx+1} completed in {fold_duration:.2f} seconds")

        fold_metrics.append(metrics)

        del model
        torch.cuda.empty_cache()

    # ------------------------------------------------------------
    # Step 6: Summary over all folds
    # ------------------------------------------------------------
    valid_folds = [m for m in fold_metrics if m["n_valid"] > 0]
    top1s = np.array([m["top1"] for m in valid_folds])
    top3s = np.array([m["top3"] for m in valid_folds])
    top5s = np.array([m["top5"] for m in valid_folds])
    mrrs = np.array([m["mrr"] for m in valid_folds])

    summary = {
        "folds": folds,
        "valid_folds": len(valid_folds),
        "top1_mean": float(np.mean(top1s)),
        "top1_std": float(np.std(top1s)),
        "top3_mean": float(np.mean(top3s)),
        "top3_std": float(np.std(top3s)),
        "top5_mean": float(np.mean(top5s)),
        "top5_std": float(np.std(top5s)),
        "mrr_mean": float(np.mean(mrrs)),
        "mrr_std": float(np.std(mrrs)),
    }

    logging.info("\n=== Cross-Validation Summary ===")
    for k, v in summary.items():
        logging.info(f"{k}: {v}")

    if output_dir:
        with open(os.path.join(output_dir, "cv_summary.json"), "w", encoding="utf-8") as f:
            json.dump({"fold_metrics": fold_metrics, "summary": summary}, f, ensure_ascii=False, indent=2)

    return fold_metrics, summary

# ================================================================
# Main execution
# ================================================================
fold_metrics, summary = run_cv(
    tsv_path="input/A_Trinken_expanded.tsv",
    vocab_json_path="input/trinken_vokabular.json",  #"input/trinken_vokabular_nur_OT.json"
    model_id="LSX-UniWue/ModernGBERT_1B", #"answerdotai/ModernBERT-large"
    folds=10,
    epochs=4,
    batch_size=32,
    max_seq_length=256,
    output_dir="cv_outputs",
    seed=42,
    save_fold_models=True
)
