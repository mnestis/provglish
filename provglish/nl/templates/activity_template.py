from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

# This first template deals with the simple existance of activities

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

# This next template handles activities with a start time.

_activity_start_query = sparql.prepareQuery(
    """SELECT ?activity ?start WHERE {
          GRAPH <prov_graph> {
             ?activity a prov:Activity .
             ?activity prov:startedAtTime ?start
          }
       }""",
    initNs= {"prov":PROV})

def _activity_start_binding(graph):
    results = graph.query(_activity_start_query)
    return results.bindings

def _activity_start_coverage(bindings, graph):
    return [(bindings["?activity"], RDF.type, PROV.Activity),
            (bindings["?activity"], PROV.startedAtTime, bindings["?start"])]

def _activity_start_string(bindings):
    sentence = {}

    sentence["subject"] = {"type":"noun_phrase",
                           "head":lex(bindings["?activity"])}

    sentence["verb"] = "be"

    sentence["object"] = {"type":"noun_phrase",
                          "head":"activity",
                          "determiner":"a",
                          "complements":[{"type":"clause",
                                          "spec":{"verb":"start",
                                                  "features":{"tense":"past",
                                                              "complementiser":"that"},
                                                  "modifiers":[{"type":"preposition_phrase",
                                                                "preposition":"at",
                                                                "noun":bindings["?start"]}]}}]}

    return realise_sentence({"sentence":sentence})

activity_start = transform.Template("Activity start", _activity_start_binding, _activity_start_coverage, _activity_start_string)

# This next template handles activities with an end time.

_activity_end_query = sparql.prepareQuery(
    """SELECT ?activity ?end WHERE {
          GRAPH <prov_graph> {
             ?activity a prov:Activity .
             ?activity prov:endedAtTime ?end
          }
       }""",
    initNs= {"prov":PROV})

def _activity_end_binding(graph):
    results = graph.query(_activity_end_query)
    return results.bindings

def _activity_end_coverage(bindings, graph):
    return [(bindings["?activity"], RDF.type, PROV.Activity),
            (bindings["?activity"], PROV.endedAtTime, bindings["?end"])]

def _activity_end_string(bindings):
    sentence = {}

    sentence["subject"] = {"type":"noun_phrase",
                           "head":lex(bindings["?activity"])}

    sentence["verb"] = "be"

    sentence["object"] = {"type":"noun_phrase",
                          "head":"activity",
                          "determiner":"a",
                          "complements":[{"type":"clause",
                                          "spec":{"verb":"end",
                                                  "features":{"tense":"past",
                                                              "complementiser":"that"},
                                                  "modifiers":[{"type":"preposition_phrase",
                                                                "preposition":"at",
                                                                "noun":bindings["?end"]}]}}]}

    return realise_sentence({"sentence":sentence})

activity_end = transform.Template("Activity end", _activity_end_binding, _activity_end_coverage, _activity_end_string)

