# ================================================================
# Script for multi-label evaluation of concept mapping results
# (mapping to Wurzelkonzepte).
#
# Purpose:
#   Reads true and predicted concept labels,
#   calculates precision, recall, F1, accuracy metrics overall
#   and per concept group.
# ================================================================

import os
import re
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.preprocessing import MultiLabelBinarizer
import warnings
from sklearn.exceptions import UndefinedMetricWarning

# --- Suppress specific sklearn warnings ---
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.preprocessing._label")
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

# ================================================================
# Constants / File paths
# ================================================================
method_dir = "llama_3.3_70b" #"modernbert" #"llama_3.3_70b" #"stringabgleich"  
input_dir = os.path.join(method_dir, "input")
output_dir = os.path.join(method_dir,"output")
input_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".tsv")]

# concept_groups für Gruppen-Accuracy
concept_groups = {
    "Trinken": {"Trinken"},
    "Getränk": {"Getränk"},
    "Durst": {"Durst"}
}

# ------------------------------------------------------------
# Option: Select prediction column
# ------------------------------------------------------------
# Choose which prediction column should be evaluated:
#   "Konzept_gemappt", "Top_1", "Top_3", or "Top_5"
prediction_column = "Konzept_gemappt"

# ================================================================
# Function: parse_labels
# Purpose: Convert a semicolon-separated label string into a list.
# Returns: list of labels or empty list if NaN or empty.
# ================================================================
def parse_labels(cell):
    if pd.isna(cell) or cell.strip() == "":
        return []
    return [label.strip() for label in cell.split(";")]

# ================================================================
# Function: reduce_to_root
# Purpose: Reduce concept labels to their root concepts.
# Returns: list of unique root concepts, preserving order.
# ================================================================
def reduce_to_root(labels):
    roots = []
    for label in labels:
        if label in {"Trinken", "Durst", "Getränk", "kein_Trinken"}:
            roots.append(label)
        else:
            root = label.split(".", 1)[0]
            roots.append(root)
    # Remove duplicates, preserve order
    seen = set()
    unique_roots = []
    for r in roots:
        if r not in seen:
            seen.add(r)
            unique_roots.append(r)
    return unique_roots

