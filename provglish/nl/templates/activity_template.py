from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_activity_query = sparql.prepareQuery(
    """SELECT ?activity WHERE {
          GRAPH <prov_graph> {
             ?activity a prov:Activity . 
          }
    }""", 
    initNs={"prov":PROV}
)

def _activity_binding(graph):
    results = graph.query(_activity_query)
    return results.bindings

def _activity_coverage(bindings, graph):
    return [(bindings["?activity"], RDF.type, PROV.Activity)]

def _activity_string(bindings):
    sentence = {}
    sentence["subject"] = lex(bindings["?activity"])
    sentence["verb"] = "be"
    sentence["object"] = {"type":"noun_phrase",
                          "head":"activity",
                          "determiner":"a"}

    return realise_sentence({"sentence":sentence})

activity = transform.Template("Activity", _activity_binding, _activity_coverage, _activity_string)
