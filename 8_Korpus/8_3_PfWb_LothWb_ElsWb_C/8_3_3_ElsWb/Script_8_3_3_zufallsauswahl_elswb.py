# ================================================================
# Script for extracting random <entry> elements from ElsWb-TEI-XML files
# and exporting selected data into a TSV file
# ================================================================

import os
import random
import csv
import html
import re
import string
from lxml import etree as et

# ================================================================
# Constants and configuration
# ================================================================
input_folder = "input/ElsWb_Daten"
output_file = "output/ElsWb_C_Zufall.tsv"
num_entries = 400

# TEI namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}

# "forbidden" pos; selection should only contain nouns, verbs and adjectives
forbidden_pos = {
    "Adv.", "Conj.", "Interj.", "Pron.", "Präp.", "Zahlwort"
}

# ================================================================
# Function: extract_pos_from_form
# Purpose: Extracts part of speech from form element
# ================================================================
def extract_pos_from_form(form_elem):
    """
    Extracts a grammatical category (Wortart) from the nearest
    following <form type="main"> element.
    """
    pos_list = {
        "Adj.", "Adv.", "Conj.", "Demin.", "Interj.",
        "f.", "m.", "n.", "Pl.", "Pron.", "Part.",
        "Präp.", "Zahlwort"
    }

    next_elem = form_elem.getnext()
    while next_elem is not None:
        if next_elem.tag.endswith("form") and next_elem.get("type") == "main":
            hi_elems = next_elem.xpath(".//tei:hi[@rend='italics']", namespaces=ns)
            for hi_elem in reversed(hi_elems):
                text = "".join(hi_elem.itertext()).strip()
                if text in pos_list:
                    return text
            break
        next_elem = next_elem.getnext()

    return ""

# ================================================================
# Function: clean_text
# Purpose: Cleans text and replaces TEI entity placeholders
# ================================================================
def clean_text(text):
    """
    Replaces custom XML entities and unescapes HTML.
    """
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
# Purpose: Extracts lemma, POS, level, and definition from <entry>
# ================================================================
def extract_entry_data(entry):
    """
    Extracts relevant fields from a <tei:entry> element.
    """
    xml_id = entry.get("{http://www.w3.org/XML/1998/namespace}id", "")

    # ------------------------------------------------------------
    # extract lemma
    # ------------------------------------------------------------
    lemma = ""
    lemma_elem = entry.find(".//tei:form[@type='leitwort']", namespaces=ns)
    if lemma_elem is not None:
        hi = lemma_elem.find(".//tei:hi[@rend='bold']", namespaces=ns)
        if hi is not None:
            lemma = clean_text("".join(hi.itertext()))

    # ------------------------------------------------------------
    # search for deepest <sense> element 
    # ------------------------------------------------------------
    sense = entry.find(".//tei:sense", namespaces=ns)
    while sense is not None and sense.find("tei:sense", namespaces=ns) is not None:
        sense = sense.find("tei:sense", namespaces=ns)

    definition = ""
    level = ""

    if sense is not None:
        # get level 
        lbl_elem = sense.find(".//tei:lbl", namespaces=ns)
        if lbl_elem is not None and lbl_elem.text:
            level = clean_text(lbl_elem.text)

        # get definition
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

    # ------------------------------------------------------------
    # part of speech
    # ------------------------------------------------------------
    pos = ""
    if lemma_elem is not None:
        pos = extract_pos_from_form(lemma_elem)

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
# Purpose: Parses XML files, extracts and filters entries, writes TSV
# ================================================================
def main(folder, output_tsv, count=400):
    """
    Parses all XML files in the input folder, filters entries
    based on part-of-speech, and exports the selected fields as TSV.
    """
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
            print(f"Error in in {datei}: {e}")
            continue

        entries = root.xpath(".//tei:entry", namespaces=ns)
        all_entries.extend(entries)

    print(f"{len(all_entries)} <entry> elements found.")

    if not all_entries:
        print("No <entry> elements found. Check paths and namespaces.")
        return

    # ------------------------------------------------------------
    # Filter entries by allowed part of speech
    # ------------------------------------------------------------
    filtered_data = []
    for entry in all_entries:
        data = extract_entry_data(entry)
        if data["Wortart"] not in forbidden_pos:
            filtered_data.append(data)

    print(f"{len(filtered_data)} entries with allowed part of speech.")

    if not filtered_data:
        print("No entries with allowed part of speech found.")
        return

    # Select random sample
    random_data = random.sample(filtered_data, min(count, len(filtered_data)))


    # Write TSV
    fieldnames = ["xml:id", "Lemma", "Wortart", "Level", "Definition", "Konzept"]
    with open(output_tsv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(random_data)

    print(f"{len(random_data)} entries saved in {output_tsv}")


# ================================================================
# Main execution
# ================================================================
if __name__ == "__main__":
    main(input_folder, output_file, count=num_entries)
