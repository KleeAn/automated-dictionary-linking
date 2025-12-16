import pandas as pd
import glob
import os
import random

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
        df = pd.read_csv(file, sep="\t", skiprows=1, header=None, names=merged_df.columns, dtype=str)
        merged_df = pd.concat([merged_df, df], ignore_index=True)
        
    # Werte in Pred_Label-Spalte anpassen (nur falls Spalte existiert)
    if "Pred_Label" in merged_df.columns:
        merged_df["Pred_Label"] = (
            merged_df["Pred_Label"]
            .replace(["1.0000", "1.0"], "1")
            .replace(["0.0000", "0.0"], "0")
        )

    print(f"Zusammengeführt: {len(tsv_files)} Dateien → {output_file}")

    # --- NEUER TEIL: Dublettenprüfung und Bereinigung ---
    duplicate_columns = ["xml:id", "Lemma", "Wortart", "Level", "Definition"]
    if not all(col in merged_df.columns for col in duplicate_columns):
        print("Warnung: Nicht alle benötigten Spalten für Dublettenprüfung vorhanden.")
    else:
        merged_df = resolve_duplicates(merged_df, duplicate_columns)

    # Ergebnis speichern
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Endergebnis gespeichert: {output_file} ({len(merged_df)} Zeilen)")

def resolve_duplicates(df, key_columns):
    """Behandelt Dubletten gemäß den definierten Regeln."""
    if "Pred_Label" not in df.columns:
        print("Keine 'Pred_Label'-Spalte gefunden, Dubletten werden einfach entfernt.")
        return df.drop_duplicates(subset=key_columns, keep="first")

    # Normalisiere Pred_Label-Werte
    df["Pred_Label"] = df["Pred_Label"].replace(["1.0000", "1.0"], "1").replace(["0.0000", "0.0"], "0")

    result_rows = []
    grouped = df.groupby(key_columns, dropna=False)

    for _, group in grouped:
        if len(group) == 1:
            result_rows.append(group.iloc[0])
        else:
            labels = group["Pred_Label"].tolist()

            # Prüfe, ob alle Pred_Label-Werte gleich sind
            if len(set(labels)) == 1:
                # alle gleich -> behalte erste
                result_rows.append(group.iloc[0])
            else:
                # Unterschiedlich -> häufigstes Pred_Label finden
                most_common = pd.Series(labels).value_counts()
                top_label = most_common.index[0]
                top_count = most_common.iloc[0]

                # Prüfen, ob es Gleichstand gibt
                tied = most_common[most_common == top_count]
                if len(tied) > 1:
                    # Gleichstand -> zufällig eine Zeile aus diesen auswählen
                    possible = group[group["Pred_Label"].isin(tied.index)]
                    chosen = possible.sample(n=1, random_state=random.randint(0, 9999))
                    result_rows.append(chosen.iloc[0])
                else:
                    # Eindeutiger Gewinner
                    chosen = group[group["Pred_Label"] == top_label].iloc[0]
                    result_rows.append(chosen)

    result_df = pd.DataFrame(result_rows)
    print(f"Dublettenprüfung abgeschlossen: {len(df)} → {len(result_df)} Zeilen")
    return result_df

if __name__ == "__main__":
    input_folder = ""  # <-- hier Pfad zu den TSV-Dateien angeben
    output_file = "A_B_C_gesamt_binär_klein_10f_32bz_3e.tsv"
    merge_tsv_files(input_folder, output_file)
