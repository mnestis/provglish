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
    SELECT ?activity ?usage ?time WHERE {
       GRAPH <prov_graph> {
          ?activity a prov:Activity .
          ?activity prov:qualifiedUsage ?usage .
          ?uasge a prov:Usage .
          ?usage prov:atTime ?time .
       }
    }
    """,
    initNs={"prov":PROV})

def _usage_binding(graph):
    results = graph.query(_usage_query)
    return results.bindings

def _usage_coverage(bindings, graph):
    return [(bindings["?activity"], RDF.type, PROV.Entity),
            (bindings["?activity"], PROV.qualifiedUsage, bindings["?usage"]),
            (bindings["?usage"], RDF.type, PROV.Usage),
            (bindings["?usage"], PROV.atTime, bindings["?time"])]

def _usage_string(bindings):
    sentence = {}

    sentence["subject"] = lex(bindings["?activity"])

    sentence["verb"] = "use"

    sentence["object"] = "something"

    at_phrase = {"type": "preposition_phrase",
                 "noun": bindings["?time"],
                 "preposition": "at"}

    sentence["modifiers"] = [at_phrase]

    sentence["features"] = {"tense":"past"}

    return realise_sentence({"sentence":sentence})

usage = transform.Template("Usage", _usage_binding, _usage_coverage, _usage_string)

# This template deals with usages that have an entity, but no time

_usage_ent_query = sparql.prepareQuery(
    """
    SELECT ?activity ?usage ?entity WHERE {
       GRAPH <prov_graph> {
          {
             ?activity a prov:Activity .
             ?activity prov:qualifiedUsage ?usage .
             ?usage a prov:Usage .
             ?usage prov:entity ?entity .
             ?entity a prov:Entity
          
          } UNION {
             ?activity a prov:Activity .
             ?activity prov:used ?entity .
             ?entity a prov:Entity
          }
       } 
    }
    """,
    initNs={"prov":PROV})

def _usage_ent_binding(graph):
    results = graph.query(_usage_ent_query)
    return results.bindings

def _usage_ent_coverage(bindings, graph):
    if "?usage" in bindings:
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?activity"], PROV.qualifiedUsage, bindings["?usage"]),
                (bindings["?usage"], RDF.type, PROV.Usage),
                (bindings["?usage"], PROV.entity, bindings["?entity"]),
                (bindings["?activity"], RDF.type, PROV.Activity)]
    else:
        return [(bindings["?entity"], RDF.type, PROV.Entity),
                (bindings["?activity"], PROV.used, bindings["?entity"]),
                (bindings["?activity"], RDF.type, PROV.Activity)]

def _usage_ent_string(bindings):
    sentence = {}

    sentence["subject"] = lex(bindings["?activity"])

    sentence["object"] = {"type": "noun_phrase",
                          "head": lex(bindings["?entity"]),
                          "features": {"number": "plural" if plural_p(bindings["?entity"]) else "singular"}}
    
    sentence["verb"] = "use"

    sentence["features"] = {"tense": "past"}

    return realise_sentence({"sentence":sentence})

usage_entity = transform.Template("Usage entity", _usage_ent_binding, _usage_ent_coverage, _usage_ent_string)
