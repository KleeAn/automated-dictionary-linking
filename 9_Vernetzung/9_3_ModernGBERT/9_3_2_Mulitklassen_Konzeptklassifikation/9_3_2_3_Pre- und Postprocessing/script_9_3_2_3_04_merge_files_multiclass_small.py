# ================================================================
# Merges multiple TSV files into a single consolidated output file.
# Cleans columns, removes unwanted ones, and aggregates duplicate
# entries by key columns while preserving order and unique values.
#
# Used to merge the predictions of the multiclass classification with
# small training data sets into a single file.
# ================================================================

import pandas as pd
import glob
import os


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
    # Load first TSV file (with header) and store original column order
    # ------------------------------------------------------------
    merged_df = pd.read_csv(tsv_files[0], sep="\t", dtype=str)
    original_columns = merged_df.columns.tolist()

    # ------------------------------------------------------------
    # Remove unwanted columns ("Top_3", "Top_5") if present
    # ------------------------------------------------------------
    for col in ["Top_3", "Top_5"]:
        if col in merged_df.columns:
            merged_df.drop(columns=col, inplace=True)

    # ------------------------------------------------------------
    # Remove spaces in "Top_1" column (if present)
    # ------------------------------------------------------------
    if "Top_1" in merged_df.columns:
        merged_df["Top_1"] = merged_df["Top_1"].str.replace(" ", "", regex=False)

    # ------------------------------------------------------------
    # Add helper column to track order
    # ------------------------------------------------------------
    merged_df["_order"] = range(len(merged_df))

    # ------------------------------------------------------------
    # Append remaining TSV files (skip header rows)
    # ------------------------------------------------------------
    for file in tsv_files[1:]:
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=original_columns, dtype=str)

        # Remove unwanted columns
        for col in ["Top_3", "Top_5"]:
            if col in df.columns:
                df.drop(columns=col, inplace=True)

        # Clean "Top_1" values
        if "Top_1" in df.columns:
            df["Top_1"] = df["Top_1"].str.replace(" ", "", regex=False)

        df["_order"] = range(len(df))
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # ------------------------------------------------------------
    # Normalize prediction label values (if applicable)
    # ------------------------------------------------------------
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace({"1.0000": "1", "0.0000": "0"})

    # ============================================================
    # Aggregation logic
    # ============================================================
    agg_keys = ["xml:id", "Lemma", "Lemma_bereinigt", "Wortart", "Level", "Definition"]

    def concat_unique(series):
        """Concatenates unique, non-empty values while preserving order."""
        seen = set()
        result = []
        for v in series:
            if pd.notna(v):
                v_str = str(v).strip()
                if v_str and v_str not in seen:
                    seen.add(v_str)
                    result.append(v_str)
        return "; ".join(result)

    # ------------------------------------------------------------
    # Group and aggregate data by defined key columns
    # ------------------------------------------------------------
    merged_df = (
        merged_df.groupby(agg_keys, dropna=False, sort=False, group_keys=False)
        .agg({
            "Konzept": concat_unique,
            "Top_1": concat_unique,
            **{col: "first" for col in merged_df.columns if col not in agg_keys + ["Konzept", "Top_1"]}
        })
        .reset_index()
    )

    # ------------------------------------------------------------
    # Restore original column order (excluding removed ones)
    # ------------------------------------------------------------
    filtered_columns = [col for col in original_columns if col in merged_df.columns and col not in ["Top_3", "Top_5"]]
    merged_df = merged_df[filtered_columns]

    # ------------------------------------------------------------
    # Save final merged file
    # ------------------------------------------------------------
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Merged {len(tsv_files)} TSV files → {output_file}")


# ================================================================
# Execution
# ================================================================
if __name__ == "__main__":
    input_folder = ""  # specify folder path containing TSV files
    output_file = "A_Trinken_multiclass_small.tsv"
    merge_tsv_files(input_folder, output_file)
