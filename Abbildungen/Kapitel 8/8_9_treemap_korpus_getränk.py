# ================================================================
# Script for creating a color-coded treemap visualizing beverage
# categories and their frequencies in a corpus.
# ================================================================

import plotly.graph_objects as go
import plotly.express as px
import colorsys

# --- Concept labels ---
labels = [
    "Getränk",         
    "Kaltgetränk", "Heißgetränk",    
    "Alkoholfreies<br>Kaltgetränk", "Alkoholhaltiges<br>Kaltgetränk", "Alkoholfreies<br>Heißgetränk", "Alkoholhaltiges<br>Heißgetränk",  
    "Kaltes<br>Milchgetränk", "Saft", "Wasser", "Softdrink", "Wein", "Spirituose", "Bier", "Kaffee", "Tee", "Kaffeeersatz", "Kakao", 
    "Sekt"
]

parents = [
    "", 
    "Getränk", "Getränk",       
    "Kaltgetränk", "Kaltgetränk", "Heißgetränk", "Heißgetränk",     
    "Alkoholfreies<br>Kaltgetränk", "Alkoholfreies<br>Kaltgetränk", "Alkoholfreies<br>Kaltgetränk", "Alkoholfreies<br>Kaltgetränk",
    "Alkoholhaltiges<br>Kaltgetränk", "Alkoholhaltiges<br>Kaltgetränk", "Alkoholhaltiges<br>Kaltgetränk", "Alkoholfreies<br>Heißgetränk",
    "Alkoholfreies<br>Heißgetränk", "Alkoholfreies<br>Heißgetränk", "Alkoholfreies<br>Heißgetränk",   
    "Wein"
]

values = [
    54,                                 
    0, 0,                
    0, 18, 1, 2,                                   
    59, 27, 15, 12, 273, 151, 42, 53, 23, 15, 3,   
    5                                              
]

adjusted_values = []

# Adjust some value sizes for better visual representation
for label, value in zip(labels, values):
    if label == "Sekt":
        adjusted_values.append(25)
    elif label == "Kakao":
        adjusted_values.append(5)
    elif label == "Alkoholhaltiges<br>Heißgetränk":
        adjusted_values.append(15)
    else:
        adjusted_values.append(value)

# --- Color helper functions ---
def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16)/255 for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(x*255) for x in rgb)

def darken_color(hex_color, factor):
    rgb = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = max(0, l * factor)  # darker
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((r, g, b))

# --- Step 1: Compute depth for each node ---
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

# --- Step 2: Identify root nodes and assign base colors ---
roots = [label for label, parent in zip(labels, parents) if parent == ""]

base_colors = ["#90b99d"]
root_color_map = {root: base_colors[i % len(base_colors)] for i, root in enumerate(roots)}

# --- Step 3: Determine color for each label based on root + depth ---
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
    color = darken_color(base_color, 1 - depth * 0.2)  # darker at deeper levels
    colors.append(color)

# --- Create and show Treemap ---
fig = go.Figure(go.Treemap(
    labels=labels,
    parents=parents,
    values=adjusted_values,   # visual sizes
    customdata=values,        # real values as additional info
    marker=dict(colors=colors),
    branchvalues="remainder",
    texttemplate="%{label}<br>%{customdata}",  # label + real value
    textfont=dict(color="white", size=24)
))

# Save graphic as PNG
fig.write_image("8_9_treemap_korpus_getränk.png", width=1200, height=1000, scale=3)

fig.show()
