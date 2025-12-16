# ================================================================
# Merges binary and multiclass predication.
# If the binary classification predicts 0 (no affiliation with the
# field “Drinking” = class "kein_Trinken), the prediction of the
# multi-class classification is also set to “kein_Trinken".
# ================================================================

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------
# Define input and output directories
# ------------------------------------------------------------
input_dir = Path("input")
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# ------------------------------------------------------------
# Load binary dictionary (file 1)
# ------------------------------------------------------------
binary = pd.read_csv(
    input_dir / "A_B_C_gesamt_binär_10f_32bz_3e.tsv",   # results of binary classification
    sep="\t",
    dtype=str
)

# Keep only relevant columns for merging
binary = binary[["xml:id", "Level", "Pred_Label"]]

# ------------------------------------------------------------
# Process all TSV files in input folder except the binary dictionary
# ------------------------------------------------------------
for file in input_dir.glob("*.tsv"):
    if file.name == "A_B_C_gesamt_binär_10f_32bz_3e.tsv":
        continue

    print(f"Verarbeite: {file.name}")

    # Load current TSV
    df = pd.read_csv(file, sep="\t", dtype=str)

    # ------------------------------------------------------------
    # Merge with binary dictionary
    # ------------------------------------------------------------
    merged = df.merge(
        binary,
        on=["xml:id", "Level"],
        how="left",
    )

    # ------------------------------------------------------------
    # Overwrite Top_1, Top_3, Top_5 if Pred_Label indicates '0'
    # ------------------------------------------------------------
    mask = merged["Pred_Label"].isin(["0", "0.0"])
    for col in ["Top_1", "Top_3", "Top_5"]:
        if col in merged.columns:
            merged.loc[mask, col] = "kein_Trinken"

    # ------------------------------------------------------------
    # Keep only original columns and remove duplicates
    # ------------------------------------------------------------
    merged = merged[df.columns]
    merged = merged.drop_duplicates()

    # ------------------------------------------------------------
    # Save processed file to output directory
    # ------------------------------------------------------------
    output_name = file.stem + "_final.tsv"
    merged.to_csv(output_dir / output_name, sep="\t", index=False)

# ------------------------------------------------------------
# Completion message
# ------------------------------------------------------------
print("Done! Files are saved in 'output/'.")
