# ================================================================
# Expands multi-concept assignments in a TSV file into separate rows.
# Used to prepare the input for a cross-validated training
# of a SentenceTransformer model for a multiclass classification of
# lemma-definition pairs to concepts.
#
# - All original columns are preserved.
# ================================================================

import pandas as pd
import os


def expand_multilabels(tsv_path: str, sep: str = ";"):
    # ------------------------------------------------------------
    # Check if input file exists
    # ------------------------------------------------------------
    if not os.path.exists(tsv_path):
        raise FileNotFoundError(f"File not found: {tsv_path}")

    # ------------------------------------------------------------
    # Load TSV into DataFrame and fill NaN values
    # ------------------------------------------------------------
    df = pd.read_csv(tsv_path, sep="\t", encoding="utf-8").fillna("")

    if "Konzept" not in df.columns:
        raise ValueError("TSV must contain a 'Konzept' column.")

    n_original = len(df)
    expanded_rows = []
    multi_count = 0

    # ------------------------------------------------------------
    # Iterate over rows and expand multi-concept entries
    # ------------------------------------------------------------
    for _, row in df.iterrows():
        concepts_raw = str(row["Konzept"]).strip()
        concepts = [c.strip() for c in concepts_raw.split(sep) if c.strip()]

        if len(concepts) > 1:
            multi_count += 1

        for c in concepts:
            new_row = row.copy()
            new_row["Konzept"] = c
            expanded_rows.append(new_row)

    # ------------------------------------------------------------
    # Create expanded DataFrame
    # ------------------------------------------------------------
    df_expanded = pd.DataFrame(expanded_rows)
    n_expanded = len(df_expanded)

    # ------------------------------------------------------------
    # Save expanded TSV
    # ------------------------------------------------------------
    out_path = os.path.join("input", "A_Trinken_expanded.tsv")
    df_expanded.to_csv(out_path, sep="\t", index=False, encoding="utf-8")

    print("Expansion completed")
    print(f"Original rows: {n_original}")
    print(f"Rows after expansion: {n_expanded}")
    print(f"Rows with multiple concepts: {multi_count}")
    print(f"Expanded file saved as: {out_path}")

    return df_expanded


# ================================================================
# Execution
# ================================================================
if __name__ == "__main__":
    tsv_path = "input/A_Trinken.tsv"
    expand_multilabels(tsv_path)
