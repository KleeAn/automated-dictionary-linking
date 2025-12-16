# ================================================================
# Script for evaluating and analyzing mapped concept data. (Wurzelkonzepte)
#
# Purpose:
#   Compares original concept annotations with mapped results,
#   based on their root concepts, calculates accuracy metrics,
#   and generates statistics.
# ================================================================

import pandas as pd
import os
import re

# ------------------------------------------------------------
# User setting: choose which mapped column to use
# Options:
#   "Konzept_gemappt"   -> use "Konzept_gemappt" (method "Stringabgleich")
#   "Top_1"             -> use "Top_1"
#   "Top_3"             -> use "Top_3"
#   "Top_5"             -> use "Top_5"
# ------------------------------------------------------------
mapping_choice = "Konzept_gemappt" 

# ------------------------------------------------------------
# Constants / File paths
# ------------------------------------------------------------
method_dir = "llama_3.3_70b" #"modernbert" #"llama_3.3_70b" #"Stringabgleich"
input_dir = os.path.join(method_dir, "input")
output_dir = os.path.join(method_dir, "output")
input_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".tsv")]

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# ------------------------------------------------------------
# Function to determine which column to use as mapped concept
# ------------------------------------------------------------
def get_mapped_column(df):
    if mapping_choice in df.columns:
        return mapping_choice
    print(f"Column '{mapping_choice}' not found in data. Falling back to 'Konzept_gemappt'.")
    return "Konzept_gemappt"

# ------------------------------------------------------------
# Function: extract_root
# Purpose: Extracts the root concept.
# ------------------------------------------------------------
def extract_root(concept):
    concept = concept.strip()
    root = concept.split('.')[0].strip() if '.' in concept else concept
    return root.lower()

# ------------------------------------------------------------
# Function: classify_root_match
# Purpose: Classifies the match type between source and mapped
#          root concepts. Categories:
#          - "perfekt": All roots exactly match
#          - "voll": All source roots are present in mapped roots, but probably extra roots exist
#          - "teils": Some roots match, but not all
#          - "kein": No matching roots or mapped list empty
# ------------------------------------------------------------
def classify_root_match(concepts_str, mapped_str):
    concepts = [c.strip() for c in concepts_str.split(";") if c.strip()]
    roots_source = set(extract_root(c) for c in concepts)

    mapped = [m.strip() for m in mapped_str.split(";") if m.strip()]
    roots_mapped = set(extract_root(m) for m in mapped)

    common = roots_source.intersection(roots_mapped)

    if not roots_mapped:
        return "kein"
    elif roots_source == roots_mapped:
        return "perfekt"
    elif roots_source.issubset(roots_mapped):
        return "voll"
    elif common:
        return "teils"
    else:
        return "kein"

# ------------------------------------------------------------
# Main processing loop
# ------------------------------------------------------------
for filename in input_files:
    input_path = os.path.join(input_dir, filename)
    try:
        df = pd.read_csv(input_path, sep="\t")
        print(f"\n Processing file: {filename} — {len(df)} rows")

        # --- choice column ---
        mapped_col = get_mapped_column(df)
        print(f"Selected column for evaluation: '{mapped_col}'")

        df["Konzeptübereinstimmung"] = df.apply(
            lambda row: classify_root_match(str(row["Konzept"]), str(row[mapped_col])),
            axis=1
        )

        stats = df["Konzeptübereinstimmung"].value_counts().reindex(
            ["perfekt", "voll", "teils", "kein"], fill_value=0
        )
        total = len(df)
        stats_df = pd.DataFrame({
            "Kategorie": stats.index,
            "Anzahl": stats.values,
            "Prozent": [round((count / total) * 100, 2) for count in stats.values]
        })

        print("\nRoot concept match statistics:")
        for _, row in stats_df.iterrows():
            print(f"   {row['Kategorie']:<7} {int(row['Anzahl']):>6} rows ({row['Prozent']:6.2f}%)")

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
                basename = filename_no_ext.split("_wurzelkonzepte")[0] + "_"
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
            output_tsv_all = os.path.join(output_dir, f"{basename}accuracy_wurzel_{mapping_choice}.tsv")
            output_tsv_stats = os.path.join(output_dir, f"{basename}accuracy_wurzel_statistik_{mapping_choice}.tsv")            
        else:
            output_tsv_all = os.path.join(output_dir, f"{basename}accuracy_wurzel.tsv")
            output_tsv_stats = os.path.join(output_dir, f"{basename}accuracy_wurzel_statistik.tsv")

        df.to_csv(output_tsv_all, sep="\t", index=False)
        stats_df.to_csv(output_tsv_stats, sep="\t", index=False)

        print(f"\nSaved files:\n- {output_tsv_all}\n- {output_tsv_stats}")

    except FileNotFoundError:
        print(f"File not found: {input_path}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")

