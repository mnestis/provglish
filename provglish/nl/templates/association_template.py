from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_assoc_query = sparql.prepareQuery(
    """SELECT DISTINCT ?activity ?agent ?assoc WHERE {
          GRAPH <prov_graph> {
             {
                ?activity a prov:Activity .
                ?activity prov:wasAssociatedWith ?agent .
                ?agent a prov:Agent
             } UNION {
                ?activity a prov:Activity .
                ?activity prov:qualifiedAssociation ?assoc .
                ?assoc a prov:Association .
                ?assoc prov:agent ?agent .
                ?agent a prov:Agent 
             }
          }
    }""", 
    initNs={"prov":PROV}
)

def _assoc_binding(graph):
    results = graph.query(_assoc_query)
    return results.bindings

def _assoc_coverage(bindings, graph):
    if "?assoc" in bindings:
        return [(bindings["?activity"], RDF.type, PROV.Activity),
                (bindings["?activity"], PROV.qualifiedAssociation, bindings["?assoc"]),
                (bindings["?assoc"], RDF.type, PROV.Association),
                (bindings["?assoc"], PROV.agent, bindings["?agent"]),
                (bindings["?agent"], RDF.type, PROV.Agent)]
    else:
        return [(bindings["?activity"], RDF.type, PROV.Activity),
                (bindings["?activity"], PROV.wasAssociatedWith, bindings["?agent"]),
                (bindings["?agent"], RDF.type, PROV.Agent)]

def _assoc_string(bindings):
    sentence = {}

    sentence["object"] = {"type": "noun_phrase",
                          "head": lex(bindings["?activity"])}

    sentence["verb"] = "associate"

    sentence["modifiers"] = [{"type": "preposition_phrase",
                               "preposition": "with",
                               "noun": lex(bindings["?agent"])}]

    sentence["features"] = {"tense": "past",
                            "passive": "true"}

    return realise_sentence({"sentence":sentence})

association = transform.Template("Association", _assoc_binding, _assoc_coverage, _assoc_string)
