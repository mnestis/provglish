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
    SELECT ?entity ?generation ?time ?activity WHERE {
       GRAPH <prov_graph> {
          {
             ?entity a prov:Entity .
             ?entity prov:qualifiedGeneration ?generation .
             ?generation a prov:Generation .
             OPTIONAL { ?generation prov:atTime ?time } .
             OPTIONAL { ?generation prov:activity ?activity } .
             FILTER ( bound(?time) || bound(?activity))
          } UNION {
             ?entity a prov:Entity .
             ?entity prov:wasGeneratedBy ?activity .
             ?activity a prov:Activity
          }
       }
    }
    """,
    initNs={"prov":PROV})

def _generation_binding(graph):
    results = graph.query(_generation_query)
    return results.bindings

def _generation_coverage(bindings, graph):
    if "?generation" in bindings:
        # Qualified
        coverage = [(bindings["?entity"], RDF.type, PROV.Entity),
                    (bindings["?entity"], PROV.qualifiedGeneration, bindings["?generation"]),
                    (bindings["?generation"], RDF.type, PROV.Generation)]

        if "?time" in bindings:
            coverage.append((bindings["?generation"], PROV.atTime, bindings["?time"]))

        if "?activity" in bindings:
            coverage.extend([(bindings["?generation"], PROV.activity, bindings["?activity"]),
                             (bindings["?activity"], RDF.type, PROV.Activity)])

        return coverage
    else:
        # Unqualified
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?entity"], PROV.wasGeneratedBy, bindings["?activity"]),
                (bindings["?activity"], RDF.type, PROV.Activity)]

def _generation_string(bindings, history):
    sentence = {}

    sentence["object"] = {"type": "noun_phrase",
                           "head": lex(bindings["?entity"]),
                           "features": {"number": "plural" if plural_p(bindings["?entity"]) else "singular"}}

    sentence["verb"] = "generate"

    sentence["features"] = {"tense": "past",
                            "passive": "true"}

    sentence["modifiers"] = []

    if "?time" in bindings:
        sentence["modifiers"].append({"type":"preposition_phrase",
                                        "preposition": "at",
                                        "noun": bindings["?time"]})

    if "?activity" in bindings:
        sentence["modifiers"].append({"type":"preposition_phrase",
                                        "preposition":"by",
                                        "noun": lex(bindings["?activity"])})

    return realise_sentence({"sentence":sentence})

generation = transform.Template("Generation", _generation_binding, _generation_coverage, _generation_string)

