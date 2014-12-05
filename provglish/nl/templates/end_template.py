from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_end_query = sparql.prepareQuery(
    """
       SELECT DISTINCT ?activity ?end ?trigger ?ender ?time WHERE {
          GRAPH <prov_graph> {
             {
                ?activity a prov:Activity .
                ?activity prov:wasEndedBy ?trigger .
                ?trigger a prov:Entity .
                FILTER NOT EXISTS { ?activity prov:qualifiedEnd ?end }
             } UNION {
                ?activity a prov:Activity .
                ?activity prov:qualifiedEnd ?end .
                ?end a prov:End .
                OPTIONAL { 
                   ?end prov:hadActivity ?ender .
                   ?ender a prov:Activity
                } .
                OPTIONAL {
                   ?end prov:entity ?trigger .
                   ?trigger a prov:Entity
                } .
                OPTIONAL {
                   ?end prov:atTime ?time
                } .
                FILTER (bound(?trigger) || bound(?ender) || bound(?time))
             }
          }
       }
    """,
    initNs={"prov":PROV})

def _end_binding(graph):
    results = graph.query(_end_query)
    return results.bindings

def _end_coverage(bindings, graph):
    coverage = [(bindings["?activity"], RDF.type, PROV.Activity)]
    
    if "?end" in bindings:
        # This is a qualified relation
        coverage.extend([(bindings["?activity"], PROV.qualifiedEnd, bindings["?end"]),
                         (bindings["?end"], RDF.type, PROV.End)])

        if "?ender" in bindings:
            coverage.extend([(bindings["?end"], PROV.hadActivity, bindings["?ender"]),
                             (bindings["?ender"], RDF.type, PROV.Activity)])
    
        if "?trigger" in bindings:
            coverage.extend([(bindings["?end"], PROV.entity, bindings["?trigger"]),
                             (bindings["?trigger"], RDF.type, PROV.Entity)])

        if "?time" in bindings:
            coverage.append((bindings["?end"], PROV.atTime, bindings["?time"]))
    else:
        # This is an unqualified relation
        coverage.extend([(bindings["?activity"], PROV.wasEndedBy, bindings["?trigger"]),
                         (bindings["?trigger"], RDF.type, PROV.Entity)])

    return coverage

def _end_string(bindings):

    sentence = {}

    if "?end" in bindings:
        # This is a qualified start
        if ("?ender" not in bindings) and ("?time" not in bindings):
            # This is a sentence where we talk about triggering.
            sentence["verb"] = "trigger"
            sentence["object"] = {"type": "noun_phrase",
                                  "head": "end of %s" % (lex(bindings["?activity"]),),
                                  "determiner": "the",
                                  "number": "singular"}

            sentence["subject"] = {"type": "noun_phrase",
                                   "head": lex(bindings["?trigger"])}
            
            sentence["features"] = {"tense":"past",
                                    "passive":"true"}
        else:
            sentence["verb"] = "end"
            sentence["object"] = {"type": "noun_phrase",
                                  "head": lex(bindings["?activity"]),
                                  "determiner": "the",
                                  "number": "singular"}
            sentence["features"] = {"tense": "past",
                                    "passive": "true"}

            if "?ender" in bindings:
                sentence["subject"] = {"type": "noun_phrase",
                                       "head": lex(bindings["?ender"])}

            if "?time" in bindings:
                sentence["modifiers"] = [{"type": "preposition_phrase",
                                            "preposition": "at",
                                            "noun": bindings["?time"]}]

    else:
        # This is an unqualified start
        sentence["verb"] = "trigger"
        sentence["object"] = {"type": "noun_phrase",
                              "head": "end of %s" % (lex(bindings["?activity"]),),
                              "determiner": "the"}
        sentence["subject"] = {"type": "noun_phrase",
                               "head": lex(bindings["?trigger"])}
        
        sentence["features"] = {"tense":"past",
                                "passive":"true"}


    return realise_sentence({"sentence":sentence})

end = transform.Template("End", _end_binding, _end_coverage, _end_string)
