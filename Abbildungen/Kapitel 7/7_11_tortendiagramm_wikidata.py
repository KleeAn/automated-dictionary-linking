# ================================================================
# Script for generating a pie chart visualizing the distribution
# of methods used for Wikidata matching.
# ================================================================

import matplotlib.pyplot as plt

# Data for the pie chart
labels = [
    "OpenRefine-Match", 
    "Wahl eines OpenRefine-Vorschlages", 
    "Eigenrecherche", 
    "Kein passendes Match"
]
sizes = [22.04, 24.07, 15, 38.89]
colors = ['#4682B4', '#FFB300', '#81C784', '#B71C1C']  # Colors for the segments

# Create the chart
plt.figure(figsize=(11, 8))
plt.pie(
    sizes,
    labels=labels,
    autopct='%1.2f%%',
    colors=colors,
    startangle=140,
    wedgeprops={'edgecolor': 'black'},
    textprops={'fontsize': 18}
)

# Set title with italic word
# plt.title("Ergebnis des Wikidata-Matchings", fontsize=18, fontweight='bold')

# Save as PNG and SVG
plt.savefig('7_11_tortendiagramm_wikidataverknüpfung.png', format='png')  # Save as PNG
#plt.savefig('tortendiagramm_wikidata.svg', format='svg')  # Save as SVG

# Display chart
plt.show()

