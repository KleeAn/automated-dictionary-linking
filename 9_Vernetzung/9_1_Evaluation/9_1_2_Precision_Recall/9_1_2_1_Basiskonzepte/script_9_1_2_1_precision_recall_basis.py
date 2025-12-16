# ================================================================
# Script for multi-label evaluation of concept mapping results
# (mapping to Basiskonzepte).
#
# Purpose:
#   Reads true and predicted concept labels,
#   calculates precision, recall, F1, accuracy metrics overall,
#   per concept group, and per part-of-speech ("Wortart").
#   Outputs evaluation report to text file and console.
# ================================================================

import os
import re
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    classification_report, accuracy_score
)
from sklearn.preprocessing import MultiLabelBinarizer
import warnings
from sklearn.exceptions import UndefinedMetricWarning

# Suppress specific sklearn warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.preprocessing._label")
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

# ------------------------------------------------------------
# Constants / File paths
# ------------------------------------------------------------
method_dir = "llama_3.3_70b" #"modernbert" #"llama_3.3_70b" #"stringabgleich"
input_dir = os.path.join(method_dir, "input")
output_dir = os.path.join(method_dir,"output")
input_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".tsv")]

groups = ["Durst", "Trinken", "Getränk"]

# ------------------------------------------------------------
# Option: Select prediction column
# ------------------------------------------------------------
# Choose which prediction column should be evaluated:
#   "Konzept_gemappt", "Top_1", "Top_3", or "Top_5"
prediction_column = "Konzept_gemappt"

# ------------------------------------------------------------
# Function: parse_labels
# Purpose: Convert a semicolon-separated label string into a list.
# Returns: list of labels or empty list if NaN or empty.
# ------------------------------------------------------------
def parse_labels(cell):
    if pd.isna(cell) or cell.strip() == "":
        return []
    return [label.strip() for label in cell.split(";")]

# ------------------------------------------------------------
# Function: special_concept_handling
# Purpose: Special case treatment for the concept
# "Trinken.Häufig_lange_trinken".
# ------------------------------------------------------------
def special_concept_handling(concepts):
    if "Trinken.Häufig_lange_trinken" in concepts:
        if len(concepts) == 1:
            return ["Trinken"]
        else:
            return [k for k in concepts if k != "Trinken.Häufig_lange_trinken"]
    return concepts

# ------------------------------------------------------------
# Function: get_group_indices
# Purpose: Find indices of labels belonging to a specific group.
# ------------------------------------------------------------
def get_group_indices(labels, group_name):
    return [i for i, label in enumerate(labels) if label == group_name or label.startswith(group_name + ".")]

# ------------------------------------------------------------
# Function: evaluate_group
# Purpose: Compute precision, recall, F1 for group labels with different averaging.
# Returns: dict with averages as keys and (p, r, f1) tuples as values.
# ------------------------------------------------------------
def evaluate_group(y_true_bin, y_pred_bin, indices):
    y_true_sub = y_true_bin[:, indices]
    y_pred_sub = y_pred_bin[:, indices]
    results = {}

    if len(indices) == 1:
        # Single class: Calculate metrics with 1D arrays (binary)
        i = indices[0]
        p = precision_score(y_true_bin[:, i], y_pred_bin[:, i], zero_division=0)
        r = recall_score(y_true_bin[:, i], y_pred_bin[:, i], zero_division=0)
        f1 = f1_score(y_true_bin[:, i], y_pred_bin[:, i], zero_division=0)
        results['single'] = (p, r, f1)
    else:
        # Multiple classes: calculate multi-label metrics with different averaging methods
        for avg in ['micro', 'macro', 'weighted']:
            p = precision_score(y_true_sub, y_pred_sub, average=avg, zero_division=0)
            r = recall_score(y_true_sub, y_pred_sub, average=avg, zero_division=0)
            f1 = f1_score(y_true_sub, y_pred_sub, average=avg, zero_division=0)
            results[avg] = (p, r, f1)

    return results


# ------------------------------------------------------------
# Function: group_accuracy
# Purpose: Calculate exact match accuracy for all group labels.
# ------------------------------------------------------------
def group_accuracy(y_true_bin, y_pred_bin, indices):
    y_true_sub = y_true_bin[:, indices]
    y_pred_sub = y_pred_bin[:, indices]
    mask = y_true_sub.sum(axis=1) > 0  # Only samples with at least one true label in group
    if np.sum(mask) == 0:
        return np.nan
    correct = np.all(y_true_sub[mask] == y_pred_sub[mask], axis=1)
    return np.mean(correct)

