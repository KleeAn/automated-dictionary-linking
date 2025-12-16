# ================================================================
# Analyzes and plots mapping success rates per method based
# on definition length (tokens) from a TSV corpus.
# ================================================================

import csv
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2_contingency

# Path to your TSV corpus file
tsv_datei = "A_B_C_gesamt_alle_methoden.tsv"

# Column names for the methods
method_columns = ["ModernGBERT", "Llama3.3:70b", "Stringabgleich"]

# Prepare data structures
definition_lengths = []
mapping_results_per_method = {method: [] for method in method_columns}

# Read TSV file
with open(tsv_datei, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter='\t')
    for row in reader:
        definition = row.get("Definition", "")
        tokens = definition.split()
        length = len(tokens)
        # Group all lengths >= 10 as "10+"
        if length >= 10:
            length_label = "10+"
        else:
            length_label = length
        definition_lengths.append(length_label)

        # Mapping results for all methods
        for method in method_columns:
            quote = row.get(method, "0/1")
            try:
                numerator, denominator = map(int, quote.split("/"))
                success = 1 if numerator > 0 else 0
            except:
                success = 0
            mapping_results_per_method[method].append(success)

# Sort lengths
lengths_sorted = sorted(set(definition_lengths), key=lambda x: int(x) if isinstance(x,int) else 10)
x_positions = np.arange(len(lengths_sorted))  # evenly spaced

# Calculate success rates per method and length
success_rates_per_method = {}
for method, results in mapping_results_per_method.items():
    length_success = Counter()
    length_fail = Counter()
    for length, success in zip(definition_lengths, results):
        if success:
            length_success[length] += 1
        else:
            length_fail[length] += 1
    rates = []
    for l in lengths_sorted:
        correct = length_success[l]
        total = length_success[l] + length_fail[l]
        rate = correct / total if total > 0 else 0
        rates.append(rate)
    success_rates_per_method[method] = rates

# --- Print results to console ---
print("\nMapping success rates per method and token length:\n")
header = ["Token Length"] + method_columns
print("{:<12}".format(header[0]), end="")
for h in header[1:]:
    print("{:>15}".format(h), end="")
print()
print("-" * (12 + 15*len(method_columns)))

for i, l in enumerate(lengths_sorted):
    print("{:<12}".format(str(l)), end="")
    for method in method_columns:
        rate = success_rates_per_method[method][i]
        print("{:>15.2f}".format(rate), end="")
    print()

# Line plot for all methods
plt.figure(figsize=(10,6))
colors = ["blue", "green", "red"]
markers = ["o", "s", "D"]

for color, marker, method in zip(colors, markers, method_columns):
    plt.plot(x_positions, success_rates_per_method[method], marker=marker, linestyle='-', label=method, color=color)

plt.xticks(x_positions, labels=[str(l) for l in lengths_sorted])
plt.xlabel('Definitionslänge (Tokens)')
plt.ylabel('Mapping-Erfolgsrate')
plt.title('Mapping-Erfolgsrate nach Definitionslänge')
plt.ylim(0.8,1.01)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(loc='upper left')
plt.savefig("10_2_erfolgsrate_deflänge.png", dpi=300, bbox_inches='tight')
plt.show()
