# ================================================================
# Script to train and evaluate a SentenceTransformer model with cross-validation,
# mapping of Lemma-Definition pairs on vocabulary terms.
# ================================================================

import os
import json
import math
import logging
import random
import time
from typing import Dict, List, Optional, Any, Set

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader
from sentence_transformers import models, SentenceTransformer, InputExample, losses

# ================================================================
# Function: extract_concepts_and_terms
# Purpose: Returns a flat list of all unique terms from a JSON vocab
# ================================================================
def extract_concepts_and_terms(json_nodes: Any) -> List[str]:
    collected: List[str] = []
    seen: Set[str] = set()

    def add_term(value: Any):
        if value is None:
            return
        s = str(value).strip()
        if not s:
            return
        if s not in seen:
            seen.add(s)
            collected.append(s)

    def gather(node: Any):
        """Recursively collects individual term values (lists/dicts)."""
        if isinstance(node, list):
            for el in node:
                gather(el)
        elif isinstance(node, dict):
            for v in node.values():
                gather(v)
        else:
            add_term(node)

    def recurse(node: Any):
        """Traverses the JSON structure and identifies 'Begriffe' keys."""
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(k, str) and k.strip().lower() == "begriffe":
                    gather(v)
                else:
                    recurse(v)
        elif isinstance(node, list):
            for el in node:
                recurse(el)

    recurse(json_nodes)
    return collected

# ================================================================
# Function: set_seed
# Purpose: Sets random seeds for reproducibility
# ================================================================
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

# ================================================================
# Function: assign_hybrid_folds
# Purpose: Assigns samples to stratified folds, handling small and large classes
# ================================================================
def assign_hybrid_folds(samples, folds=10, seed=42):
    np.random.seed(seed)
    terms = [s["term"] for s in samples]
    counter = pd.Series(terms).value_counts()

    small_classes = counter[counter < folds].index.tolist()
    large_classes = counter[counter >= folds].index.tolist()

    fold_ids = np.full(len(samples), -1, dtype=int)

    # ------------------------------------------------------------
    # Large classes: StratifiedKFold
    # ------------------------------------------------------------
    large_idx = [i for i, s in enumerate(samples) if s["term"] in large_classes]
    large_labels = [samples[i]["term"] for i in large_idx]
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    for fold, (_, test_idx) in enumerate(skf.split(np.zeros(len(large_labels)), large_labels)):
        idxs = [large_idx[i] for i in test_idx]
        fold_ids[idxs] = fold

    # ------------------------------------------------------------
    # Small classes: distribute randomly
    # ------------------------------------------------------------
    for cls in small_classes:
        cls_idx = [i for i, s in enumerate(samples) if s["term"] == cls]
        np.random.shuffle(cls_idx)
        for i, idx in enumerate(cls_idx):
            fold_ids[idx] = i % folds

    assert (fold_ids >= 0).all(), "Not all samples received a fold!"
    return fold_ids

