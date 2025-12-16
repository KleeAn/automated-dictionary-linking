# ================================================================
# Script for creating a pie chart visualizing the distribution
# of the root concepts "Trinken", "Durst", and "Getränk" in a corpus.
# ================================================================

import plotly.graph_objects as go

# Root concepts
labels = ["Trinken", "Durst", "Getränk"]
values = [396, 28, 753]

# Colors from your Matplotlib example
colors = ['#4682B4', '#FFB300', '#81C784']  # blue, orange, green

fig = go.Figure(go.Pie(
    labels=labels,
    values=values,
    marker=dict(colors=colors),
    textinfo='label+value+percent',  # shows label + percentage value
    textfont=dict(size=28),
    insidetextorientation='radial',
    showlegend=False  # hide legend
))

# Optional: adjust layout
fig.update_layout(
    width=600,
    height=600,
    margin=dict(t=40, b=0, l=0, r=0)
)

# Save graphic as PNG
fig.write_image("8_7_tortendiagramm_korpus_konzepte.png", width=800, height=800, scale=3)

fig.show()
