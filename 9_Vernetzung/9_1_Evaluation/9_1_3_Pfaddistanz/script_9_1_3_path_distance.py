# ================================================================
# Script for distance calculation in SKOS concept hierarchy.
#
# Loads a SKOS hierarchy and calculates minimal and average path
# distances between source concepts and their mapped concepts.
# Saves augmented data and prints summary statistics.
# ================================================================

# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------
from rdflib import Graph, Namespace
import networkx as nx
import pandas as pd
import os
import re

# ------------------------------------------------------------
# Constants / File paths
# ------------------------------------------------------------
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
skos_file = "trinken.ttl"
max_distance = 8

method_dir = "llama_3.3_70b" #"llama_3.1_8b" #"llama_3.3_70b" #"qwen_2.5_32b" #"qwen_2.5_72b" #"deepseek_r1_32b" #"deepseek_r1_70b" #"stringabgleich" #"modernbert"
input_dir = os.path.join(method_dir, "input")
output_dir = os.path.join(method_dir,"output")
input_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".tsv")]

# ------------------------------------------------------------
# Option: Select prediction column
# ------------------------------------------------------------
# Choose which prediction column should be evaluated:
#   "Konzept_gemappt", "Top_1", "Top_3", or "Top_5"
prediction_column = "Konzept_gemappt"

# ------------------------------------------------------------
# Function: label_for
# Purpose: Get German prefLabel of a concept URI from the SKOS graph.
# Returns the label string or falls back to the URI fragment.
# ------------------------------------------------------------
def label_for(graph, concept_uri):
    for _, _, label in graph.triples((concept_uri, SKOS.prefLabel, None)):
        if label.language == "de":
            return str(label)
    for _, _, label in graph.triples((concept_uri, SKOS.prefLabel, None)):
        return str(label)
    return concept_uri.split("#")[-1] if "#" in concept_uri else concept_uri.toPython().split("/")[-1]

# ------------------------------------------------------------
# Function: itemname_for
# Purpose: Extract the local identifier from a concept URI.
# ------------------------------------------------------------
def itemname_for(concept_uri):
    return concept_uri.split("#")[-1] if "#" in concept_uri else concept_uri.toPython().split("/")[-1]

# ------------------------------------------------------------
# Function: load_skos_tree
# Purpose: Load SKOS RDF file and build a directed graph of broader relations.
# Returns: the graph and a mapping of item names to their labels.
# ------------------------------------------------------------
def load_skos_tree(file_path):
    g = Graph()
    g.parse(file_path, format="ttl")
    print(f"SKOS-file loaded: {file_path} — Triple found: {len(g)}")

    tree = nx.DiGraph()
    item2label = {}

    # Add edges from broader relations (parent → child)
    for concept, _, parent in g.triples((None, SKOS.broader, None)):
        child_label = label_for(g, concept)
        parent_label = label_for(g, parent)
        tree.add_edge(parent_label, child_label)

    # Add nodes and build mapping from item name to label
    for s in g.subjects(predicate=SKOS.prefLabel):
        label = label_for(g, s)
        tree.add_node(label)
        item = itemname_for(s)
        item2label[item] = label

    return tree, item2label

# ------------------------------------------------------------
# Function: extract_leaf
# Purpose: Extract the leaf part after the last dot in a concept key.
# ------------------------------------------------------------
def extract_leaf(k):
    return k.split('.')[-1].strip() if '.' in k else k.strip()

# ------------------------------------------------------------
# Function: path_distance
# Purpose: Calculate path distance between two nodes in the tree using
# the lowest common ancestor (LCA) and shortest paths.
# Returns a max distance if no path exists.
# ------------------------------------------------------------
def path_distance(tree, concept1, concept2, max_dist=max_distance):
    try:
        lca = nx.lowest_common_ancestor(tree, concept1, concept2)
        if lca is None:
            return max_dist
        return nx.shortest_path_length(tree, lca, concept1) + nx.shortest_path_length(tree, lca, concept2)
    except Exception:
        return max_dist

# ------------------------------------------------------------
# Function: special_concept_handling
# Purpose: Special case treatment for the concept
# "Trinken.Häufig_lange_trinken".
# ------------------------------------------------------------
def special_concept_handling(concepts):
    if "Trinken.Häufig_lange_trinken" in concepts:
        if len(concepts) == 1:
            return ["Trinken"]
        else:
            return [k for k in concepts if k != "Trinken.Häufig_lange_trinken"]
    return concepts

