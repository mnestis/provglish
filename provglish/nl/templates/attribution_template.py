from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_attribution_query = sparql.prepareQuery(
    """SELECT DISTINCT ?entity ?agent ?attr WHERE {
          GRAPH <prov_graph> {
             {
                ?entity a prov:Entity .
                ?entity prov:wasAttributedTo ?agent .
                ?agent a prov:Agent
             } UNION {
                ?entity a prov:Entity .
                ?entity prov:qualifiedAttribution ?attr .
                ?attr a prov:Attribution .
                ?attr prov:agent ?agent .
                ?agent a prov:Agent 
             }
          }
    }""", 
    initNs={"prov":PROV}
)

def _attribution_binding(graph):
    results = graph.query(_attribution_query)
    return results.bindings

def _attribution_coverage(bindings, graph):
    if "?attr" in bindings:
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?entity"], PROV.qualifiedAttribution, bindings["?attr"]),
                (bindings["?attr"], RDF.type, PROV.Attribution),
                (bindings["?attr"], PROV.agent, bindings["?agent"]),
                (bindings["?agent"], RDF.type, PROV.Agent)]
    else:
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?entity"], PROV.wasAttributedTo, bindings["?agent"]),
                (bindings["?agent"], RDF.type, PROV.Agent)]

def _attribution_string(bindings, history):
    sentence = {}

    sentence["object"] = {"type": "noun_phrase",
                          "head": lex(bindings["?entity"]),
                          "features": {"number": "plural" if plural_p(bindings["?entity"]) else "singular"}}
    sentence["verb"] = "attribute"

    sentence["modifiers"] = [{"type": "preposition_phrase",
                               "preposition": "to",
                               "noun": lex(bindings["?agent"])}]

    sentence["features"] = {"tense": "past",
                            "passive": "true"}

    return realise_sentence({"sentence":sentence})

attribution = transform.Template("Attribution", _attribution_binding, _attribution_coverage, _attribution_string)
