# 7 - Vokabular

## Overview
The folder for chapter 7 contains the conceptual vocabulary developed in this chapter for the semantic field of drinking in various file formats, as well as a script for conversion the vocabulary from TSV into a SKOS vocabulary in Turtle Syntax.

## Files
The vocabulary in different formats and scopes:
- `trinken_vokabular.tsv`
- `trinken_vokabular_nur_OT.tsv`
- `trinken_vokabular.json`
- `trinken_vokabular_nur_OT.json`
- `trinken_vokabular.ttl`
- `trinken_vokabular.tsv`

The files with the suffix “nur_OT” contain a reduced version of the vocabulary, in which the term entries are limited to the Openthesaurus source.

File used for the conversion into Turtle:
- `trinken_prefixes_concepts.ttl`


## Creation of the SKOS vocabulary

With the help of script_7_tsv2ttl.py the TSV version of the concept vocabulary is converted into a SKOS vocabulary in Turtle Syntax.

It loads a pre-existing file with defined prefixes and concepts, and appends the vocabulary entries in SKOS syntax according to the definition in Chapter 7.5.

### Input
- `trinken_prefixes_concepts.ttl` - contains definition of prefixes and concepts
- `trinken_vokabular.tsv` - TSV version of the vocabulary with mappings to Wikidata

### Output
- `trinken_vokabular.ttl`

## Publication of the SKOS vocabulary

The vocabulary is published via Skohub Pages (see https://github.com/skohub-io/skohub-pages).

You can find the corresponding repository here: https://github.com/KleeAn/trinken.

The published vocabulary can be found at this address:  https://kleean.github.io/trinken/TrinkenVokabular/Trinken_Vokabular.html.