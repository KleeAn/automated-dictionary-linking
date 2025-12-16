# ================================================================
# Script for training a SentenceTransformer model on Lemma-Definition pairs
# and evaluating cross-validated classification against the concept "Trinken".
# ================================================================

import os
import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, models, losses, InputExample, util
from torch.utils.data import DataLoader
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import time

# ================================================================
# Paths
# ================================================================
input_file = os.path.join("input", "A_B_C_gesamt_binär.tsv")
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# ================================================================
# Load Data and Prepare Lemma-Definition Texts
# ================================================================
df = pd.read_csv(input_file, sep="\t")

df["Lemma_Def"] = df["Lemma_bereinigt"].astype(str).str.strip() + " — " + df["Definition"].astype(str).str.strip()

texts = df["Lemma_Def"].tolist()
labels = df["Label"].tolist()

# ================================================================
# Cross-Validation Setup
# ================================================================
num_splits = 10  # 10% test data
skf = StratifiedKFold(n_splits=num_splits, shuffle=True, random_state=42)

# ================================================================
# Hyperparameters
# ================================================================
batch_size = 32
num_epochs = 5
threshold = 0.5  # Cosine similarity threshold for classification

# ================================================================
# Cross-Validation Loop
# ================================================================
for fold, (train_idx, test_idx) in enumerate(skf.split(texts, labels), 1):
    print(f"\n=== Fold {fold}/{num_splits} ===")
    fold_start_time = time.time()
    
    # ------------------------------------------------------------
    # Step 1: Train / Test Split
    # ------------------------------------------------------------
    train_texts = [texts[i] for i in train_idx]
    train_labels = [labels[i] for i in train_idx]
    test_texts = [texts[i] for i in test_idx]
    test_labels = [labels[i] for i in test_idx]
    
    # ------------------------------------------------------------
    # Step 2: Prepare InputExamples for Training
    # ------------------------------------------------------------
    train_input_examples = [
        InputExample(texts=[text, "Trinken"], label=float(label))
        for text, label in zip(train_texts, train_labels)
    ]
    train_loader = DataLoader(train_input_examples, shuffle=True, batch_size=batch_size)
    
    # ------------------------------------------------------------
    # Step 3: Initialize Model
    # ------------------------------------------------------------
    model_id = "LSX-UniWue/ModernGBERT_1B"
    word_embedding = models.Transformer(model_id)
    pooling_layer = models.Pooling(
        word_embedding.get_word_embedding_dimension(),
        pooling_mode_mean_tokens=True,
        pooling_mode_cls_token=False,
        pooling_mode_max_tokens=False
    )
    model = SentenceTransformer(modules=[word_embedding, pooling_layer])
    
    # Define Loss
    loss_function = losses.CosineSimilarityLoss(model=model)
    
    # ------------------------------------------------------------
    # Step 4: Fine-tuning
    # ------------------------------------------------------------
    warmup_steps = int(len(train_loader) * num_epochs * 0.1)
    model.fit(
        train_objectives=[(train_loader, loss_function)],
        epochs=num_epochs,
        warmup_steps=warmup_steps,
        output_path=os.path.join(output_dir, f"finetuned_fold_{fold}")
    )
    
    # ------------------------------------------------------------
    # Step 5: Concept Embedding for "Trinken"
    # ------------------------------------------------------------
    concept_emb = model.encode(["Trinken"], convert_to_tensor=True)
    
    # ------------------------------------------------------------
    # Step 6: Evaluate Test Data
    # ------------------------------------------------------------
    fold_results = []
    all_true_labels, all_pred_labels = [], []

    # Extract fold rows from DataFrame
    df_fold = df.iloc[test_idx].copy()  

    for i, (text, label) in enumerate(zip(test_texts, test_labels)):
        text_emb = model.encode(text, convert_to_tensor=True)
        cosine_score = util.cos_sim(text_emb, concept_emb)[0][0].item()
        predicted_label = 1 if cosine_score > threshold else 0

        all_true_labels.append(label)
        all_pred_labels.append(predicted_label)

        # Add new columns
        df_fold.loc[df_fold.index[i], "Cosine_Score"] = cosine_score
        df_fold.loc[df_fold.index[i], "Pred_Label"] = predicted_label

    # Accuracy per Fold
    acc = accuracy_score(all_true_labels, all_pred_labels)
    print(f"Fold {fold} Accuracy: {acc:.4f}")

    # Save fold results
    results_file = os.path.join(output_dir, f"fold_{fold}_results.tsv")
    df_fold.to_csv(results_file, sep="\t", index=False, float_format="%.4f")
    print(f"Fold {fold} results saved.")
    fold_end_time = time.time()
    print(f"Fold {fold} runtime: {fold_end_time - fold_start_time:.2f} seconds")

# ================================================================
# Aggregate Results Across Folds
# ================================================================
total_true_labels = []
total_pred_labels = []

fold_metrics = []

for fold in range(1, num_splits + 1):
    results_df = pd.read_csv(os.path.join(output_dir, f"fold_{fold}_results.tsv"), sep="\t")
    true_fold = results_df["Label"].tolist()
    pred_fold = results_df["Pred_Label"].tolist()

    fold_acc = accuracy_score(true_fold, pred_fold)
    fold_prec = precision_score(true_fold, pred_fold)
    fold_rec = recall_score(true_fold, pred_fold)
    fold_f1 = f1_score(true_fold, pred_fold)

    fold_metrics.append([fold_acc, fold_prec, fold_rec, fold_f1])

    total_true_labels.extend(true_fold)
    total_pred_labels.extend(pred_fold)

# Convert to NumPy array for easy stats
fold_metrics = np.array(fold_metrics)  # Shape: (num_splits, 4)

# Mean and Std over folds
mean_metrics = fold_metrics.mean(axis=0)
std_metrics = fold_metrics.std(axis=0)

print("\n=== Overall Results Across All Folds ===")
print(f"Accuracy : {mean_metrics[0]:.4f} ± {std_metrics[0]:.4f}")
print(f"Precision: {mean_metrics[1]:.4f} ± {std_metrics[1]:.4f}")
print(f"Recall   : {mean_metrics[2]:.4f} ± {std_metrics[2]:.4f}")
print(f"F1-Score : {mean_metrics[3]:.4f} ± {std_metrics[3]:.4f}")

# ------------------------------------------------------------
# Save Aggregated Results
# ------------------------------------------------------------
aggregated_file = os.path.join(output_dir, "aggregated_results.tsv")
aggregated_df = pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall", "F1-Score"],
    "Mean": mean_metrics,
    "Std": std_metrics
})
aggregated_df.to_csv(aggregated_file, sep="\t", index=False, float_format="%.4f")
print(f"Aggregated results saved to: {aggregated_file}")