# ------------------------------------------------------------
# Function: group_accuracy_at_least_one
# Purpose: Calculate accuracy if at least one label matches in group.
# ------------------------------------------------------------
def group_accuracy_at_least_one(y_true_bin, y_pred_bin, indices):
    y_true_sub = y_true_bin[:, indices]
    y_pred_sub = y_pred_bin[:, indices]
    mask = y_true_sub.sum(axis=1) > 0
    if np.sum(mask) == 0:
        return np.nan
    correct_at_least_one = np.sum(np.logical_and(y_true_sub[mask], y_pred_sub[mask]), axis=1) > 0
    return np.mean(correct_at_least_one)

# ------------------------------------------------------------
# Function: overall_metrics
# Purpose: Calculate overall precision, recall, F1 for all labels.
# ------------------------------------------------------------
def overall_metrics(y_true_bin, y_pred_bin):
    metrics = {
        "Weighted-Precision": precision_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0),
        "Weighted-Recall": recall_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0),
        "Weighted-F1": f1_score(y_true_bin, y_pred_bin, average='weighted', zero_division=0),
        
        "Micro-Precision": precision_score(y_true_bin, y_pred_bin, average='micro', zero_division=0),
        "Micro-Recall": recall_score(y_true_bin, y_pred_bin, average='micro', zero_division=0),
        "Micro-F1": f1_score(y_true_bin, y_pred_bin, average='micro', zero_division=0),

        "Macro-Precision": precision_score(y_true_bin, y_pred_bin, average='macro', zero_division=0),
        "Macro-Recall": recall_score(y_true_bin, y_pred_bin, average='macro', zero_division=0),
        "Macro-F1": f1_score(y_true_bin, y_pred_bin, average='macro', zero_division=0)
    }
    return metrics

# ------------------------------------------------------------
# Function: print_overall_metrics
# Purpose: Format overall metrics for output.
# ------------------------------------------------------------
def print_overall_metrics(metrics, output_lines):
    output_lines.append("=== Overall metrics ===")
    output_lines.append(f"{'metrics':20} | value")
    output_lines.append("-" * 30)
    for name, value in metrics.items():
        output_lines.append(f"{name:20} | {value:.4f}")

# ------------------------------------------------------------
# Function: print_classification_report
# Purpose: Generate detailed classification report per label.
# ------------------------------------------------------------
def print_classification_report(y_true_bin, y_pred_bin, labels, output_lines, title=""):
    if title:
        output_lines.append(f"\n=== {title} ===")
    report = classification_report(y_true_bin, y_pred_bin, target_names=labels, zero_division=0)
    output_lines.append(report)

# ------------------------------------------------------------
# Function: print_subset_accuracies
# Purpose: Print exact match accuracy and accuracy with at least one correct label.
# ------------------------------------------------------------
def print_subset_accuracies(y_true_bin, y_pred_bin, output_lines):
    acc_exact = accuracy_score(y_true_bin, y_pred_bin)
    correct_at_least_one = np.sum(np.logical_and(y_true_bin, y_pred_bin).sum(axis=1) > 0)
    ratio_at_least_one = correct_at_least_one / y_true_bin.shape[0]

    output_lines.append(f"Accuracy (exact match of all predictions): {acc_exact:.4f}")
    output_lines.append(f"Accuracy (at least one match):      {ratio_at_least_one:.4f}")

# ------------------------------------------------------------
# Function: evaluate_groups
# Purpose: Evaluate precision, recall, F1, and accuracy per group.
# Formatted output analogous to overall metrics.
# ------------------------------------------------------------
def evaluate_groups(y_true_bin, y_pred_bin, labels, groups, output_lines):
    for group in groups:
        indices = get_group_indices(labels, group)
        if not indices:
            output_lines.append(f"\nNo labels found for group '{group}'!")
            continue

        res = evaluate_group(y_true_bin, y_pred_bin, indices)
        output_lines.append(f"\n=== Metrics for '{group}' ===")

        if 'single' in res:
            p, r, f1 = res['single']
            output_lines.append(f"{'Metric':10} | {'Value':7}")
            output_lines.append("-" * 20)
            output_lines.append(f"Precision  | {p:.4f}")
            output_lines.append(f"Recall     | {r:.4f}")
            output_lines.append(f"F1-Score   | {f1:.4f}")
        else:
            output_lines.append(f"{'Averaging':10} | {'Precision':9} | {'Recall':7} | {'F1-Score':8}")
            output_lines.append("-" * 43)
            for avg in ['micro', 'macro', 'weighted']:
                p, r, f1 = res[avg]
                output_lines.append(f"{avg.capitalize():10} | {p:9.4f} | {r:7.4f} | {f1:8.4f}")

        acc_exact = group_accuracy(y_true_bin, y_pred_bin, indices)
        if np.isnan(acc_exact):
            output_lines.append("Accuracy (exact match of all predictions): No valid samples")
        else:
            output_lines.append(f"Accuracy (exact match of all predictions): {acc_exact:.4f}")

        acc_at_least_one = group_accuracy_at_least_one(y_true_bin, y_pred_bin, indices)
        if np.isnan(acc_at_least_one):
            output_lines.append("Accuracy (at least one match): No valid samples")
        else:
            output_lines.append(f"Accuracy (at least one match): {acc_at_least_one:.4f}")


