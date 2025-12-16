# ================================================================
# Script for creating a horizontal bar chart showing the frequency
# of different drinking concepts in a corpus.
# ================================================================

import plotly.graph_objects as go

# Labels
labels = [
    "Alkohol trinken  ", 
    "Trinken allgemein  ", 
    "Schnell/große Mengen trinken  ", 
    "Langsam/kleine Mengen trinken  ", 
    "Austrinken  ", 
    "Geräuschvoll trinken  ", 
    "Häufig/lange trinken  "
]

values = [182, 87, 45, 25, 21, 18, 18]

colors = [
    '#1f77b4',  # strong blue
    '#ff7f0e',  # orange
    '#2ca02c',  # green
    '#d62728',  # red
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2',  # pink
]

# Calculate percentages
total = sum(values)
percent_text = [f"{v} ({v/total:.1%})" for v in values]

# Horizontal bar chart
fig = go.Figure(go.Bar(
    x=values,
    y=labels,
    orientation='h',
    marker=dict(color=colors, line=dict(color='white', width=1)),
    text=percent_text,
    textposition='outside',
    textfont=dict(size=21)
))

# Layout
fig.update_layout(
    width=1260,
    height=875,
    margin=dict(t=30, l=180, r=20, b=30),
    xaxis=dict(
        title=dict(
            text="Anzahl",     
            font=dict(size=18)  
        ),
        range=[0, max(values)*1.2],
        tickfont=dict(size=14)
    ),
    yaxis=dict(
        tickfont=dict(size=22),
        autorange="reversed"
    )
)

# Save as PNG
fig.write_image("8_8_balkendiagramm_korpus_trinken.png", width=1240, height=875, scale=2)

# Display
fig.show()
