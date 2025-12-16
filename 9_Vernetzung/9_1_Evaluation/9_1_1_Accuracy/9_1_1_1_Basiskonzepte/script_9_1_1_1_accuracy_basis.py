# ================================================================
# Script for evaluating and analyzing mapped concept data. (Basiskonzepte)
#
# Purpose:
#   Compares original concept annotations with mapped results,
#   calculates accuracy metrics, and generates detailed statistics.
# ================================================================

import pandas as pd
from collections import Counter
import os
import re

# ------------------------------------------------------------
# User setting: choose which mapped column to use
# Options:
#   "Konzept_gemappt"  -> use "Konzept_gemappt"
#   "Top_1"             -> use "Top_1"
#   "Top_3"             -> use "Top_3"
#   "Top_5"             -> use "Top_5"
# ------------------------------------------------------------
mapping_choice = "Konzept_gemappt"

# ------------------------------------------------------------
# Constants / File paths
# ------------------------------------------------------------
method_dir = "llama_3.3_70b" #"llama_3.3_70b" #"qwen_2.5_72b" #"qwen_2.5_32b" #"llama_3.1_8b" #"llama_3.3_70b" #"stringabgleich" #"modernbert"
input_dir = os.path.join(method_dir, "input")
output_dir = os.path.join(method_dir, "output")
input_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".tsv")]

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# ------------------------------------------------------------
# Function to determine which column to use as "Konzept_gemappt"
# ------------------------------------------------------------
def get_mapped_column(df):
    if mapping_choice in df.columns:
        return mapping_choice
    print(f"Column '{mapping_choice}' not found in data. Falling back to 'Konzept_gemappt'.")
    return "Konzept_gemappt"

# ------------------------------------------------------------
# Function: compare_concepts
# Purpose: Compare original and mapped concepts.
# Returns: Match ratio and number of incorrect extra concepts.
# ------------------------------------------------------------
def compare_concepts(concepts_str, mapped_str):
    # Split and clean concept lists
    concepts = [c.strip() for c in concepts_str.split(";") if c.strip()]

    # Special case: replace specific concept "Trinken.Häufig_lange_trinken"
    if "Trinken.Häufig_lange_trinken" in concepts:
        concepts = ["Trinken"] if len(concepts) == 1 else [
            c for c in concepts if c != "Trinken.Häufig_lange_trinken"
        ]

    mapped = [m.strip() for m in mapped_str.split(";") if m.strip()]

    # Calculate match ratio
    total = len(concepts)
    correct = sum(1 for c in concepts if c in mapped)
    ratio = f"{correct}/{total}" if total > 0 else "0/0"

    # Count additional incorrect concepts
    wrong_additional = sum(1 for m in mapped if m not in concepts)

    return pd.Series([ratio, wrong_additional])

# ------------------------------------------------------------
# Function: same_concepts
# Purpose: Check if two concept sets are exactly the same,
#          ignoring order.
# ------------------------------------------------------------
def same_concepts(concepts_str, mapped_str):
    return set(c.strip() for c in concepts_str.split(";") if c.strip()) == \
           set(m.strip() for m in mapped_str.split(";") if m.strip())

# ------------------------------------------------------------
# Function: extract_concept_group
# Purpose: Extract main concept group from concept string.
#          Returns one of predefined groups or "Andere".
# ------------------------------------------------------------
def extract_concept_group(concept):
    if pd.isna(concept):
        return "Andere"
    group = str(concept).split(";")[0].split(".")[0].strip()
    return group if group in {"Getränk", "Trinken", "Durst", "kein_Trinken"} else "Andere"

# ------------------------------------------------------------
# Function: table_ratio_stats
# Purpose: Create table showing distribution of match ratios.
# ------------------------------------------------------------
def table_ratio_stats(df):
    return pd.DataFrame(
        sorted(Counter(df["Quote"]).items()),
        columns=["Quote", "Anzahl"]
    )

# ------------------------------------------------------------
# Function: table_percentage
# Purpose: Create percentage table for a given column and subset.
# ------------------------------------------------------------
def table_percentage(df, column_name, subset, label):
    total_counts = df[column_name].value_counts().sort_index()
    subset_counts = subset[column_name].value_counts().sort_index()

    table = pd.DataFrame({
        column_name: total_counts.index,
        "Gesamt": total_counts.values,
        label: [subset_counts.get(k, 0) for k in total_counts.index]
    })
    table["%"] = (table[label] / table["Gesamt"]) * 100
    return table

