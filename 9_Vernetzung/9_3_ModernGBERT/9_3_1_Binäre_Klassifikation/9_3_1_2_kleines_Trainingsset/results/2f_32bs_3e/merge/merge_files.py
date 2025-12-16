import pandas as pd
import glob
import os

def merge_tsv_files(input_folder, output_file):
    # Alle TSV-Dateien finden, Ausgabedatei ausschließen
    tsv_files = [
        f for f in glob.glob(os.path.join(input_folder, "*.tsv"))
        if os.path.abspath(f) != os.path.abspath(output_file)
    ]
    
    if not tsv_files:
        print("Keine TSV-Dateien gefunden.")
        return

    # Erste Datei mit Header einlesen
    merged_df = pd.read_csv(tsv_files[0], sep="\t", dtype=str)

    # Restliche Dateien: Header überspringen
    for file in tsv_files[1:]:
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=merged_df.columns)
        merged_df = pd.concat([merged_df, df], ignore_index=True)
        
    # Werte in Pred_Label-Spalte anpassen (nur falls Spalte existiert)
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace("1.0000", "1")
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace("0.0000", "0")

    # Ergebnis speichern
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Zusammengeführt: {len(tsv_files)} Dateien → {output_file}")

if __name__ == "__main__":
    input_folder = ""
    output_file = "A_B_C_gesamt_binär_klein_2f_32bz_3e.tsv"
    merge_tsv_files(input_folder, output_file)
