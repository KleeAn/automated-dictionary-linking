# ================================================================
# Script for multi-label evaluation of term mapping results
# (mapping of concept group Getränk).
# ================================================================

import os
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
from sklearn.preprocessing import MultiLabelBinarizer
import warnings
from sklearn.exceptions import UndefinedMetricWarning

# --- Suppress specific sklearn warnings ---
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.preprocessing._label")
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

# ================================================================
# Constants / File paths
# ================================================================
method_dir = "modernbert" #"modernbert"  #"llama_3.3_70b" #"stringabgleich"
input_dir = os.path.join(method_dir, "input")
output_dir = os.path.join(method_dir, "output")
input_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".tsv")]

# ================================================================
# Option: Select prediction column
# ================================================================
# Choose which column to evaluate: "Begriff_gemappt", "Top_1", "Top_3", or "Top_5"
prediction_column = "Top_5"

# ================================================================
# Function: parse_labels
# ================================================================
def parse_labels(cell):
    if pd.isna(cell) or cell.strip() == "":
        return []
    return [label.strip() for label in cell.split(";")]

# ================================================================
# Function: evaluate_file
# ================================================================
def evaluate_file(input_filepath):
    df = pd.read_csv(input_filepath, sep="\t")

    if prediction_column not in df.columns:
        raise ValueError(f"Column '{prediction_column}' not found in {input_filepath}.")

    y_true = df["Begriff"].apply(parse_labels).tolist()
    y_pred = df[prediction_column].apply(parse_labels).tolist()

    mlb = MultiLabelBinarizer()
    mlb.fit(y_true + y_pred)
    y_true_bin = mlb.transform(y_true)
    y_pred_bin = mlb.transform(y_pred)
    labels = mlb.classes_

    output_lines = []
    output_lines.append(f"=== Evaluation using column: {prediction_column} ===\n")

    # --- Overall metrics ---
    output_lines.append("=== Overall metrics ===")
    output_lines.append(f"Weighted-Precision:    {precision_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0):.4f}")
    output_lines.append(f"Weighted-Recall:       {recall_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0):.4f}")
    output_lines.append(f"Weighted-F1:           {f1_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0):.4f}")
    output_lines.append(f"Micro-Precision:       {precision_score(y_true_bin, y_pred_bin, average='micro', zero_division=0):.4f}")
    output_lines.append(f"Micro-Recall:          {recall_score(y_true_bin, y_pred_bin, average='micro', zero_division=0):.4f}")
    output_lines.append(f"Macro-Precision:       {precision_score(y_true_bin, y_pred_bin, average='macro', zero_division=0):.4f}")
    output_lines.append(f"Macro-Recall:          {recall_score(y_true_bin, y_pred_bin, average='macro', zero_division=0):.4f}")

    # --- At least one correct ---
    at_least_one_correct = np.sum(np.logical_and(y_true_bin, y_pred_bin).sum(axis=1) > 0)
    total_samples = len(y_true_bin)
    at_least_one_correct_ratio = at_least_one_correct / total_samples
    output_lines.append(f"Accuracy (at least one match):    {at_least_one_correct} of {total_samples} entries ({at_least_one_correct_ratio:.2%})")

    # --- Per-concept report ---
    output_lines.append("\n=== Precision/Recall/F1 per concept ===")
    output_lines.append(classification_report(y_true_bin, y_pred_bin, target_names=labels, zero_division=0))

    # --- Save results ---
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.basename(input_filepath)
    basename_noext = os.path.splitext(basename)[0]

    if "match" in basename_noext:
        basename_clean = basename_noext.split("match")[0].rstrip("_- ")
    else:
        basename_clean = basename_noext.rstrip("_- ")

    # append prediction_column if method is modernbert
    if method_dir == "modernbert":
        output_filename = f"{basename_clean}_evaluation_begriffe_{prediction_column}.txt"
    else:
        output_filename = f"{basename_clean}_evaluation_begriffe.txt"

    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"\nResults for {basename} using column '{prediction_column}':\n")
    print("\n".join(output_lines))
    print(f"\nResults were saved in: {output_path}\n{'='*50}\n")

# ================================================================
# Main program
# ================================================================
def main():
    if not input_files:
        print("No TSV files found in input directory.")
        return

    for input_file in input_files:
        input_filepath = os.path.join(input_dir, input_file)
        evaluate_file(input_filepath)

if __name__ == "__main__":
    main()
