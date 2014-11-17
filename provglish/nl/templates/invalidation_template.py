from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_inv_query = sparql.prepareQuery(
    """SELECT ?entity ?activity ?time ?inv WHERE {
          GRAPH <prov_graph> {
             {
                ?entity prov:wasInvalidatedBy ?activity .
                ?entity a prov:Entity .
                ?activity a prov:Activity .
             } UNION {
                ?entity prov:qualifiedInvalidation ?inv .
                ?entity a prov:Entity .
                ?inv a prov:Invalidation .
                OPTIONAL { ?inv prov:activity ?activity .
                           ?activity a prov:Activity } .
                OPTIONAL { ?inv prov:atTime ?time } .
                FILTER (bound(?activity) || bound(?time))
             }
          }
    }""", 
    initNs={"prov":PROV}
)

def _inv_binding(graph):
    results = graph.query(_inv_query)
    return results.bindings

def _inv_coverage(bindings, graph):
    if "?inv" in bindings:
        coverage = [(bindings["?entity"], RDF.type, PROV.Entity),
                    (bindings["?entity"], PROV.qualifiedInvalidation, bindings["?inv"]),
                    (bindings["?inv"], RDF.type, PROV.Invalidation)]

        if "?activity" in bindings:
            coverage.extend([(bindings["?activity"], RDF.type, PROV.Activity),
                             (bindings["?inv"], PROV.activity, bindings["?activity"])])

        if "?time" in bindings:
            coverage.append((bindings["?inv"], PROV.atTime, bindings["?time"]))
        
        return coverage
    else:
        # Unqualified relationship, nice and easy
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?activity"], RDF.type, PROV.Activity),
                (bindings["?entity"], PROV.wasInvalidatedBy, bindings["?activity"])]

def _inv_string(bindings):
    sentence = {}
    
    sentence["object"] = {"type": "noun_phrase",
                          "head": lex(bindings["?entity"]),
                          "features": {"number": "plural" if plural_p(bindings["?entity"]) else "singular"}}

    sentence["verb"] = "invalidate"

    sentence["features"] = {"tense": "past",
                            "passive": "true"}

    if "?activity" in bindings:
        sentence["subject"] = lex(bindings["?activity"])

    if "?time" in bindings:
        sentence["modifiers"] = [{"type": "preposition_phrase",
                                  "noun": bindings["?time"],
                                  "preposition": "at"}]

    return realise_sentence({"sentence":sentence})

invalidation = transform.Template("Invalidation", _inv_binding, _inv_coverage, _inv_string)
