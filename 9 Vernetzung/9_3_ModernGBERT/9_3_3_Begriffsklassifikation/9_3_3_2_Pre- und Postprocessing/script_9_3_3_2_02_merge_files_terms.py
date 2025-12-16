# ================================================================
# Merges multiple TSV files into a single consolidated output file.
# Used to merge the predictions of the multiclass classification of
# lemma-definition pairs to terms.
#
# - Aggregates duplicate entries based on defined key columns.
# - Normalizes prediction labels ("1.0000" → "1", "0.0000" → "0").
# ================================================================

import pandas as pd
import glob
import os


def merge_tsv_files(input_folder, output_file):
    # ------------------------------------------------------------
    # Locate all TSV files in the input folder (exclude output file)
    # ------------------------------------------------------------
    tsv_files = [
        f for f in glob.glob(os.path.join(input_folder, "*.tsv"))
        if os.path.abspath(f) != os.path.abspath(output_file)
    ]
    
    if not tsv_files:
        print("No TSV files found.")
        return

    # ------------------------------------------------------------
    # Load the first TSV file (with header) and store column order
    # ------------------------------------------------------------
    merged_df = pd.read_csv(tsv_files[0], sep="\t", dtype=str)
    original_columns = merged_df.columns.tolist()

    # ------------------------------------------------------------
    # Remove spaces from top prediction columns (if present)
    # ------------------------------------------------------------
    for col in ["Top_1", "Top_3", "Top_5"]:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].str.replace(" ", "")

    # ------------------------------------------------------------
    # Add helper column to preserve order
    # ------------------------------------------------------------
    merged_df["_order"] = range(len(merged_df))

    # ------------------------------------------------------------
    # Append remaining TSV files (skip header rows)
    # ------------------------------------------------------------
    for file in tsv_files[1:]:
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=original_columns, dtype=str)
        
        # Remove spaces in top prediction columns
        for col in ["Top_1", "Top_3", "Top_5"]:
            if col in df.columns:
                df[col] = df[col].str.replace(" ", "")
        
        # Maintain order within each file
        df["_order"] = range(len(df))
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # ------------------------------------------------------------
    # Normalize prediction label values (if column exists)
    # ------------------------------------------------------------
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace({
            "1.0000": "1",
            "0.0000": "0"
        })

    # ------------------------------------------------------------
    # Define key and aggregation columns
    # ------------------------------------------------------------
    key_columns = ["xml:id", "Lemma", "Lemma_bereinigt", "Wortart", "Level", "Definition", "Konzept"]
    agg_columns = ["Begriff", "Top_1", "Top_3", "Top_5"]

    # ------------------------------------------------------------
    # Define aggregation function for unique merged values
    # ------------------------------------------------------------
    def agg_unique(values):
        seen = set()
        result = []
        for v in values:
            if pd.notna(v):
                # Split values by semicolon and trim whitespace
                for item in v.split(";"):
                    item_clean = item.strip()
                    if item_clean != "" and item_clean not in seen:
                        seen.add(item_clean)
                        result.append(item_clean)
        return "; ".join(result)

    # ------------------------------------------------------------
    # Group and aggregate if all key columns are present
    # ------------------------------------------------------------
    if all(col in merged_df.columns for col in key_columns):
        merged_df = (
            merged_df.groupby(key_columns, dropna=False, sort=False, as_index=False)
            .agg({
                col: agg_unique if col in agg_columns else "first"
                for col in merged_df.columns if col not in key_columns
            })
        )

    # ------------------------------------------------------------
    # Restore original column order
    # ------------------------------------------------------------
    merged_df = merged_df[[col for col in original_columns if col in merged_df.columns]]

    # ------------------------------------------------------------
    # Save merged output file
    # ------------------------------------------------------------
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Merged: {len(tsv_files)} files → {output_file}")


# ================================================================
# Execution
# ================================================================
if __name__ == "__main__":
    input_folder = ""  # Specify folder containing TSV files
    output_file = "A_Getränk_multiclass.tsv"
    merge_tsv_files(input_folder, output_file)