# ------------------------------------------------------------
# Function: process_file
# Purpose: Process one mapping result file.
#          Calculates statistics, prints summary,
#          and exports results as TSV and Excel.
# ------------------------------------------------------------
def process_file(filename):
    # --- Load file ---
    path = os.path.join(input_dir, filename)
    try:
        df = pd.read_csv(path, sep="\t")
    except FileNotFoundError:
        print(f"File not found: {path}")
        return
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return

    print(f"\nProcessing file: {filename} ({len(df)} rows)")

    # --- Determine which column to use ---
    mapped_col = get_mapped_column(df)
    print(f"Selected column for evaluation: '{mapped_col}'")

    # --- Calculate match metrics ---
    df[["Quote", "Falsche Zusätzliche"]] = df.apply(
        lambda r: compare_concepts(str(r["Konzept"]), str(r[mapped_col])),
        axis=1
    )
    df["ExaktGleich"] = df.apply(
        lambda r: same_concepts(str(r["Konzept"]), str(r[mapped_col])),
        axis=1
    )

    # --- Create relevant subsets ---
    relevant = df[df["Quote"].isin({"1/1", "1/2", "1/3", "2/2", "2/3", "2/4"})].copy()
    complete = df[df["Quote"].isin({"1/1", "2/2", "3/3", "4/4"})].copy()
    exact = df[df["ExaktGleich"]].copy()

    relevant["Konzeptgruppe"] = relevant["Konzept"].apply(extract_concept_group)
    complete["Konzeptgruppe"] = complete["Konzept"].apply(extract_concept_group)
    exact["Konzeptgruppe"] = exact["Konzept"].apply(extract_concept_group)

    # --- Print ratio statistics ---
    print("\nRatio statistics:")
    ratio_tab = table_ratio_stats(df)
    print(ratio_tab)

    # --- Additional incorrect concepts in relevant subset ---
    wrong_in_relevant = (relevant["Falsche Zusätzliche"] > 0).sum()
    total_rows = len(df)
    print(f"\n{wrong_in_relevant} of {len(relevant)} rows in relevant ratios contain additional incorrect concepts.")

    # --- Summary metrics ---
    relevant_count = len(relevant)
    print(f"\nShare of rows with at least one exact match: "
          f"{relevant_count} of {total_rows} = {relevant_count / total_rows * 100:.2f}%")

    complete_count = len(complete)
    print(f"\nShare of rows with all desired concepts: "
          f"{complete_count} of {total_rows} = {complete_count / total_rows * 100:.2f}%")

    exact_count = len(exact)
    print(f"\nShare of perfectly mapped rows: "
          f"{exact_count} of {total_rows} = {exact_count / total_rows * 100:.2f}%\n")

    # --- Optional: Part-of-speech statistics ---
    if "Wortart" in df.columns:
        print("\nPart-of-speech statistics:")
        print(table_percentage(df, "Wortart", relevant, "Mind. 1 Exact Match"))
        print()
        print(table_percentage(df, "Wortart", complete, "Alle Konzepte"))
        print()
        print(table_percentage(df, "Wortart", exact, "Perfekt gemappt"))
        print()
    else:
        print("\nℹColumn 'Wortart' not found – skipping POS table.")

    # --- Concept group statistics ---
    print("\nConcept group statistics:")
    df["Konzeptgruppe"] = df["Konzept"].apply(extract_concept_group)
    print(table_percentage(df, "Konzeptgruppe", relevant, "Mind. 1 Exact Match"))
    print()
    print(table_percentage(df, "Konzeptgruppe", complete, "Alle Konzepte"))
    print()
    print(table_percentage(df, "Konzeptgruppe", exact, "Perfekt gemappt"))
    print()

    # --- Accuracy summary table ---
    accuracy_df = pd.DataFrame([{
            "Metrik": "Anteil Zeilen mit mindestens einem Exact Match",
            "Treffer": relevant_count,
            "Gesamtzahl": total_rows,
            "Prozent": round(relevant_count / total_rows * 100, 2)
        }, {
            "Metrik": "Anteil Zeilen mit allen gesuchten Konzepten",
            "Treffer": complete_count,
            "Gesamtzahl": total_rows,
            "Prozent": round(complete_count / total_rows * 100, 2)
        }, {
            "Metrik": "Anteil perfekt gemappter Zeilen",
            "Treffer": exact_count,
            "Gesamtzahl": total_rows,
            "Prozent": round(exact_count / total_rows * 100, 2)
        }
    ])

    
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
        output_path = os.path.join(output_dir, f"{basename}accuracy_basis_{mapping_choice}.tsv")
    else:
        output_path = os.path.join(output_dir, f"{basename}accuracy_basis.tsv")
    
    df.to_csv(output_path, sep="\t", index=False)
    
    if method_dir == "modernbert":
        stats_path = os.path.join(output_dir, f"{basename}accuracy_basis_statistik_{mapping_choice}.xlsx")
    else:
       stats_path = os.path.join(output_dir, f"{basename}accuracy_basis_statistik.xlsx")
       
    with pd.ExcelWriter(stats_path) as writer:
        ratio_tab.to_excel(writer, sheet_name="Quoten", index=False)
        if "Wortart" in df.columns:
            table_percentage(df, "Wortart", relevant, "Mind. 1 Exact Match").to_excel(writer, sheet_name="Wortart_Exact", index=False)
            table_percentage(df, "Wortart", complete, "Alle Konzepte").to_excel(writer, sheet_name="Wortart_Voll", index=False)
            table_percentage(df, "Wortart", exact, "Perfekt gemappt").to_excel(writer, sheet_name="Wortart_Exakt", index=False)
        table_percentage(df, "Konzeptgruppe", relevant, "Mind. 1 Exact Match").to_excel(writer, sheet_name="Gruppe_Exact", index=False)
        table_percentage(df, "Konzeptgruppe", complete, "Alle Konzepte").to_excel(writer, sheet_name="Gruppe_Voll", index=False)
        table_percentage(df, "Konzeptgruppe", exact, "Perfekt gemappt").to_excel(writer, sheet_name="Gruppe_Exakt", index=False)
        accuracy_df.to_excel(writer, sheet_name="Accuracy_total", index=False)

    print(f"\nData saved to:\n- {output_path}\n- {stats_path}")

# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------
if __name__ == "__main__":
    for file in input_files:
        process_file(file)
