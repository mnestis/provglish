from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_generation_query = sparql.prepareQuery(
    """
    SELECT ?entity ?generation ?time WHERE {
       GRAPH <prov_graph> {
          ?entity a prov:Entity .
          ?entity prov:qualifiedGeneration ?generation .
          ?generation a prov:Generation .
          ?generation prov:atTime ?time .
       }
    }
    """,
    initNs={"prov":PROV})

def _generation_binding(graph):
    results = graph.query(_generation_query)
    return results.bindings

def _generation_coverage(bindings, graph):
    return [(bindings["?entity"], RDF.type, PROV.Entity),
            (bindings["?entity"], PROV.qualifiedGeneration, bindings["?generation"]),
            (bindings["?generation"], RDF.type, PROV.Generation),
            (bindings["?generation"], PROV.atTime, bindings["?time"])]

def _generation_string(bindings):
    sentence = {}

    sentence["object"] = {"type": "noun_phrase",
                          "head": lex(bindings["?entity"]),
                          "features": {"number": "plural" if plural_p(bindings["?entity"]) else "singular"}}
    
    sentence["verb"] = "generate"

    at_phrase = {"type": "preposition_phrase",
                 "noun": bindings["?time"],
                 "preposition": "at"}

    sentence["modifiers"] = [at_phrase]

    sentence["features"] = {"passive":"true",
                            "tense": "past"}

    return realise_sentence({"sentence":sentence})

generation = transform.Template("Generation", _generation_binding, _generation_coverage, _generation_string)
