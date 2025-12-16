# ================================================================
# Script for matching definitions from TSV files with ElsWb-XML entries.
# ================================================================

import os
import csv
import html
import string
import re
from lxml import etree as et

# ================================================================
# Constants and configuration
# ================================================================
input__folder = "input"
output__folder = "output"
xml_folder = os.path.join(input__folder, "ElsWb_Daten")

os.makedirs(output__folder, exist_ok=True)

# TEI namespace
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# ================================================================
# Function: clean_definition
# Purpose: Removes trailing punctuation and whitespace from text
# ================================================================
def clean_definition(text):
    """
    Cleans the definition text by removing trailing punctuation and whitespace.
    """
    return text.rstrip(string.punctuation + " ").strip()

# ================================================================
# Function: extract_wortart_for_form
# Purpose: Extracts part of speech from a TEI form element
# ================================================================
def extract_wortart_for_form(form_elem):
    """
    Extracts the part of speech from the form element following the given element.
    """
    allowed_pos = {"Adj.", "Adv.", "f.", "m.", "n.", "Pl.", "Demin."}
    next_elem = form_elem.getnext()
    while next_elem is not None:
        if next_elem.tag.endswith("form") and next_elem.get("type") == "main":
            hi_elems = next_elem.xpath(".//tei:hi[@rend='italics']", namespaces=NS)
            for hi_elem in reversed(hi_elems):
                text = "".join(hi_elem.itertext()).strip()
                if text in allowed_pos:
                    return text
            break
        next_elem = next_elem.getnext()
    return ""

# ================================================================
# Function: process_file
# Purpose: Processes TSV and XML data and outputs matched entries
# ================================================================
def process_file(tsv_filename, output_filename):
    """
    Processes a TSV file and matches its definitions with XML entries.
    Outputs a new TSV with aligned data.
    """
    print(f"→ Processing: {os.path.basename(tsv_filename)}")

    # ------------------------------------------------------------
    # Step 1: Read the TSV definitions and build a dictionary
    # ------------------------------------------------------------
    definition_mapping = {}
    with open(tsv_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            definition = clean_definition(row["Definition"].strip()).lower()
            concept = row["Konzept"].strip()
            definition_mapping[definition] = concept

    # ------------------------------------------------------------
    # Step 2: Open output file for writing matched results
    # ------------------------------------------------------------
    with open(output_filename, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["xml:id", "Lemma", "Wortart", "Level", "Definition", "Konzept"])

        # --------------------------------------------------------
        # Step 3: Iterate through each XML file in the input folder
        # --------------------------------------------------------
        for filename in os.listdir(xml_folder):
            if not filename.lower().endswith(".xml"):
                continue

            filepath = os.path.join(xml_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                xml_text = f.read()

            # Preprocess XML text (resolve main non-standard entities)
            xml_text = xml_text.replace("&supercharn;", "n")
            xml_text = xml_text.replace("&supercharh;", "h")
            xml_text = xml_text.replace("&supercharg;", "g")
            xml_text = xml_text.replace("&superchare;", "e")
            xml_text = xml_text.replace("&etrema;", "ë")
            xml_text = html.unescape(xml_text)

            # Parse XML content
            parser = et.XMLParser(resolve_entities=False, load_dtd=False, recover=True)
            root = et.fromstring(xml_text.encode("utf-8"), parser)


            # ----------------------------------------------------
            # Step 4: Process <entry> elements inside XML structure
            # ----------------------------------------------------
            for entry in root.xpath(".//tei:entry", namespaces=NS):
                entry_id = entry.get("{http://www.w3.org/XML/1998/namespace}id", "")
                lw_elem = entry.find(".//tei:form[@type='leitwort']", namespaces=NS)
                leitwort = "".join(lw_elem.itertext()).strip() if lw_elem is not None else ""

                # Extract lemma text (with fallback for <abbr>)
                def extract_lemma_text(lemma_elem):
                    abbr = lemma_elem.find(".//tei:abbr", namespaces=NS)
                    if abbr is not None:
                        return "".join(abbr.itertext()).strip()
                    return "".join(lemma_elem.itertext()).strip()

                # Attempt to match a single definition to a TSV concept
                # If matched, find the most appropriate lemma and write output
                def check_and_write(def_text, def_elem, label_text=""):
                    def_text_clean = clean_definition(def_text)
                    def_text_lc = def_text_clean.lower()
                    matched_concept = ""
                    best_score = None
                    best_match = ""

                    # Try to match the cleaned definition with entries from the TSV
                    for tsv_def, concept in definition_mapping.items():
                        tokens = tsv_def.split()
                        if len(tokens) == 1:
                            def_tokens = def_text_lc.split()
                            if len(def_tokens) == 1:
                                if tsv_def in def_text_lc:
                                    matched_concept = concept
                                    best_match = tsv_def
                                    best_score = 100
                                    break
                            else:
                                pattern = re.compile(r'\b' + re.escape(tsv_def) + r'\b')
                                if pattern.search(def_text_lc):
                                    matched_concept = concept
                                    best_match = tsv_def
                                    best_score = 100
                                    break
                    
                    # If match found, extract closest lemma and write to output
                    if matched_concept:
                        best_lemma = leitwort
                        best_lemma_id = entry_id
                        best_pos = ""
                        min_distance = float("inf")
                        def_line = getattr(def_elem, "sourceline", None)

                        # Try to locate lemma element that appears before the definition
                        lemma_elems = entry.xpath(".//tei:form[@type='lemma']", namespaces=NS)
                        if not lemma_elems:
                            lemma_elems = entry.xpath(".//tei:form[@type='leitwort']", namespaces=NS)

                        for lemma_elem in lemma_elems:
                            lemma_line = getattr(lemma_elem, "sourceline", None)
                            if lemma_line and def_line and lemma_line < def_line:
                                distance = def_line - lemma_line
                                if distance < min_distance:
                                    min_distance = distance
                                    best_lemma = extract_lemma_text(lemma_elem)
                                    best_lemma_id = lemma_elem.get("{http://www.w3.org/XML/1998/namespace}id", entry_id)
                                    best_pos = extract_wortart_for_form(lemma_elem)

                        writer.writerow([
                            best_lemma_id,
                            best_lemma,
                            best_pos,
                            label_text,
                            def_text_clean,
                            matched_concept
                        ])


                # ------------------------------------------------
                # Step 5: Match <def> elements (main definitions)
                # ------------------------------------------------
                for def_elem in entry.xpath(".//tei:sense//tei:def", namespaces=NS):
                    def_text = "".join(def_elem.itertext()).strip()
                    check_and_write(def_text, def_elem)

                # ------------------------------------------------
                # Step 6: Match <lbl> + italic <hi> pairs (labeled glosses)
                # ------------------------------------------------
                for lbl in entry.xpath(".//tei:sense//tei:lbl", namespaces=NS):
                    next_elem = lbl.getnext()
                    if next_elem is not None and next_elem.tag.endswith("hi") and next_elem.get("rend") == "italics":
                        hi_text = "".join(next_elem.itertext()).strip()
                        hi_text = clean_definition(hi_text)
                        label_text = "".join(lbl.itertext()).strip()
                        check_and_write(hi_text, next_elem, label_text)

        print(f"Done: '{os.path.basename(output_filename)}' has been saved.\n")

# ================================================================
# Main execution
# ================================================================
process_file(
    os.path.join(input__folder, "definitionen_A.tsv"),
    os.path.join(output__folder, "abgleich_elswb_A.tsv")
)

process_file(
    os.path.join(input__folder, "definitionen_B.tsv"),
    os.path.join(output__folder, "abgleich_elswb_B.tsv")
)
