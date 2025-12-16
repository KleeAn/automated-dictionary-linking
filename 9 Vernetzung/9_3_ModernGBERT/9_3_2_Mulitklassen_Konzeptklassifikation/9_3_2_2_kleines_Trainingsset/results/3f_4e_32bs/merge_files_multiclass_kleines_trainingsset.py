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

    # Unerwünschte Spalten entfernen
    for col in ["Top_3", "Top_5"]:
        if col in merged_df.columns:
            merged_df.drop(columns=col, inplace=True)

    # Leerzeichen in Top_1-Spalte entfernen
    if "Top_1" in merged_df.columns:
        merged_df["Top_1"] = merged_df["Top_1"].str.replace(" ", "", regex=False)

    # Hilfsspalte für Reihenfolge
    merged_df["_order"] = range(len(merged_df))

    # Restliche Dateien einlesen (Header überspringen)
    for file in tsv_files[1:]:
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=original_columns, dtype=str)

        # Unerwünschte Spalten entfernen
        for col in ["Top_3", "Top_5"]:
            if col in df.columns:
                df.drop(columns=col, inplace=True)

        # Leerzeichen in Top_1-Spalte entfernen
        if "Top_1" in df.columns:
            df["Top_1"] = df["Top_1"].str.replace(" ", "", regex=False)

        df["_order"] = range(len(df))
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # Werte in Pred_Label-Spalte anpassen (optional)
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = merged_df["Pred_Label"].replace({"1.0000": "1", "0.0000": "0"})

    # --- NEU: Aggregation über xml:id, Lemma, Lemma_bereinigt, Wortart, Level, Definition ---
    agg_keys = ["xml:id", "Lemma", "Lemma_bereinigt", "Wortart", "Level", "Definition"]

    def concat_unique(series):
        """Fasst eindeutige, nicht-leere Werte zusammen, Reihenfolge beibehalten"""
        seen = set()
        result = []
        for v in series:
            if pd.notna(v):
                v_str = str(v).strip()
                if v_str and v_str not in seen:
                    seen.add(v_str)
                    result.append(v_str)
        return "; ".join(result)

    merged_df = (
        merged_df.groupby(agg_keys, dropna=False, sort=False, group_keys=False)
        .agg({
            "Konzept": concat_unique,
            "Top_1": concat_unique,
            **{col: "first" for col in merged_df.columns if col not in agg_keys + ["Konzept", "Top_1"]}
        })
        .reset_index()
    )

    # Original-Spaltenreihenfolge (ohne Top_3, Top_5)
    filtered_columns = [col for col in original_columns if col in merged_df.columns and col not in ["Top_3", "Top_5"]]
    merged_df = merged_df[filtered_columns]

    # Ergebnis speichern
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Zusammengeführt: {len(tsv_files)} Dateien → {output_file}")

if __name__ == "__main__":
    input_folder = ""  # Hier den Ordnerpfad angeben
    output_file = "A_Trinken_klein_3f_32bs_4e.tsv"
    merge_tsv_files(input_folder, output_file)
