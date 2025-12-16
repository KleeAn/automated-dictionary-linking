# ================================================================
# Script for color-coded treemap visualizing concepts
# and their frequencies in a controlles vocabulary.
# ================================================================

import plotly.graph_objects as go
import colorsys
import numpy as np

# --- Concepts ---
labels = [
    "trinken", "Durst", "Getränk",
    # Subcategories of Trinken
    "trinken<br>(allg.)", "langsam/<br>kleine Mengen", "schnell/<br>große<br>Mengen", "austrinken", "geräuschvoll", "Alkohol trinken",
    # Subcategories of Getränk
    "Alkoholfreies<br>Kaltgetränk", "Alkoholhaltiges<br>Kaltgetränk", "Alkoholfreies<br>Heißgetränk", "Alkoholhaltiges<br>Heißgetränk"
]

parents = [
    "", "", "",
    "trinken", "trinken", "trinken", "trinken", "trinken", "trinken",
    "Getränk", "Getränk", "Getränk", "Getränk"
]

values = [
    140, 35, 365,
    18, 6, 18, 8, 3, 87,
    108, 159, 67, 20
]

# --- Transform values for more compact visualization ---
adjusted_values = [np.sqrt(v) for v in values]

# --- Color utility functions ---
def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16)/255 for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(x*255) for x in rgb)

def darken_color(hex_color, factor):
    rgb = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = max(0, l * factor)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((r, g, b))

# --- Compute depths ---
def compute_depths(labels, parents):
    depth_map = {}
    label_to_parent = dict(zip(labels, parents))
    for label in labels:
        depth = 0
        current = label
        while label_to_parent.get(current, "") != "":
            current = label_to_parent[current]
            depth += 1
        depth_map[label] = depth
    return depth_map

depths = compute_depths(labels, parents)

# --- Assign root colors ---
roots = [label for label, parent in zip(labels, parents) if parent == ""]
base_colors = ["#6AB7FF", "#FFA500", "#90b99d"]  # Blue, orange, green
root_color_map = {root: base_colors[i % len(base_colors)] for i, root in enumerate(roots)}

# --- Colors for each label ---
def find_root(label, label_to_parent):
    current = label
    while label_to_parent.get(current, "") != "":
        current = label_to_parent[current]
    return current

label_to_parent = dict(zip(labels, parents))
colors = []
for label in labels:
    root = find_root(label, label_to_parent)
    base_color = root_color_map[root]
    depth = depths[label]
    color = darken_color(base_color, 1 - depth * 0.2)
    colors.append(color)

# --- Create Treemap ---
fig = go.Figure(go.Treemap(
    labels=labels,
    parents=parents,
    values=adjusted_values,   # transformed values for more compact layout
    customdata=values,        # real values as additional info
    marker=dict(colors=colors),
    branchvalues="remainder",
    texttemplate="%{label}<br>%{customdata}",
    textfont=dict(color="white", size=22),
    tiling=dict(
        pad=2,
        flip='x',
        packing='squarify',
        squarifyratio=1.2
    )
))

# Make layout more compact
fig.update_layout(
    width=1100,
    height=770,
    margin=dict(t=50, l=25, r=25, b=25)
)

# Save image
# fig.write_html("treemap_vokabular_verteilung.html")
fig.write_image("7_9_treemap_konzeptverteilung.png", width=1200, height=1000, scale=3)

fig.show()
