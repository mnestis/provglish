from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_del_query = sparql.prepareQuery(
    """SELECT ?delegate ?delegator ?activity ?delegation WHERE {
          GRAPH <prov_graph> {
             {
                ?delegate a prov:Agent .
                ?delegate prov:actedOnBehalfOf ?delegator .
                ?delegator a prov:Agent
             } UNION {
                ?delegate a prov:Agent .
                ?delegate prov:qualifiedDelegation ?delegation .
                ?delegation a prov:Delegation . 
                OPTIONAL { ?delegation prov:agent ?delegator .
                           ?delegator a prov:Agent } .
                OPTIONAL { ?delegation prov:hadActivity ?activity .
                           ?activity a prov:Activity }
             }
          }
    }""", 
    initNs={"prov":PROV}
)

def _del_binding(graph):
    results = graph.query(_del_query)
    return results.bindings

def _del_coverage(bindings, graph):
    if "?delegation" in bindings:
        # Qualified derivation follows:
        coverage =  [(bindings["?delegate"], RDF.type, PROV.Agent),
                     (bindings["?delegate"], PROV.qualifiedDelegation, bindings["?delegation"]),
                     (bindings["?delegation"], RDF.type, PROV.Delegation)]
        
        if "?delegator" in bindings:
            coverage.extend([(bindings["?delegation"], PROV.agent, bindings["?delegator"]),
                             (bindings["?delegator"], RDF.type, PROV.Agent)])

        if "?activity" in bindings:
            coverage.extend([(bindings["?delegation"], PROV.hadActivity, bindings["?activity"]),
                             (bindings["?activity"], RDF.type, PROV.Activity)])

        return coverage

    else:
        return [(bindings["?delegate"], RDF.type, PROV.Agent),
                (bindings["?delegate"], PROV.actedOnBehalfOf, bindings["?delegator"]),
                (bindings["?delegator"], RDF.type, PROV.Agent)]

def _del_string(bindings, history):
    sentence = {}

    sentence["subject"] = lex(bindings["?delegate"])
    
    if "?delegator" in bindings:
        sentence["modifiers"] = [{"type": "preposition_phrase",
                                  "preposition": "on behalf of",
                                  "noun": lex(bindings["?delegator"])}]

    if "?activity" in bindings:
        sentence["verb"] = "do"
        sentence["object"] = lex(bindings["?activity"])
    else:
        sentence["verb"] = "act"

    sentence["features"] = {"tense":"past"}

    return realise_sentence({"sentence":sentence})

delegation = transform.Template("Delegation", _del_binding, _del_coverage, _del_string)
