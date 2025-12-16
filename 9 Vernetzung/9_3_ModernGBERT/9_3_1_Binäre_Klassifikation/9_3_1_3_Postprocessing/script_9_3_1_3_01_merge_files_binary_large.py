# ================================================================
# Merges multiple TSV files into a single consolidated output file.
# Used to merge the predictions of the binary classification into
# a single file.
#
# - Retains headers from the first file only.
# - Normalizes prediction labels ("1.0000" → "1", "0.0000" → "0").
# ================================================================

import pandas as pd
import glob
import os

def merge_tsv_files(input_folder, output_file):
    # ------------------------------------------------------------
    # Locate all TSV files in the input folder
    # ------------------------------------------------------------
    tsv_files = [
        f for f in glob.glob(os.path.join(input_folder, "*.tsv"))
        if os.path.abspath(f) != os.path.abspath(output_file)
    ]
    
    if not tsv_files:
        print("No TSV files found.")
        return

    # ------------------------------------------------------------
    # Load first TSV file (with header)
    # ------------------------------------------------------------
    merged_df = pd.read_csv(tsv_files[0], sep="\t", dtype=str)

    # ------------------------------------------------------------
    # Append remaining TSV files (skip header rows)
    # ------------------------------------------------------------
    for file in tsv_files[1:]:
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=merged_df.columns)
        merged_df = pd.concat([merged_df, df], ignore_index=True)
        
    # ------------------------------------------------------------
    # Normalize prediction label values (if applicable)
    # ------------------------------------------------------------
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace("1.0000", "1")
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace("0.0000", "0")

    # ------------------------------------------------------------
    # Save merged file
    # ------------------------------------------------------------
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Merged {len(tsv_files)} TSV files → {output_file}")


# ================================================================
# Execution
# ================================================================
if __name__ == "__main__":
    input_folder = ""  # specify folder path containing TSV files
    output_file = "A_B_C_gesamt_binary.tsv"
    merge_tsv_files(input_folder, output_file)
