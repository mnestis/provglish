from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

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

def _agent_string(bindings):
    sentence = {}
    sentence["subject"] = {"type": "noun_phrase",
                           "head": lex(bindings["?agent"]),
                           "features":{"number": "plural" if plural_p(bindings["?agent"]) else "singular"}}
    sentence["verb"] = "be"
    sentence["object"] = {"type":"noun_phrase",
                          "head":"agent",
                          "determiner":"a"}

    return realise_sentence({"sentence":sentence})

agent = transform.Template("Agent", _agent_binding, _agent_coverage, _agent_string)