# ------------------------------------------------------------
# Function: compute_min_distance
# Purpose: Calculate minimal and average distances between source
# and mapped concepts in a data row, also determine minimal edge.
# ------------------------------------------------------------
def compute_min_distance(row, tree, item2label):
    try:
        raw_sources = [k.strip() for k in str(row["Konzept"]).split(";") if k.strip()]
        raw_sources = special_concept_handling(raw_sources)
        sources = [extract_leaf(k) for k in raw_sources]

        targets = [extract_leaf(k) for k in str(row[prediction_column]).split(";") if k.strip()]

        # Handle special "kein_Trinken" cases explicitly
        if "kein_Trinken" in sources and "kein_Trinken" in targets:
            return pd.Series({
                "Distanz_minimal": 0,
                "Distanz_Durchschnitt": 0.0,
                "Kante_min": "kein_Trinken → kein_Trinken"
            })
        elif "kein_Trinken" in sources or "kein_Trinken" in targets:
            return pd.Series({
                "Distanz_minimal": max_distance + 1,
                "Distanz_Durchschnitt": float(max_distance + 1),
                "Kante_min": ""
            })

        sources_labels = [item2label.get(q) for q in sources if item2label.get(q)]
        targets_labels = [item2label.get(z) for z in targets if item2label.get(z)]

        if not sources_labels or not targets_labels:
            return pd.Series({
                "Distanz_minimal": max_distance,
                "Distanz_Durchschnitt": float(max_distance),
                "Kante_min": ""
            })

        min_dist = max_distance
        best_min_edge = ""
        distances = []

        # Compute all pairwise distances, track minimal distance and edge
        for target in targets_labels:
            for source in sources_labels:
                if target not in tree.nodes or source not in tree.nodes:
                    continue
                dist = path_distance(tree, source, target)
                distances.append(dist)
                if dist < min_dist:
                    min_dist = dist
                    best_min_edge = f"{source} → {target}"

        if not distances:
            return pd.Series({
                "Distanz_minimal": max_distance,
                "Distanz_Durchschnitt": float(max_distance),
                "Kante_min": ""
            })

        avg_dist = sum(distances) / len(distances)

        return pd.Series({
            "Distanz_minimal": min_dist,
            "Distanz_Durchschnitt": avg_dist,
            "Kante_min": best_min_edge
        })

    except Exception:
        return pd.Series({
            "Distanz_minimal": max_distance,
            "Distanz_Durchschnitt": float(max_distance),
            "Kante_min": ""
        })
    
# ------------------------------------------------------------
# Function: extract_concept_group
# Purpose: Extract concept group prefix from a concept string.
# Returns "Other" if not in predefined groups.
# ------------------------------------------------------------
def extract_concept_group(concept):
    if pd.isna(concept):
        return "Andere"
    basis = str(concept).split(";")[0].strip()
    group = basis.split(".")[0]
    return group if group in {"Getränk", "Trinken", "Durst", "kein_Trinken"} else "Andere"


