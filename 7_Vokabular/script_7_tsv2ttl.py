'''
Script for converting a concept vocabulary into a SKOS vocabulary in Turtle Syntax.

This script is designed to process a TSV (Tab-Separated Values) file containing concepts
and terms related to the semantic field of "Drinking," along with mappings to Wikidata.
It loads a pre-existing file with defined prefixes and concepts, and appends the new
vocabulary entries in SKOS syntax according to the definition in Chapter 7.5.
'''

# === Imports ===

import csv
import pandas as pd
import re

# === Files ===

prefixes_concepts_file = "trinken_prefixes_concepts.ttl"
vocab_file = "trinken_vokabular.tsv"   
output_file = "trinken_vokabular.ttl"  

# === Functions ===

def read_tsv_to_dataframe(input_file):
    '''Reads TSV file and creates a dataframe.'''
    df = pd.read_csv(input_file, delimiter='\t', encoding='utf-8')
    return df

def read_ttl(ttl_file):
    '''Reads Turtle file and return string.'''
    with open(ttl_file, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def normalize_identifier(value):
    """
    Normalizes a string for use as an identifier:
    removes spaces and converts the string to lowercase.
    """
    value = value.strip().lower()
    value = re.sub(r'\s+', '_', value)
    return value

def transform_data(df):
    '''Converts the entries from the DataFrame into triples using the SKOS syntax and returns a string.'''
    ttl_string = ""
    for index, row in df.iterrows():
        konzept = row['Konzept']  
        begriff = row['Begriff']  
        varianten = row['Begriffsvarianten']  
        referenz = row['Referenz'] 
        wikidata_exact = row['Wikidata_exact'] 
        wikidata_close = row['Wikidata_close']  
        
        # identifier
        id_eintrag = 'tr:' + normalize_identifier(begriff)
        
        # ontolex:LexicalEntry
        ttl_eintrag = id_eintrag + r' a ontolex:LexicalEntry ;' + '\n'
        
        # rdfs:label
        ttl_eintrag += '\t' + r'rdfs:label "{}"@de ;'.format(begriff) + '\n'
        
        # ontolex:canonicalForm; removing optional number for the writtenRep
        ttl_eintrag += '\t' + r'ontolex:canonicalForm [' + '\n'
        ttl_eintrag += '\t\t' + r'a ontolex:Form ;' + '\n' + '\t\t' + r'ontolex:writtenRep "{}"@de ;'.format(re.sub(r'\d+$', '', begriff)) + '\n'
        
        # variants
        # no variants
        if pd.isna(varianten):
            ttl_eintrag += '\t' + r'] .' + '\n\n'
        # variants existing
        else:
            ttl_eintrag += '\t' + r'] ;' + '\n'
            var_string = ''
            # split string and save in list
            if ";" in varianten:
                var_list = varianten.split("; ")
                for var in var_list:
                    var_string = '\t' + r'ontolex:otherForm [' + '\n'
                    var_string += '\t\t' + r'a ontolex:Form ;' + '\n' + '\t\t' + r'ontolex:writtenRep "{}"@de ;'.format(var.strip()) + '\n' 
                    var_string += '\t' + r'] ;' + '\n'
                    ttl_eintrag += var_string
                # replace ; in last entry with .
                ttl_eintrag = ttl_eintrag[:-2] + r'.' + '\n\n'
            # single variant
            else:
                var_string = '\t' + r'ontolex:otherForm [' + '\n'
                var_string += '\t\t' + r'a ontolex:Form ;' + '\n' + '\t\t' + r'ontolex:writtenRep "{}"@de ;'.format(varianten.strip()) + '\n'
                var_string += '\t' + r'] .' + '\n\n'
                ttl_eintrag += var_string
                
        # ontolex:LexicalSense
        ttl_eintrag += r'tr:sense-' + normalize_identifier(begriff) + r' a ontolex:LexicalSense ;' + '\n'
        ttl_eintrag += '\t' + r'ontolex:isSenseOf {} ;'.format(id_eintrag) + '\n'
        
        # ontolex:reference
        # reference to Openthesaurus exists
        if pd.notna(referenz):
            # split string and save in list
            if ";" in (referenz):
                ref_list = referenz.split("; ")
                for ref in ref_list:
                    ttl_eintrag += '\t' + r'ontolex:reference <{}> ;'.format(ref.strip()) + '\n'
            # single reference
            else:
                ttl_eintrag += '\t' + r'ontolex:reference <{}> ;'.format(referenz.strip()) + '\n'
        
        # Wikidata mapping
        if pd.notna(wikidata_exact):
            ttl_eintrag += '\t' + r'ontolex:reference <{}> ;'.format(wikidata_exact.strip()) + '\n'
        if pd.notna(wikidata_close):
            ttl_eintrag += '\t' + r'ontolex:reference [' + '\n'
            ttl_eintrag += '\t\t' + r'skos:closeMatch <{}> ;'.format(wikidata_close.strip()) + '\n'
            ttl_eintrag += '\t' + r'] ;' + '\n'
            
        # concept mapping
        ttl_eintrag += '\t' + r'tree:isSenseInConcept tr:{} .'.format(konzept.strip())
        
        ttl_string = ttl_string + ttl_eintrag + '\n\n'
        
    return ttl_string
    

def write_ttl(ttl_string, output_file):
    ''' Writes string into a file.'''
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(ttl_string)
        file.flush()
    
    print(f"The TTL file has been saved under: {output_file}")

# === Coordinating function ===

def main(prefixes_concepts_file, vocab_file, output_file):
    prefixes_concepts = read_ttl(prefixes_concepts_file)
    df = read_tsv_to_dataframe(vocab_file)
    print("DataFrame:")
    print(df.head()) 
    ttl_string = transform_data(df)
    # merges predefined prefix declarations and concept definitions with new entries
    complete = prefixes_concepts + ttl_string
    write_ttl(complete, output_file)

main(prefixes_concepts_file, vocab_file, output_file)

