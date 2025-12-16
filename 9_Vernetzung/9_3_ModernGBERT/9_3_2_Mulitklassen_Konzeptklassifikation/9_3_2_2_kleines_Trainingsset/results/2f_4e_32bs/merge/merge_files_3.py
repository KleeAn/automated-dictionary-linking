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

    # Erste Datei mit Header einlesen → Reihenfolge merken
    merged_df = pd.read_csv(tsv_files[0], sep="\t", dtype=str)
    original_columns = merged_df.columns.tolist()

    # Leerzeichen in Top-Spalten entfernen
    for col in ["Top_1", "Top_3", "Top_5"]:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].str.replace(" ", "")

    # Hilfsspalte für Reihenfolge
    merged_df["_order"] = range(len(merged_df))

    # Restliche Dateien: Header überspringen
    for file in tsv_files[1:]:
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=original_columns, dtype=str)
        
        # Leerzeichen in Top-Spalten entfernen
        for col in ["Top_1", "Top_3", "Top_5"]:
            if col in df.columns:
                df[col] = df[col].str.replace(" ", "")
        
        df["_order"] = range(len(df))  # innerhalb der Datei Reihenfolge behalten
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # Werte in Pred_Label-Spalte anpassen (nur falls Spalte existiert)
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace({"1.0000": "1", "0.0000": "0"})

    # Gruppierung und Aggregation
    key_columns = ["xml:id", "Lemma", "Lemma_bereinigt", "Wortart", "Level", "Definition"]
    agg_columns = ["Konzept", "Top_1", "Top_3", "Top_5"]

    def agg_unique(values):
        seen = set()
        result = []
        for v in values:
            if pd.notna(v):
                # Werte durch ; splitten
                for item in v.split(";"):
                    item_clean = item.strip()  # führende/trailing Leerzeichen entfernen
                    if item_clean != "" and item_clean not in seen:
                        seen.add(item_clean)
                        result.append(item_clean)
        return "; ".join(result)


    if all(col in merged_df.columns for col in key_columns):
        merged_df = (
            merged_df.groupby(key_columns, dropna=False, sort=False, as_index=False)
            .agg({col: agg_unique if col in agg_columns else "first" for col in merged_df.columns if col not in key_columns})
        )

    # Original-Spaltenreihenfolge wiederherstellen
    merged_df = merged_df[[col for col in original_columns if col in merged_df.columns]]

    # Ergebnis speichern
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Zusammengeführt: {len(tsv_files)} Dateien → {output_file}")

if __name__ == "__main__":
    input_folder = ""  # Ordner angeben
    output_file = "A_Trinken_klein_2f_32bz_4e.tsv"
    merge_tsv_files(input_folder, output_file)
