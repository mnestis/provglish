from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence
from provglish.nl.lexicalisation import activity_uri_to_noun_phrase_spec as act_spec

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_start_query = sparql.prepareQuery(
    """
       SELECT DISTINCT ?activity ?start ?trigger ?starter ?time WHERE {
          GRAPH <prov_graph> {
             {
                ?activity a prov:Activity .
                ?activity prov:wasStartedBy ?trigger .
                ?trigger a prov:Entity .
                FILTER NOT EXISTS {?activity prov:qualifiedStart ?start}
             } UNION {
                ?activity a prov:Activity .
                ?activity prov:qualifiedStart ?start .
                ?start a prov:Start .
                OPTIONAL { 
                   ?start prov:hadActivity ?starter .
                   ?starter a prov:Activity
                } .
                OPTIONAL {
                   ?start prov:entity ?trigger .
                   ?trigger a prov:Entity
                } .
                OPTIONAL {
                   ?start prov:atTime ?time
                } .
                FILTER (bound(?trigger) || bound(?starter) || bound(?time))
             }
          }
       }
    """,
    initNs={"prov":PROV})

def _start_binding(graph):
    results = graph.query(_start_query)
    return results.bindings

def _start_coverage(bindings, graph):
    coverage = [(bindings["?activity"], RDF.type, PROV.Activity)]
    
    if "?start" in bindings:
        # This is a qualified relation
        coverage.extend([(bindings["?activity"], PROV.qualifiedStart, bindings["?start"]),
                         (bindings["?start"], RDF.type, PROV.Start)])

        if "?starter" in bindings:
            coverage.extend([(bindings["?start"], PROV.hadActivity, bindings["?starter"]),
                             (bindings["?starter"], RDF.type, PROV.Activity)])
    
        if "?trigger" in bindings:
            coverage.extend([(bindings["?start"], PROV.entity, bindings["?trigger"]),
                             (bindings["?trigger"], RDF.type, PROV.Entity)])

        if "?time" in bindings:
            coverage.append((bindings["?start"], PROV.atTime, bindings["?time"]))
    else:
        # This is an unqualified relation
        coverage.extend([(bindings["?activity"], PROV.wasStartedBy, bindings["?trigger"]),
                         (bindings["?trigger"], RDF.type, PROV.Entity)])

    return coverage

def _start_string(bindings, history):

    sentence = {}

    if "?start" in bindings:
        # This is a qualified start
        if ("?starter" not in bindings) and ("?time" not in bindings):
            # This is a sentence where we talk about triggering.
            sentence["verb"] = "trigger"
            sentence["object"] = {"type": "noun_phrase",
                                  "head": "start of %s" % (act_spec(bindings["?activity"]),),
                                  "determiner": "the",
                                  "number": "singular"}

            sentence["subject"] = {"type": "noun_phrase",
                                   "head": lex(bindings["?trigger"])}
            
            sentence["features"] = {"tense":"past",
                                    "passive":"true"}
        else:
            sentence["verb"] = "start"
            sentence["object"] = {"type": "noun_phrase",
                                  "head": act_spec(bindings["?activity"]),
                                  "determiner": "the",
                                  "number": "singular"}
            sentence["features"] = {"tense": "past",
                                    "passive": "true"}

            if "?starter" in bindings:
                sentence["subject"] = {"type": "noun_phrase",
                                       "head": lex(bindings["?starter"])}

            if "?time" in bindings:
                sentence["modifiers"] = [{"type": "preposition_phrase",
                                            "preposition": "at",
                                            "noun": bindings["?time"]}]

    else:
        # This is an unqualified start
        sentence["verb"] = "trigger"
        sentence["object"] = {"type": "noun_phrase",
                              "head": "start of %s" % (act_spec(bindings["?activity"]),),
                              "determiner": "the"}
        sentence["subject"] = {"type": "noun_phrase",
                               "head": lex(bindings["?trigger"])}
        
        sentence["features"] = {"tense":"past",
                                "passive":"true"}


    return realise_sentence({"sentence":sentence})

start = transform.Template("Start", _start_binding, _start_coverage, _start_string)
