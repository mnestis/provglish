from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence
from provglish.nl.lexicalisation import agent_uri_to_noun_phrase_spec as ag_spec

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_agent_query = sparql.prepareQuery(
    """SELECT ?agent WHERE {
          GRAPH <prov_graph> {
             ?agent a prov:Agent . 
          }
    }""", 
    initNs={"prov":PROV}
)

def _agent_binding(graph):
    results = graph.query(_agent_query)
    return results.bindings

def _agent_coverage(bindings, graph):
    return [(bindings["?agent"], RDF.type, PROV.Agent)]

def _agent_string(bindings, history):
    sentence = {}
    sentence["subject"] = ag_spec(bindings["?agent"])
    sentence["verb"] = "be"
    sentence["object"] = {"type":"noun_phrase",
                          "head":"agent",
                          "determiner":"a"}

    sentence["features"] = {"tense": "past"}

    return realise_sentence({"sentence":sentence})

agent = transform.Template("Agent", _agent_binding, _agent_coverage, _agent_string)
