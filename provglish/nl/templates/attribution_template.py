from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence
from provglish.nl.lexicalisation import entity_uri_to_noun_phrase_spec as ent_spec
from provglish.nl.lexicalisation import agent_uri_to_noun_phrase_spec as ag_spec

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

    sentence["object"] = ent_spec(bindings["?entity"])
    sentence["verb"] = "attribute"

    sentence["modifiers"] = [{"type": "preposition_phrase",
                               "preposition": "to",
                               "noun": ag_spec(bindings["?agent"])}]

    sentence["features"] = {"tense": "past",
                            "passive": "true"}

    return realise_sentence({"sentence":sentence})

attribution = transform.Template("Attribution", _attribution_binding, _attribution_coverage, _attribution_string)
