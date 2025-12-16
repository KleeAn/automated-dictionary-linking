# ================================================================
# Merges multiple TSV files into a single consolidated output file.
# Includes duplicate resolution logic based on defined key columns.
# Used to merge the predictions of the binary classification with small
# training data sets into a single file.
#
# - Retains headers from the first file only.
# - Normalizes prediction labels ("1.0000"/"1.0" → "1", "0.0000"/"0.0" → "0").
# - Resolves duplicates using defined rules for "Pred_Label".
# ================================================================

import pandas as pd
import glob
import os
import random


def merge_tsv_files(input_folder, output_file):
    # ------------------------------------------------------------
    # Locate all TSV files in the input folder
    # (excluding the designated output file)
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
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=merged_df.columns, dtype=str)
        merged_df = pd.concat([merged_df, df], ignore_index=True)
        
    # ------------------------------------------------------------
    # Normalize prediction label values (if applicable)
    # ------------------------------------------------------------
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = (
            merged_df["Pred_Label"]
            .replace(["1.0000", "1.0"], "1")
            .replace(["0.0000", "0.0"], "0")
        )

    print(f"Merged {len(tsv_files)} TSV files → {output_file}")

    # ------------------------------------------------------------
    # Duplicate detection and resolution
    # ------------------------------------------------------------
    duplicate_columns = ["xml:id", "Lemma", "Wortart", "Level", "Definition"]
    if not all(col in merged_df.columns for col in duplicate_columns):
        print("Warning: Not all required columns for duplicate check are present.")
    else:
        merged_df = resolve_duplicates(merged_df, duplicate_columns)

    # ------------------------------------------------------------
    # Save merged and cleaned file
    # ------------------------------------------------------------
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Final output saved: {output_file} ({len(merged_df)} rows)")


# ================================================================
# Duplicate resolution logic
# ================================================================
def resolve_duplicates(df, key_columns):
    """Resolves duplicate rows according to defined rules."""
    
    # ------------------------------------------------------------
    # If no 'Pred_Label' column exists, drop duplicates directly
    # ------------------------------------------------------------
    if "Pred_Label" not in df.columns:
        print("No 'Pred_Label' column found — duplicates removed directly.")
        return df.drop_duplicates(subset=key_columns, keep="first")

    # ------------------------------------------------------------
    # Normalize 'Pred_Label' values before processing
    # ------------------------------------------------------------
    df["Pred_Label"] = df["Pred_Label"].replace(["1.0000", "1.0"], "1").replace(["0.0000", "0.0"], "0")

    result_rows = []
    grouped = df.groupby(key_columns, dropna=False)

    # ------------------------------------------------------------
    # Process each group of potential duplicates
    # ------------------------------------------------------------
    for _, group in grouped:
        if len(group) == 1:
            result_rows.append(group.iloc[0])
        else:
            labels = group["Pred_Label"].tolist()

            # All labels identical → keep first
            if len(set(labels)) == 1:
                result_rows.append(group.iloc[0])
            else:
                # Find most frequent label
                most_common = pd.Series(labels).value_counts()
                top_label = most_common.index[0]
                top_count = most_common.iloc[0]

                # ----------------------------------------------------
                # Tie case → randomly select one of the tied rows
                # ----------------------------------------------------
                tied = most_common[most_common == top_count]
                if len(tied) > 1:
                    possible = group[group["Pred_Label"].isin(tied.index)]
                    chosen = possible.sample(n=1, random_state=random.randint(0, 9999))
                    result_rows.append(chosen.iloc[0])
                else:
                    # Clear winner → keep that one
                    chosen = group[group["Pred_Label"] == top_label].iloc[0]
                    result_rows.append(chosen)

    result_df = pd.DataFrame(result_rows)
    print(f"Duplicate resolution completed: {len(df)} → {len(result_df)} rows")
    return result_df


# ================================================================
# Execution
# ================================================================
if __name__ == "__main__":
    input_folder = ""  # specify folder path containing TSV files
    output_file = "A_B_C_gesamt_binary_small.tsv"
    merge_tsv_files(input_folder, output_file)
