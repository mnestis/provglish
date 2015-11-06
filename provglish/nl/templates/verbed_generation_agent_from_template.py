from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence
from provglish.nl.lexicalisation import entity_uri_to_noun_phrase_spec as ent_spec
from provglish.nl.lexicalisation import activity_uri_to_noun_phrase_spec as act_spec
from provglish.nl.lexicalisation import agent_uri_to_noun_phrase_spec as ag_spec

from provglish.nl.lexicalisation import uri_contains_verb as verb_p
from provglish.nl.lexicalisation import activity_uri_to_verb_phrase_spec as verb_spec

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_generation_query = sparql.prepareQuery(
    """
    SELECT ?source ?entity ?generation ?activity ?agent WHERE {
       GRAPH <prov_graph> {
          {
             ?entity a prov:Entity .
             ?entity prov:qualifiedGeneration ?generation .
             ?generation a prov:Generation .
             ?generation prov:activity ?activity .
             ?activity prov:used ?source
             OPTIONAL { ?activity prov:wasAssociatedWith ?agent} .
             OPTIONAL { ?entity prov:wasAttributedTo ?agent} .
             FILTER bound(?agent)
          } UNION {
             ?entity a prov:Entity .
             ?entity prov:wasGeneratedBy ?activity .
             ?activity a prov:Activity .
             ?activity prov:used ?source
             OPTIONAL { ?activity prov:wasAssociatedWith ?agent} .
             OPTIONAL { ?entity prov:wasAttributedTo ?agent} .
             FILTER bound(?agent)
          }
       }
    }
    """,
    initNs={"prov":PROV})

def _generation_binding(graph):
    results = graph.query(_generation_query)
    initial_bindings = results.bindings
    filtered_bindings = []
    for binding in initial_bindings:
        if verb_p(binding["?activity"]):
            filtered_bindings.append(binding)

    return filtered_bindings

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

        # Agent coverage
        coverage.extend([(bindings["?agent"], RDF.type, PROV.Agent),
                         (bindings["?entity"], PROV.wasAttributedTo, bindings["?agent"]),
                         (bindings["?activity"], PROV.wasAssociatedWith, bindings["?agent"]),
                         (bindings["?activity"], PROV.used, bindings["?source"]),
                         (bindings["?source"], RDF.type, PROV.Entity)])

        return coverage
    else:
        # Unqualified
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?entity"], PROV.wasGeneratedBy, bindings["?activity"]),
                (bindings["?activity"], RDF.type, PROV.Activity),
                (bindings["?agent"], RDF.type, PROV.Agent),
                (bindings["?activity"], PROV.wasAssociatedWith, bindings["?agent"]),
                (bindings["?entity"], PROV.wasAttributedTo, bindings["?agent"]),
                (bindings["?activity"], PROV.used, bindings["?source"]),
                (bindings["?source"], RDF.type, PROV.Entity)]

def _generation_string(bindings, history):
    sentence = {}

    sentence["subject"] = ag_spec(bindings["?agent"])

    sentence["object"] = ent_spec(bindings["?entity"])

    sentence["verb"] = verb_spec(bindings["?activity"])

    sentence["features"] = {"tense": "past"}
   

    sentence["complements"] = [
        {"type":"preposition_phrase",
         "preposition": "from",
         "noun": ent_spec(bindings["?source"])}
    ]

    return realise_sentence({"sentence":sentence})

generation = transform.Template("Generation", _generation_binding, _generation_coverage, _generation_string)

