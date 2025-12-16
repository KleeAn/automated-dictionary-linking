# ================================================================
# Script for running the pipeline to build a corpus based on
# dictionary entries from Pfälzisches Wörterbuch.
# ================================================================

import script_8_1_01_txt2tsv
import script_8_1_02_xml_mapping
import script_8_1_03_normalize_pos

prefix = "Sachgruppe_5920_dummy" # Sachgruppe_5920, _5925, _7455, _7470

def main(prefix):
    print("Script txt2tsv.py (TXT -> TSV)")
    script_8_1_01_txt2tsv.main(prefix)
    
    print("Script xml_mapping.py (Matching to XML data)")
    script_8_1_02_xml_mapping.main(prefix)
    
    print("Script normalize_pos.py (Normalize POS)")
    script_8_1_03_normalize_pos.main(prefix)
    
    print("All scripts successfully executed!")

if __name__ == '__main__':
    main(prefix)

