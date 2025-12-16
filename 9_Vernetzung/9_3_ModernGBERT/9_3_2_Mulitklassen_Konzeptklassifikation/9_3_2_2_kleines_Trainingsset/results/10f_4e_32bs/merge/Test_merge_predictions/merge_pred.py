import pandas as pd
import glob
import os

# === Einstellungen ===
ordner_pfad = "./"        # Pfad zum Ordner mit den TSV-Dateien
ausgabe_datei = "zusammengeführt.tsv"  # Name der Ausgabedatei

# === Alle TSV-Dateien im Ordner finden ===
tsv_dateien = sorted(glob.glob(os.path.join(ordner_pfad, "*.tsv")))

if not tsv_dateien:
    print("Keine TSV-Dateien gefunden!")
else:
    print(f"{len(tsv_dateien)} TSV-Dateien gefunden.")

    dfs = []
    for i, datei in enumerate(tsv_dateien):
        print(f"Lese Datei {i+1}/{len(tsv_dateien)}: {datei}")
        if i == 0:
            # Erste Datei mit Header
            df = pd.read_csv(datei, sep="\t")
        else:
            # Ab der zweiten Datei Header überspringen
            df = pd.read_csv(datei, sep="\t", header=0)
        dfs.append(df)

    # Alle DataFrames zusammenführen
    gesamt = pd.concat(dfs, ignore_index=True)

    # In eine neue TSV-Datei schreiben
    gesamt.to_csv(ausgabe_datei, sep="\t", index=False)
    print(f"Alle Dateien wurden zu '{ausgabe_datei}' zusammengeführt.")
