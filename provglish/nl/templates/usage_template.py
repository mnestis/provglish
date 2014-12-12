from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_usage_query = sparql.prepareQuery(
    """
    SELECT ?activity ?usage ?time ?entity WHERE {
       GRAPH <prov_graph> {
          {
             ?activity a prov:Activity .
             ?activity prov:qualifiedUsage ?usage .
             ?usage a prov:Usage .
             OPTIONAL { ?usage prov:atTime ?time } .
             OPTIONAL { ?usage prov:entity ?entity .
                        ?entity a prov:Entity } .
             FILTER ( bound(?time) || bound(?entity))
          } UNION {
             ?activity a prov:Activity .
             ?activity prov:used ?entity .
             ?entity a prov:Entity
          }
       }
    }
    """,
    initNs={"prov":PROV})

def _usage_binding(graph):
    results = graph.query(_usage_query)
    return results.bindings

def _usage_coverage(bindings, graph):
    if "?usage" in bindings:
        # Qualified
        coverage = [(bindings["?activity"], RDF.type, PROV.Activity),
                    (bindings["?activity"], PROV.qualifiedUsage, bindings["?usage"]),
                    (bindings["?usage"], RDF.type, PROV.Usage)]

        if "?time" in bindings:
            coverage.append((bindings["?usage"], PROV.atTime, bindings["?time"]))

        if "?entity" in bindings:
            coverage.extend([(bindings["?usage"], PROV.entity, bindings["?entity"]),
                             (bindings["?entity"], RDF.type, PROV.Entity)])

        return coverage
    else:
        # Unqualified
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?activity"], PROV.used, bindings["?entity"]),
                (bindings["?activity"], RDF.type, PROV.Activity)]

def _usage_string(bindings, history):
    sentence = {}

    sentence["subject"] = lex(bindings["?activity"])

    sentence["verb"] = "use"

    sentence["features"] = {"tense": "past"}

    sentence["modifiers"] = []

    if "?entity" in bindings:
        sentence["object"] = {"type": "noun_phrase",
                              "head": lex(bindings["?entity"]),
                              "features": {"number": "plural" if plural_p(bindings["?entity"]) else "singular"}}

    else:
        sentence["object"] = "something"

    if "?time" in bindings:
        sentence["modifiers"].append({"type":"preposition_phrase",
                                        "preposition": "at",
                                        "noun": bindings["?time"]})

    return realise_sentence({"sentence":sentence})

usage = transform.Template("Usage", _usage_binding, _usage_coverage, _usage_string)

