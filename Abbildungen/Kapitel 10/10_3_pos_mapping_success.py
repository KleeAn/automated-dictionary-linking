# ================================================================
# Analyzes and plots mapping success rates per method based
# on part-of-speech from a TSV corpus.
# ================================================================

import csv
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

# File path
tsv_datei = "A_B_C_gesamt_alle_methoden.tsv"

# Methods
method_columns = ["ModernGBERT", "Llama3.3:70b", "Stringabgleich"]

# Target POS tags
target_pos = ["Substantiv", "Verb", "Adjektiv"]
pos_column = "Wortart"

# Containers
pos_tags = []
mapping_results_pos = {method: [] for method in method_columns}

# --- Read TSV ---
with open(tsv_datei, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter='\t')
    for row in reader:
        pos = row.get(pos_column, "UNK")
        if pos not in target_pos:
            continue  # ignore others

        pos_tags.append(pos)

        for method in method_columns:
            quote = row.get(method, "0/1")
            try:
                num, den = map(int, quote.split("/"))
                success = 1 if num > 0 else 0
            except:
                success = 0
            mapping_results_pos[method].append(success)

# --- Fix order: Substantiv, Verb, Adjektiv ---
pos_sorted = target_pos
x_positions = np.arange(len(pos_sorted))

# --- Calculate success rates ---
success_rates_pos = {}
for method, results in mapping_results_pos.items():
    pos_success = Counter()
    pos_fail = Counter()
    for p, success in zip(pos_tags, results):
        (pos_success if success else pos_fail)[p] += 1

    rates = []
    for p in pos_sorted:
        corr = pos_success[p]
        tot = pos_success[p] + pos_fail[p]
        rates.append(corr/tot if tot>0 else 0)
    success_rates_pos[method] = rates

# --- Plot ---
plt.figure(figsize=(8,5))
colors = ["blue","green","red"]
markers = ["o","s","D"]

for c,m,method in zip(colors,markers,method_columns):
    plt.plot(x_positions, success_rates_pos[method],
             marker=m, linestyle='-', label=method, color=c)

plt.xticks(x_positions, labels=pos_sorted, rotation=0)
plt.xlabel('Wortart')
plt.ylabel('Mappingerfolgsrate')
plt.title('Mappingerfolgsrate pro Wortart')
plt.ylim(0.7,1.01)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig("10_3_erfolgsrate_wortart.png", dpi=300)
plt.show()