# ------------------------------------------------------------
# Function: evaluate_by_pos
# Purpose: Perform evaluation for each part-of-speech (Wortart).
# Formatted output analogous to overall metrics.
# ------------------------------------------------------------
def evaluate_by_pos(df, output_lines):
    output_lines.append("\n=== Evaluation per part of speech ===")
    for part_of_speech in sorted(df["Wortart"].dropna().unique()):
        mask = df["Wortart"] == part_of_speech
        if mask.sum() == 0:
            continue

        y_true_pos = df.loc[mask, "Konzept"].apply(parse_labels).apply(special_concept_handling).tolist()
        y_pred_pos = df.loc[mask, prediction_column].apply(parse_labels).tolist()

        mlb_wa = MultiLabelBinarizer()
        y_true_bin_wa = mlb_wa.fit_transform(y_true_pos)
        y_pred_bin_wa = mlb_wa.transform(y_pred_pos)
        labels_wa = mlb_wa.classes_

        output_lines.append(f"\n--- Part of speech: {part_of_speech} ---")
        try:
            metrics = overall_metrics(y_true_bin_wa, y_pred_bin_wa)
            output_lines.append(f"{'metrics':20} | value")
            output_lines.append("-" * 30)
            for name, value in metrics.items():
                output_lines.append(f"{name:20} | {value:.4f}")

            correct_at_least_one = np.sum(np.logical_and(y_true_bin_wa, y_pred_bin_wa).sum(axis=1) > 0)
            ratio_at_least_one = correct_at_least_one / y_true_bin_wa.shape[0]
            output_lines.append(f"Accuracy (at least one match): {ratio_at_least_one:.4f}")

            output_lines.append(f"\nReport for Part of speech '{part_of_speech}':")
            report = classification_report(y_true_bin_wa, y_pred_bin_wa, target_names=labels_wa, zero_division=0)
            for line in report.splitlines():
                output_lines.append("  " + line)
        except ValueError as e:
            output_lines.append(f"Not enough data for part of speech '{part_of_speech}' – {str(e)}")

# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------
def main():
    os.makedirs(output_dir, exist_ok=True)

    for filename in input_files:
        input_filepath = os.path.join(input_dir, filename)
        print(f"____________________________________________\n\n")
        print(f"Processing file: {input_filepath}")

        # --- Load input file ---
        df = pd.read_csv(input_filepath, sep="\t")

        # --- Parse labels ---
        y_true = df["Konzept"].apply(parse_labels).apply(special_concept_handling).tolist()
        y_pred = df[prediction_column].apply(parse_labels).tolist()


        # --- Binarize multi-label data ---
        mlb = MultiLabelBinarizer()
        y_true_bin = mlb.fit_transform(y_true)
        y_pred_bin = mlb.transform(y_pred)
        labels = mlb.classes_

        output_lines = []

        # --- Overall metrics ---
        metrics = overall_metrics(y_true_bin, y_pred_bin)
        print_overall_metrics(metrics, output_lines)

        # --- Detailed classification report ---
        print_classification_report(y_true_bin, y_pred_bin, labels, output_lines, 
                                    title="Precision/Recall/F1 per concept")

        # --- Subset accuracies ---
        print_subset_accuracies(y_true_bin, y_pred_bin, output_lines)

        # --- Metrics per group ---
        evaluate_groups(y_true_bin, y_pred_bin, labels, groups, output_lines)

        # --- Evaluation per Wortart ---
        evaluate_by_pos(df, output_lines)

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
            output_path = os.path.join(output_dir, f"{basename}precision_recall_basis_{prediction_column}.txt")
        else:
            output_path = os.path.join(output_dir, f"{basename}precision_recall_basis.txt")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        # --- Print results to console ---
        print("\n".join(output_lines))
        print(f"\nResults were saved in: {output_path}")


if __name__ == "__main__":
    main()