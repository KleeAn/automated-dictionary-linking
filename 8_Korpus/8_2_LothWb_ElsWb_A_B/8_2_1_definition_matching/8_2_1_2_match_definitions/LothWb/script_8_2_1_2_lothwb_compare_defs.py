# ================================================================
# Script for matching definitions from TSV files with LothWb-XML entries.
# ================================================================

import os
import csv
import html
import string
import re
import requests
from lxml import etree as et

# ================================================================
# Constants and configuration
# ================================================================
input__folder = "input"
output__folder = "output"
xml_folder = os.path.join(input__folder, "LothWb_Daten")

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
# Function: get_wortart_from_api
# Purpose: Retrieves part of speech via Wörterbuchnetz API
# ================================================================
def get_wortart_from_api(lemma):
    """
    Queries the Woerterbuchnetz API to get part of speech for a given lemma.
    """
    url = f"https://api.woerterbuchnetz.de/open-api/dictionaries/LothWB/lemmata/{lemma}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result_set = data.get("result_set", [])
            if result_set:
                return result_set[0].get("gram", "")
    except Exception as e:
        print(f"Error for '{lemma}': {e}")
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
    # Step 1: Read TSV and build dictionary of definitions → concepts
    # ------------------------------------------------------------
    definition_mapping = {}
    with open(tsv_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            definition = clean_definition(row["Definition"].strip()).lower()
            concept = row["Konzept"].strip()
            definition_mapping[definition] = concept

    # Cache for POS lookup
    wortart_cache = {}

    # ------------------------------------------------------------
    # Step 2: Prepare output TSV
    # ------------------------------------------------------------
    with open(output_filename, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["xml:id", "Lemma", "Wortart", "Level", "Definition", "Konzept"])

        # --------------------------------------------------------
        # Step 3: Iterate through all XML files
        # --------------------------------------------------------
        for filename in os.listdir(xml_folder):
            if not filename.lower().endswith(".xml"):
                continue

            filepath = os.path.join(xml_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                xml_text = f.read()

            # Clean up XML text
            xml_text = xml_text.replace("&supercharn;", "n")
            xml_text = html.unescape(xml_text)

            # Parse XML
            parser = et.XMLParser(resolve_entities=False, load_dtd=False, recover=True)
            root = et.fromstring(xml_text.encode("utf-8"), parser)

            # ----------------------------------------------------
            # Step 4: Process <entry> elements
            # ----------------------------------------------------
            for entry in root.xpath(".//tei:entry", namespaces=NS):
                entry_id = entry.get("{http://www.w3.org/XML/1998/namespace}id", "")
                lw_elem = entry.find(".//tei:form[@type='leitwort']", namespaces=NS)
                leitwort = "".join(lw_elem.itertext()).strip() if lw_elem is not None else ""

                # Helper: extract lemma
                def extract_lemma_text(lemma_elem):
                    abbr = lemma_elem.find(".//tei:abbr", namespaces=NS)
                    if abbr is not None:
                        return "".join(abbr.itertext()).strip()
                    return "".join(lemma_elem.itertext()).strip()

                # Helper: core match/write logic
                def check_and_write(def_text, def_elem, label_text=""):
                    def_text_clean = clean_definition(def_text)
                    def_text_lc = def_text_clean.lower()
                    matched_concept = ""

                    # Try to match definition
                    for tsv_def, concept in definition_mapping.items():
                        tokens = tsv_def.split()
                        if len(tokens) == 1:
                            def_tokens = def_text_lc.split()
                            if len(def_tokens) == 1:
                                if tsv_def in def_text_lc:
                                    matched_concept = concept
                                    break
                            else:
                                pattern = re.compile(r'\b' + re.escape(tsv_def) + r'\b')
                                if pattern.search(def_text_lc):
                                    matched_concept = concept
                                    break

                    # If matched: find closest lemma, query POS, write row
                    if matched_concept:
                        best_lemma = leitwort
                        best_lemma_id = entry_id
                        min_distance = float("inf")
                        def_line = getattr(def_elem, "sourceline", None)

                        # Try to find best lemma before definition
                        for lemma_elem in entry.xpath(".//tei:form[@type='lemma']", namespaces=NS):
                            lemma_line = getattr(lemma_elem, "sourceline", None)
                            if lemma_line and def_line and lemma_line < def_line:
                                distance = def_line - lemma_line
                                if distance < min_distance:
                                    min_distance = distance
                                    best_lemma = extract_lemma_text(lemma_elem)
                                    best_lemma_id = lemma_elem.get("{http://www.w3.org/XML/1998/namespace}id", entry_id)

                        # Get POS from cache or API
                        if best_lemma not in wortart_cache:
                            wortart_cache[best_lemma] = get_wortart_from_api(best_lemma)
                        pos = wortart_cache.get(best_lemma, "")

                        writer.writerow([
                            best_lemma_id,
                            best_lemma,
                            pos,
                            label_text,
                            def_text_clean,
                            matched_concept
                        ])

                # ------------------------------------------------
                # Step 5: Match <def> elements
                # ------------------------------------------------
                for def_elem in entry.xpath(".//tei:sense//tei:def", namespaces=NS):
                    def_text = "".join(def_elem.itertext()).strip()
                    check_and_write(def_text, def_elem)

                # ------------------------------------------------
                # Step 6: Match <lbl> + italic <hi> pairs
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
    os.path.join(input__folder, "definitionen_A_final.tsv"),
    os.path.join(output__folder, "abgleich_lothwb_A.tsv")
)

process_file(
    os.path.join(input__folder, "definitionen_B_final.tsv"),
    os.path.join(output__folder, "abgleich_lothwb_B.tsv")
)
