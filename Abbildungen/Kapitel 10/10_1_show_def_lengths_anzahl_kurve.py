# ================================================================
# Plots the distribution of definition lengths (in tokens)
# from a TSV corpus file.
# ================================================================

import csv
from collections import Counter
import matplotlib.pyplot as plt

# Path to your TSV file
tsv_datei = "A_B_C_gesamt_alle_methoden.tsv"

definition_lengths = []

# Read TSV file
with open(tsv_datei, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter='\t')
    for row in reader:
        definition = row.get("Definition", "")
        tokens = definition.split()
        length = len(tokens)
        definition_lengths.append(length)

# Count frequencies
length_counter = Counter(definition_lengths)
lengths_sorted = sorted(length_counter.keys())
counts = [length_counter[l] for l in lengths_sorted]

# Create line plot
plt.figure(figsize=(12,6))
plt.plot(lengths_sorted, counts, marker='o', linestyle='-', color='blue')
plt.xlabel('Definitionslänge (Tokens)')
plt.ylabel('Anzahl Definitionen')
plt.title('Längenverteilung der Definitionen im Korpus')
plt.xticks(lengths_sorted)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# save the figure
plt.savefig("10_1_längenverteilung_defs.png", dpi=300, bbox_inches='tight')

plt.show()