# ------------------------------------------------------------
# Main execution block
# ------------------------------------------------------------
if __name__ == "__main__":
    # Load SKOS tree graph and label mapping
    skos_tree, item2label = load_skos_tree(skos_file)

    # Create input/output directories if missing
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Process each input file
    for filename in input_files:
        input_path = os.path.join(input_dir, filename)

        try:
            df = pd.read_csv(input_path, sep="\t")
            print(f"\nProcessing file: {filename} ({len(df)} Zeilen)")

            # Compute distances and minimal edges for each row
            df[["Distanz_minimal", "Distanz_Durchschnitt", "Kante_min"]] = df.apply(
                lambda row: compute_min_distance(row, skos_tree, item2label),
                axis=1
            )
            
            # ------------------------------------------------------------
            # Determine basename depending on the selected method_dir
            # ------------------------------------------------------------
            filename_no_ext = os.path.splitext(filename)[0]

            if method_dir == "stringabgleich":

                patterns = [
                    "4_A_Trinken_OT_", "4_B_Verwandt_OT_", "4_C_Zufall_OT_", "4_A_B_C_gesamt_OT_",
                    "4_A_Trinken_", "4_B_Verwandt_", "4_C_Zufall_", "4_A_B_C_gesamt_"
                ]
                pattern_regex = re.compile(r".*?(" + "|".join(map(re.escape, patterns)) + ")")
                match = pattern_regex.search(filename)
                if match:
                    basename = match.group(0)
                else:
                    basename = filename_no_ext + "_"

            elif any(method_dir.startswith(prefix) for prefix in ["deepseek", "qwen", "llama"]):
                if "_basiskonzepte" in filename_no_ext:
                    basename = filename_no_ext.split("_basiskonzepte")[0] + "_"
                else:
                    basename = filename_no_ext + "_"

            elif method_dir == "modernbert":
                if "_final" in filename_no_ext:
                    basename = filename_no_ext.split("_final")[0] + "_"
                else:
                    basename = filename_no_ext + "_"

            else:
                # Fallback
                basename = filename_no_ext + "_"

            # --- Save results ---
            if method_dir == "modernbert":
                output_path = os.path.join(output_dir, f"{basename}pfaddistanzen_{prediction_column}.tsv")
            else:
                output_path = os.path.join(output_dir, f"{basename}pfaddistanzen.tsv")
                
            # Save augmented DataFrame
            df.to_csv(output_path, sep="\t", index=False)
            print(f"Saved as: {output_path}")

            # statistics
            durchschnitt_min = df["Distanz_minimal"].mean()
            durchschnitt_avg = df["Distanz_Durchschnitt"].mean()
            print(f"∅ minimal path distance: {durchschnitt_min:.2f}")
            print(f"∅ average path distance: {durchschnitt_avg:.2f}")
            
            if "Wortart" in df.columns:
                print("\nAverage distances per part-of-speech:")
                pos = df["Wortart"].dropna().unique()
                for p in sorted(pos):
                    subset = df[df["Wortart"] == p]
                    if len(subset) == 0:
                        continue
                    dist_min = subset["Distanz_minimal"].mean()
                    dist_avg = subset["Distanz_Durchschnitt"].mean()
                    print(f"{p}:∅ min = {dist_min:.2f}, ∅ avg = {dist_avg:.2f}")
            else:
                print("No column 'Wortart' found – no statistics possible.")
                
            df["Konzeptgruppe"] = df["Konzept"].apply(extract_concept_group)
            print("\n Average distances per concept group:")
            groups = df["Konzeptgruppe"].unique()
            for group in sorted(groups):
                subset = df[df["Konzeptgruppe"] == group]
                if len(subset) == 0:
                    continue
                dist_min = subset["Distanz_minimal"].mean()
                dist_avg = subset["Distanz_Durchschnitt"].mean()
                print(f"{group}: ∅ min = {dist_min:.2f}, ∅ avg = {dist_avg:.2f}")
        
            # Write summary to text file
            if method_dir == "modernbert":
                stats_file = os.path.join(output_dir, f"{basename}pfaddistanzen_{prediction_column}.txt")
            else:
                stats_file = os.path.join(output_dir, f"{basename}pfaddistanzen.txt")
            
            with open(stats_file, "w", encoding="utf-8") as f:
                f.write(f"File: {filename}\n")
                f.write(f"Rows: {len(df)}\n")
                f.write(f"∅ minimal path distance: {durchschnitt_min:.2f}\n")
                f.write(f"∅ average path distance: {durchschnitt_avg:.2f}\n\n")

                if "Wortart" in df.columns:
                    f.write("Average distances per part-of-speech:\n")
                    for wortart in sorted(pos):
                        subset = df[df["Wortart"] == wortart]
                        if len(subset) == 0:
                            continue
                        dist_min = subset["Distanz_minimal"].mean()
                        dist_avg = subset["Distanz_Durchschnitt"].mean()
                        f.write(f"{wortart}: ∅ min = {dist_min:.2f}, ∅ avg = {dist_avg:.2f}\n")
                    f.write("\n")
                else:
                    f.write("No column 'Wortart' found – no statistics possible.\n\n")

                f.write("Average distances per concept group:\n")
                for group in sorted(groups):
                    subset = df[df["Konzeptgruppe"] == group]
                    if len(subset) == 0:
                        continue
                    dist_min = subset["Distanz_minimal"].mean()
                    dist_avg = subset["Distanz_Durchschnitt"].mean()
                    f.write(f"{group}: ∅ min = {dist_min:.2f}, ∅ avg = {dist_avg:.2f}\n")

            print(f"Statistics saved as: {stats_file}")


        except FileNotFoundError:
            print(f"File not found: {input_path}")
        except Exception as e:
            print(f"Error processing file {filename}: {e}")




