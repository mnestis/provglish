from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_entity_query = sparql.prepareQuery(
    """SELECT ?entity WHERE {
          GRAPH <prov_graph> {
             ?entity a prov:Entity . 
          }
    }""", 
    initNs={"prov":PROV}
)

def _entity_binding(graph):
    results = graph.query(_entity_query)
    return results.bindings

def _entity_coverage(bindings, graph):
    return [(bindings["?entity"], RDF.type, PROV.Entity)]

def _entity_string(bindings):
    sentence = {}
    sentence["subject"] = {"type": "noun_phrase",
                           "head": lex(bindings["?entity"]),
                           "features":{"number": "plural" if plural_p(bindings["?entity"]) else "singular"}}
    sentence["verb"] = "be"
    sentence["object"] = {"type":"noun_phrase",
                          "head":"entity",
                          "determiner":"a"}

    sentence["features"] = {"tense": "past"}

    return realise_sentence({"sentence":sentence})

entity = transform.Template("Entity", _entity_binding, _entity_coverage, _entity_string)
