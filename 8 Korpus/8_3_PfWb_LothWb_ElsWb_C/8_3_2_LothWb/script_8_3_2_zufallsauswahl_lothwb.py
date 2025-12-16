# ================================================================
# Script for extracting random <entry> elements from LothWb-TEI-XML files
# and exporting selected data into a TSV file
# ================================================================

import os
import random
import csv
import html
import re
import requests
from lxml import etree as et

# ================================================================
# Constants and configuration
# ================================================================
input_folder = "input/LothWb_Daten"
output_file = "output/LothWb_C_Zufall.tsv"
num_entries = 300

# TEI namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}

# Cache für API-results
wortart_cache = {}

# ================================================================
# Function: get_wortart_from_api
# Purpose: Retrieves part of speech from Woerterbuchnetz API
# ================================================================
def get_wortart_from_api(lemma):
    if not lemma:
        return ""

    if lemma in wortart_cache:
        return wortart_cache[lemma]

    url = f"https://api.woerterbuchnetz.de/open-api/dictionaries/LothWB/lemmata/{lemma}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result_set = data.get("result_set", [])
            if result_set:
                pos = result_set[0].get("gram", "")
                wortart_cache[lemma] = pos
                return pos
    except Exception as e:
        print(f"⚠️ API-Fehler bei Lemma '{lemma}': {e}")

    wortart_cache[lemma] = ""
    return ""

# ================================================================
# Function: clean_text
# Purpose: Cleans text and replaces TEI entity placeholders
# ================================================================
def clean_text(text):
    if text is None:
        return ""

    replacements = {
        "&supercharn;": "n",
        "&supercharh;": "h",
        "&supercharg;": "g",
        "&superchare;": "e",
        "&etrema;": "ë",
    }

    for key, val in replacements.items():
        text = text.replace(key, val)

    text = html.unescape(text)

    while text and text[-1] in {".", ",", ";", ":", "!", "?", "…"}:
        text = text[:-1]

    return text.strip()

# ================================================================
# Function: remove_trailing_punctuation
# Purpose: Removes trailing punctuation and whitespace
# ================================================================
def remove_trailing_punctuation(text):
    return re.sub(r"[.,;:!?…\s]+$", "", text.strip())

# ================================================================
# Function: extract_entry_data
# Purpose: Extracts lemma, level, and definition from <entry>
# ================================================================
def extract_entry_data(entry):
    xml_id = entry.get("{http://www.w3.org/XML/1998/namespace}id", "")

    # extract lemma
    lemma = ""
    lemma_elem = entry.find(".//tei:form[@type='leitwort']", namespaces=ns)
    if lemma_elem is not None:
        hi = lemma_elem.find(".//tei:hi[@rend='bold']", namespaces=ns)
        if hi is not None:
            lemma = clean_text("".join(hi.itertext()))

    # search for deepest <sense> element
    sense = entry.find(".//tei:sense", namespaces=ns)
    while sense is not None and sense.find("tei:sense", namespaces=ns) is not None:
        sense = sense.find("tei:sense", namespaces=ns)

    definition = ""
    level = ""

    if sense is not None:
        lbl_elem = sense.find(".//tei:lbl", namespaces=ns)
        if lbl_elem is not None and lbl_elem.text:
            level = clean_text(lbl_elem.text)

        def_elem = sense.find("tei:def", namespaces=ns)
        if def_elem is not None:
            hi = def_elem.find(".//tei:hi[@rend='italics']", namespaces=ns)
            if hi is not None and hi.text:
                definition = clean_text(hi.text)
            else:
                definition = clean_text("".join(def_elem.itertext()))
        else:
            hi = sense.find(".//tei:hi[@rend='italics']", namespaces=ns)
            if hi is not None and hi.text:
                definition = clean_text(hi.text)

        definition = remove_trailing_punctuation(definition)

    pos = ""

    return {
        "xml:id": xml_id,
        "Lemma": lemma,
        "Wortart": pos,
        "Level": level,
        "Definition": definition,
        "Konzept": "kein_Trinken"
    }

# ================================================================
# Function: main
# Purpose: Parses XML files, extracts entries, does random sampling,
#          calls API for POS only on sampled entries, filters forbidden POS,
#          writes TSV
# ================================================================
def main(folder, output_tsv, count=300):
    all_entries = []

    for filename in os.listdir(folder):
        if not filename.lower().endswith(".xml"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            xml_text = f.read()

        # replace special characters
        replacements = {
            "&supercharn;": "n",
            "&supercharh;": "h",
            "&supercharg;": "g",
            "&superchare;": "e",
            "&etrema;": "ë",
        }
        for key, val in replacements.items():
            xml_text = xml_text.replace(key, val)

        xml_text = html.unescape(xml_text)

        parser = et.XMLParser(resolve_entities=False, load_dtd=False, recover=True)
        try:
            root = et.fromstring(xml_text.encode("utf-8"), parser)
        except et.XMLSyntaxError as e:
            print(f"Error in '{filename}': {e}")
            continue

        entries = root.xpath(".//tei:entry", namespaces=ns)
        all_entries.extend(entries)

    print(f"{len(all_entries)} <entry>-elements found.")

    if not all_entries:
        print("No <entry>-elements found.")
        return

    # extract all data (except POS)
    extracted_data = [extract_entry_data(entry) for entry in all_entries]
    print(f"{len(extracted_data)} entries extracted.")

    # random sample
    random_data = random.sample(extracted_data, min(count, len(extracted_data)))

    # API request only for the random selection
    for entry_data in random_data:
        lemma = entry_data["Lemma"]
        entry_data["Wortart"] = get_wortart_from_api(lemma)

    # POS to be excluded
    forbidden_pos = {
        "adv.",
        "conj.",
        "präp.",
        "präp. m."
    }

    # Filter POS
    filtered_random_data = [
        entry for entry in random_data
        if entry["Wortart"] not in forbidden_pos
    ]

    # Write TSV
    fieldnames = ["xml:id", "Lemma", "Wortart", "Level", "Definition", "Konzept"]
    with open(output_tsv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(filtered_random_data)

    print(f"{len(filtered_random_data)} entries saved in '{output_tsv}'")

# ================================================================
# Main execution
# ================================================================
if __name__ == "__main__":
    main(input_folder, output_file, count=num_entries)
