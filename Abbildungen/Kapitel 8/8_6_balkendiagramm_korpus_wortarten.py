# ================================================================
# Script for creating a stacked bar chart showing the
# distribution of word classes across subcorpora.
# ================================================================

import matplotlib.pyplot as plt
import numpy as np

# label corpora
teilkorpora = ['A "Trinken"', 'B "Verwandt"', 'C "Zufall"']

# Values for word classes
wortarten = [
    [770, 737, 726],  # nouns
    [323, 123, 221],  # verbs
    [7, 106, 85],     # adjectives
]

# Colors for word classes
farben_wortarten = ['#76b7b2', '#59a14f', '#edc948']

# Positions of the groups
x = np.arange(len(teilkorpora))
breite = 0.5  # width of the bars

fig, ax = plt.subplots(figsize=(10, 6))

# ---------------------
# Word classes (stacked bars)
# ---------------------
bottoms = np.zeros(len(teilkorpora))
wortarten_handles = []
for i in range(len(wortarten)):
    bar = ax.bar(
        x,
        wortarten[i],
        width=breite,
        bottom=bottoms,
        color=farben_wortarten[i],
        label=['Substantive', 'Verben', 'Adjektive'][i]  # labels remain in German
    )
    bottoms += wortarten[i]
    wortarten_handles.append(bar[0])

# Axes & labels
ax.set_ylabel('Anzahl Einträge')
ax.set_title('Zusammensetzung der Teilkorpora nach Wortarten')
ax.set_xticks(x)
ax.set_xticklabels(teilkorpora)

# Legend
ax.legend(title='Wortarten', loc='upper left', bbox_to_anchor=(1.02, 1))

plt.tight_layout()

# Save
plt.savefig('8_6_balkendiagramm_korpus_wortarten.png', dpi=500, bbox_inches='tight')
plt.show()