# ================================================================
# Main program
# ================================================================
def main():
    os.makedirs(output_dir, exist_ok=True)

    for filename in input_files:
        input_filepath = os.path.join(input_dir, filename)
        print(f"____________________________________________\n\n")
        print(f"Processing file: {input_filepath}")

        # --- Load input file ---
        df = pd.read_csv(input_filepath, sep="\t")

        # --- Parse and reduce concepts to roots ---
        y_true_raw = df["Konzept"].apply(parse_labels)
        y_pred_raw = df[prediction_column].apply(parse_labels)
        y_true = y_true_raw.apply(reduce_to_root).tolist()
        y_pred = y_pred_raw.apply(reduce_to_root).tolist()

        # --- Binarize multi-label data ---
        mlb = MultiLabelBinarizer()
        y_true_bin = mlb.fit_transform(y_true)
        y_pred_bin = mlb.transform(y_pred)
        labels = mlb.classes_

        output_lines = []

        # --- Overall metrics ---
        output_lines.append("=== Overall metrics ===")
        output_lines.append(f"Weighted-Precision: {precision_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0):.4f}")
        output_lines.append(f"Weighted-Recall:    {recall_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0):.4f}")
        output_lines.append(f"Weighted-F1:        {f1_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0):.4f}")
        output_lines.append(f"Micro-Precision:    {precision_score(y_true_bin, y_pred_bin, average='micro', zero_division=0):.4f}")
        output_lines.append(f"Micro-Recall:       {recall_score(y_true_bin, y_pred_bin, average='micro', zero_division=0):.4f}")
        output_lines.append(f"Macro-Precision:    {precision_score(y_true_bin, y_pred_bin, average='macro', zero_division=0):.4f}")
        output_lines.append(f"Macro-Recall:       {recall_score(y_true_bin, y_pred_bin, average='macro', zero_division=0):.4f}")

        # --- Subset accuracy ---
        output_lines.append(f"Accuracy (exact match of all predictions):    {accuracy_score(y_true_bin, y_pred_bin):.4f}")

        # --- Accuracy: at least one correct prediction ---
        correct_at_least_one = np.sum(np.logical_and(y_true_bin, y_pred_bin).sum(axis=1) > 0)
        total_samples = y_true_bin.shape[0]
        ratio_at_least_one = correct_at_least_one / total_samples
        output_lines.append(f"Accuracy (at least one match): {ratio_at_least_one:.4f}")

        # --- Precision/Recall/F1 per concept ---
        output_lines.append("\n=== Precision/Recall/F1 per concept ===")
        header = f"{'Label':<20} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}"
        output_lines.append(header)
        output_lines.append("-" * len(header))

        for i, label in enumerate(labels):
            y_true_label = y_true_bin[:, i]
            y_pred_label = y_pred_bin[:, i]

            p = precision_score(y_true_label, y_pred_label, zero_division=0)
            r = recall_score(y_true_label, y_pred_label, zero_division=0)
            f1 = f1_score(y_true_label, y_pred_label, zero_division=0)
            support = int(np.sum(y_true_label))

            output_lines.append(f"{label:<20} {p:10.4f} {r:10.4f} {f1:10.4f} {support:10}")

        # --- Accuracy per concept group (at least one match) ---
        output_lines.append("\n=== Accuracy per concept group (at least one match) ===")
        for group_name, concept_set in concept_groups.items():
            correct_count = 0
            total_count = 0
            for true_labels, pred_labels in zip(y_true, y_pred):
                if concept_set & set(true_labels):  # concept group is part of ground truth
                    total_count += 1
                    if concept_set & set(true_labels) & set(pred_labels):  # at least one intersection
                        correct_count += 1
            if total_count > 0:
                acc = correct_count / total_count
                output_lines.append(f"{group_name}: {acc:.4f} ({correct_count}/{total_count})")
            else:
                output_lines.append(f"{group_name}: No occurrences in the ground truth")

        # --- Save results to file ---
        os.makedirs(output_dir, exist_ok=True)

        # ------------------------------------------------------------
        # Determine basename depending on the selected method_dir
        # ------------------------------------------------------------

        filename_no_ext = os.path.splitext(filename)[0]   # remove file extension

        if method_dir == "stringabgleich":
           
            patterns = [
                "A_Trinken_OT_", "B_Verwandt_OT_", "C_Zufall_OT_", "A_B_C_gesamt_OT_",
                "A_Trinken_", "B_Verwandt_", "C_Zufall_", "A_B_C_gesamt_"
            ]
            pattern_regex = re.compile(r".*?(" + "|".join(map(re.escape, patterns)) + ")")
            match = pattern_regex.search(filename)
            if match:
                basename = match.group(0)
            else:
                basename = filename_no_ext + "_"

        elif any(method_dir.startswith(prefix) for prefix in ["deepseek", "qwen", "llama"]):
            if "_basiskonzepte" in filename_no_ext:
                basename = filename_no_ext.split("_basiskonzepte")[0] + "_"
            else:
                basename = filename_no_ext + "_"

        elif method_dir == "modernbert":
            if "_final" in filename_no_ext:
                basename = filename_no_ext.split("_final")[0] + "_"
            else:
                basename = filename_no_ext + "_"

        else:
            # Fallback
            basename = filename_no_ext + "_"
            
        # --- Save results ---
        if method_dir == "modernbert":
            output_path = os.path.join(output_dir, f"{basename}precision_recall_wurzel_{prediction_column}.txt")
        else:
            output_path = os.path.join(output_dir, f"{basename}precision_recall_wurzel.txt")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        # --- Print results to console ---
        print("\n".join(output_lines))
        print(f"\nResults were saved in: {output_path}")

if __name__ == "__main__":
    main()


