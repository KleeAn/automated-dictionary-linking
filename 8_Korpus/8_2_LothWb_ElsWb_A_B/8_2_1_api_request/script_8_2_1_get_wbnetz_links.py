# ================================================================
# Script for querying the Woerterbuchnetz API and
# extracting the linked LothWB and ElsWB entries.
# ================================================================

import requests
import csv
import os

# ================================================================
# Function: api_query
# Purpose:  Loads PfWB srcids and concepts, queries the API, and writes results
# ================================================================
def api_query(input_tsv, output_suffix):
    """
    Processes a TSV file to extract srcids and concepts, makes API calls, 
    and writes related entries to output TSV files for LothWB and ElsWB dictionaries.
    """

    # ------------------------------------------------------------
    # 1. Load srcids and concept values from input TSV
    # ------------------------------------------------------------
    input_path = os.path.join("input", input_tsv)
    srcid_to_konzept = {}

    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        for row in reader:
            srcid = row.get("xml:id")
            konzept = row.get("Konzept", "").strip()
            if srcid:
                srcid_clean = srcid.lstrip("P")
                srcid_to_konzept[srcid_clean] = konzept

    srcids = list(srcid_to_konzept.keys())

    target_sigla = {"LothWB", "ElsWB"}
    entry_counter = {sigle: 0 for sigle in target_sigla}
    results = {sigle: [] for sigle in target_sigla}

    # ------------------------------------------------------------
    # 2. Query API for each srcid
    # ------------------------------------------------------------
    for srcid in srcids:
        url = f"https://api.woerterbuchnetz.de/dictionaries/PfWB/links-from/{srcid}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            for entry in data:
                tgt_sigle = entry["tgtsigle"]
                if tgt_sigle in target_sigla:
                    srclemma_raw = entry.get("srclemma", "")
                    tgtlemma_raw = entry.get("tgtlemma") or ""

                    # Clean srclemma
                    srclemma_clean = srclemma_raw.split("@")[0].strip()

                    # Process tgtlemma
                    tgtlemma_parts = [part.strip() for part in tgtlemma_raw.split("@") if part.strip()]
                    tgtlemma_clean_parts = [tgtlemma_parts[0]]
                    tgtlemma_clean_parts += [part.lstrip(",") for part in tgtlemma_parts[1:] if part.startswith(",")]
                    tgtlemma_clean = ", ".join(tgtlemma_clean_parts)

                    # tgtgram only for LothWB
                    tgtgram = ""
                    if tgt_sigle == "LothWB":
                        tgtgram_candidates = [part for part in tgtlemma_parts[1:] if not part.startswith(",")]
                        tgtgram = tgtgram_candidates[0] if tgtgram_candidates else ""

                    tgtid = entry.get("tgtid", "")
                    # Prefix srcid with 'L' or 'E' depending on target dictionary
                    prefixed_tgtid = ("L" if tgt_sigle == "LothWB" else "E") + tgtid
                    # Prefix srcid with 'P'
                    prefixed_srcid = "P" + srcid
                    concept = srcid_to_konzept.get(srcid, "")

                    row = [prefixed_srcid, srclemma_clean, prefixed_tgtid, tgtlemma_clean, tgtgram, concept]
                    results[tgt_sigle].append(row)
                    entry_counter[tgt_sigle] += 1
        else:
            print(f"Error for srcid {srcid}: HTTP {response.status_code}")

    # ------------------------------------------------------------
    # 3. Write results to output files
    # ------------------------------------------------------------
    if not os.path.exists("output"):
        os.makedirs("output")

    for sigle, rows in results.items():
        if rows:
            output_file = os.path.join("output", f"{sigle}_{output_suffix}_API.tsv")
            with open(output_file, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile, delimiter="\t")
                writer.writerow(["srcid", "srclemma", "tgtid", "tgtlemma", "tgtgram", "concept_PfWb"])
                writer.writerows(rows)

    # ------------------------------------------------------------
    # 4. Print summary
    # ------------------------------------------------------------
    print(f"\n Summary for {input_tsv}:")
    for sigle in target_sigla:
        count = entry_counter[sigle]
        if count > 0:
            print(f"{sigle}_{output_suffix}_API.tsv created with {count} entries.")
        else:
            print(f"{sigle}_{output_suffix}_API.tsv contains no entries.")


# ================================================================
# Main execution
# ================================================================
if __name__ == "__main__":
    api_query("PfWb_A_Trinken.tsv", "A")
    api_query("PfWb_B_Verwandt.tsv", "B")
