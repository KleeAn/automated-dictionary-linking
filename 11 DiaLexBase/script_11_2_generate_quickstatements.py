# ================================================================
# This script prepares statements about lemmas as quick statements
# for automated import into a Wikibase based on a TSV file.

# - reads a TSV file of lexical entries
# - processes each lemma and its senses, generates structured
#   QuickStatement lines for variants, dictionary references,
#   IDs, definitions and concepts,
# - removes duplicates
# - writes the cleaned result to a TXT file.
# ================================================================

import os
import csv

# ==========================
# Input file
# ==========================
input_file = "A_Trinken_mapping_gesamt.tsv" 
base_name, _ = os.path.splitext(input_file)
output_file = f"{base_name}.txt"

# ==========================
# Variables for output
# ==========================
qs_lines = []  # list of all QS lines (keeps original order)
seen = set()   # set for duplicate checking
last_lnumber = None
sense_counter = 0

# ==========================
# Processing the TSV
# ==========================
with open(input_file, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile, delimiter="\t")

    for row in reader:

        # --------------------------
        # TSV columns
        # --------------------------
        lnumber = row.get("Lnummer", "").strip()
        variants = row.get("Varianten", "").strip()
        dictionary = row.get("Wörterbuch", "").strip()
        xml_id = row.get("xml:id", "").strip()
        url = row.get("url", "").strip()
        definition = row.get("Definition", "").strip()
        concepts = row.get("Konzept", "").strip()
        stringmatching = row.get("stringmatching", "").strip()
        modernGBERT = row.get("ModernGBERT", "").strip()
        llama = row.get("Llama", "").strip()

        if not lnumber:
            continue

        # --------------------------
        # Check if new L-number or same as previous
        # --------------------------
        is_new_lnumber = (lnumber != last_lnumber)
        if is_new_lnumber:
            sense_counter = 1   # new L-number → S1
        else:
            sense_counter += 1  # same L-number → next sense S2, S3, ...

        # --------------------------
        # Steps 1–3 (only for a new L-number)
        # --------------------------
        if is_new_lnumber:

            # lemma variants (P7)
            if variants:
                for v in [x.strip() for x in variants.split(",") if x.strip()]:
                    line = f'{lnumber}\tP7\t"{v}"'
                    if line not in seen:
                        seen.add(line)
                        qs_lines.append(line)

            # dictionary (P5)
            if dictionary:
                line = f"{lnumber}\tP5\t{dictionary}"
                if line not in seen:
                    seen.add(line)
                    qs_lines.append(line)

            # xml:id → P15/P16/P17 + URL (P3)
            if xml_id:
                first = xml_id[0].upper()
                prop = None
                if first == "P":
                    prop = "P15"
                elif first == "E":
                    prop = "P16"
                elif first == "L":
                    prop = "P17"

                if prop:
                    value = xml_id[1:]
                    if url:
                        line = f'{lnumber}\t{prop}\t"{value}"\tS3\t"{url}"'
                    else:
                        line = f'{lnumber}\t{prop}\t"{value}"'
                    if line not in seen:
                        seen.add(line)
                        qs_lines.append(line)

        # --------------------------
        # Step 4: Sense / Definition
        # --------------------------
        if definition:
            s_id = f"{lnumber}-S{sense_counter}"
            line = f'{s_id}\tP8\t"{definition}"'
            if url:
                line += f'\tS6\t"{url}"'
            if line not in seen:
                seen.add(line)
                qs_lines.append(line)

            # --------------------------
            # # Step 5: Gold standard concepts (P9)
            # --------------------------
            if concepts:
                for k in [x.strip() for x in concepts.split(";") if x.strip()]:
                    line = f'{s_id}\tP9\t{k}'
                    if line not in seen:
                        seen.add(line)
                        qs_lines.append(line)

            # --------------------------
            # Steps 6–8: Concepts mapped by string match, ModernGBERT, Llama
            # --------------------------
            feld_mapping = {
                "stringmatching": "Q16",
                "ModernGBERT": "Q17",
                "Llama": "Q18"
            }
            for feld, q_code in feld_mapping.items():
                inhalt = row.get(feld, "").strip()
                if inhalt:
                    for teil in [x.strip() for x in inhalt.split(";") if x.strip()]:
                        line = f'{s_id}\tP10\t{teil}\tP11\t{q_code}'
                        if line not in seen:
                            seen.add(line)
                            qs_lines.append(line)

        # --------------------------
        # Post-processing: remember last L-number
        # --------------------------
        last_lnumber = lnumber

# ==========================
# Write output to TXT
# ==========================
with open(output_file, "w", encoding="utf-8") as outfile:
    for line in qs_lines:
        outfile.write(line + "\n")