# ================================================================
# Function: run_cv
# Purpose: Executes cross-validated training, embedding, and evaluation
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
    # ------------------------------------------------------------
    # Step 1: Set seed and logging
    # ------------------------------------------------------------
    set_seed(seed)
    logging.basicConfig(level=logging.INFO)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Device: {device}")

    # ------------------------------------------------------------
    # Step 2: Load TSV and JSON vocab
    # ------------------------------------------------------------
    df = pd.read_csv(tsv_path, sep="\t", encoding="utf-8").fillna("")
    if "Definition" not in df.columns or "Begriff" not in df.columns:
        raise ValueError("TSV must contain columns 'Definition' and 'Begriff'.")
    if "Lemma_bereinigt" not in df.columns:
        raise ValueError("TSV must contain the column 'Lemma_bereinigt'.")

    with open(vocab_json_path, "r", encoding="utf-8") as f:
        vocab_json = json.load(f)
    mapping = extract_concepts_and_terms(vocab_json)
    logging.info(f"Extracted {len(mapping)} terms from vocab JSON.")

    # ------------------------------------------------------------
    # Step 3: Build usable samples
    # ------------------------------------------------------------
    samples = []
    for _, row in df.iterrows():
        definition = str(row["Definition"]).strip()
        lemma = str(row["Lemma_bereinigt"]).strip()
        term = str(row["Begriff"]).strip()
        if not definition or not term:
            continue

        row_dict = row.to_dict()

        samples.append({
            "lemma": lemma,
            "definition": definition,
            "term": term,
            "row": row_dict
        })

    logging.info(f"Usable samples: {len(samples)}")

    # ------------------------------------------------------------
    # Step 4: Hybrid fold assignment
    # ------------------------------------------------------------
    fold_ids = assign_hybrid_folds(samples, folds=folds, seed=seed)

    fold_metrics = []

    # ------------------------------------------------------------
    # Step 5: Cross-validation loop
    # ------------------------------------------------------------
    for fold_idx in range(folds):
        start_time = time.time()
        
        train_idx = [i for i, f in enumerate(fold_ids) if f != fold_idx]
        test_idx = [i for i, f in enumerate(fold_ids) if f == fold_idx]

        logging.info(f"\n--- Fold {fold_idx+1}/{folds} ---")

        train_samples = [samples[i] for i in train_idx]
        test_samples = [samples[i] for i in test_idx]

        train_examples = [
            InputExample(texts=[f"{s['lemma']} — {s['definition']}", s["term"]]) for s in train_samples
        ]

        # ------------------------------------------------------------
        # Step 5a: Model initialization
        # ------------------------------------------------------------
        word_embedding_model = models.Transformer(
            model_id,
            max_seq_length=max_seq_length
        )
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

        # ------------------------------------------------------------
        # Step 5b: Encode term vectors
        # ------------------------------------------------------------
        test_terms = [s["term"] for s in test_samples]
        missing_terms = [t for t in test_terms if t not in mapping]

        terms = mapping + missing_terms
        embs = model.encode(terms, convert_to_numpy=True, normalize_embeddings=True)

        term_matrix = np.vstack(embs)
        term_to_idx = {t: i for i, t in enumerate(terms)}

        # ------------------------------------------------------------
        # Step 5c: Encode definitions and compute similarities
        # ------------------------------------------------------------
        texts = [f"{s['lemma']} — {s['definition']}" if s["lemma"] else s["definition"] for s in test_samples]
        true_terms = [s["term"] for s in test_samples]
        def_embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        sims = np.matmul(def_embs, term_matrix.T)

        top1 = top3 = top5 = 0
        mrr_sum = 0.0
        valid_count = 0
        fold_predictions = []

        for i, s in enumerate(test_samples):
            true_t = s["term"]
            idx_true = term_to_idx[true_t]
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
            top_k_terms = [terms[idx] for idx in ranked_idxs]

            row_dict = s["row"].copy()
            row_dict["Top_1"] = top_k_terms[0]
            row_dict["Top_3"] = " ; ".join(top_k_terms[:3])
            row_dict["Top_5"] = " ; ".join(top_k_terms)
            fold_predictions.append(row_dict)

        metrics = {
            "top1": top1 / valid_count if valid_count else None,
            "top3": top3 / valid_count if valid_count else None,
            "top5": top5 / valid_count if valid_count else None,
            "mrr": mrr_sum / valid_count if valid_count else None,
            "n_valid": valid_count
        }
        logging.info(f"Fold {fold_idx+1} metrics: {metrics}")

        # ------------------------------------------------------------
        # Step 5d: Save fold predictions
        # ------------------------------------------------------------
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

    # ================================================================
    # Step 6: Aggregate cross-validation results
    # ================================================================
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

    # ------------------------------------------------------------
    # Step 7: Save summary JSON
    # ------------------------------------------------------------
    if output_dir:
        with open(os.path.join(output_dir, "cv_summary.json"), "w", encoding="utf-8") as f:
            json.dump({"fold_metrics": fold_metrics, "summary": summary}, f, ensure_ascii=False, indent=2)

    return fold_metrics, summary

# ================================================================
# Main Execution
# ================================================================
fold_metrics, summary = run_cv(
    tsv_path="input/A_Getränke_expanded.tsv",
    vocab_json_path="input/getränke_vokabular_nur_OT.json",
    model_id="LSX-UniWue/ModernGBERT_1B",
    folds=10,
    epochs=4,
    batch_size=32,
    max_seq_length=256,
    output_dir="cv_outputs",
    seed=42,
    save_fold_models=True
)