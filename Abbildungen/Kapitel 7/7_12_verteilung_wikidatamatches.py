# ================================================================
# Script for generating a pie chart showing the proportion of
# entries with and without a Wikidata match.
# ================================================================

import matplotlib.pyplot as plt

# Data for the pie chart
labels = [
    "Einträge mit\nWikidata-Match", 
    "Einträge ohne\nWikidata-Match", 
]
sizes = [50.37, 49.63]
colors = ['#A8CBB7', '#A18EC4']

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

# Save as PNG and SVG
plt.savefig('7_12_tortendiagramm_verteilung_wikidatamatches.png', format='png', bbox_inches='tight')  # Save as PNG
# plt.savefig('7_tortendiagramm_verteilung_wikidatamatches.svg', format='svg', bbox_inches='tight')  # Save as SVG

# Display chart
plt.show()
