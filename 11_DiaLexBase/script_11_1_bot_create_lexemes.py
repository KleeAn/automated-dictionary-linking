# ================================================================
# This script reads lexical data from a TSV file and automatically creates new lexemes
# in a Wikibase instance using the Wikidata Integrator.
#
# - logs in via API
# - obtains a CSRF token
# - constructs lexeme JSON structures from the TSV fields
# - submits them to the Wikibase API,
# -  reports the IDs of newly created lexemes
# ================================================================

import json
import requests
import csv
from wikidataintegrator import wdi_login

### ---------------------------------------------------------
### 1) Instance configuration
### ---------------------------------------------------------

wikibase_url = "https://dialexbase.wikibase.cloud"
api_url = f"{wikibase_url}/w/api.php"

# replace with your username and password
bot_user = "XXX" 
bot_password = "XXX"


### ---------------------------------------------------------
### 2) Login via WDI
### ---------------------------------------------------------

login = wdi_login.WDLogin(user=bot_user, pwd=bot_password, mediawiki_api_url=api_url)
session = login.get_session()

# Fetch CSRF Token
token_response = session.get(api_url, params={
    "action": "query",
    "meta": "tokens",
    "format": "json"
}).json()

csrf_token = token_response["query"]["tokens"]["csrftoken"]

### ---------------------------------------------------------
### 3) Read the TSV file
### ---------------------------------------------------------

tsv_file = "A_Trinken_mappung_gesamt.tsv" 

with open(tsv_file, encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        lemma = row["Lemma"]
        language = row["Sprache"]
        word_class = row["Wortart"]

        lang_qid = row["Sprache"]  
        lex_cat_qid = row["Wortart"]  

        if not lang_qid or not lex_cat_qid:
            print(f"Error: No lexical category QID found for lemma '{lemma}' gefunden")
            continue

        # Construct lexeme data object
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {
                "de": {           # "de" is set as language code
                    "language": "de",
                    "value": lemma
                }
            },
            "language": lang_qid,    # Language QID from TSV
            "lexicalCategory": lex_cat_qid
        }

        lexeme_data_str = json.dumps(lexeme_data)

        # API request parameters
        params = {
            "action": "wbeditentity",
            "new": "lexeme",
            "format": "json",
            "token": csrf_token,
            "data": lexeme_data_str
        }

        response = session.post(api_url, data=params)
        result = response.json()

        if "entity" in result:
            print(f"New lexeme '{lemma}':", result["entity"]["id"])
        else:
            print(f"Error for lexeme '{lemma}':", result)
