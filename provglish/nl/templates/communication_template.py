from provglish import transform, prov
from provglish.lexicalisation import urn_from_uri as lex
from provglish.lexicalisation import plural_p
from provglish.prov import PROV
from provglish.nl.tools import SETTINGS, realise_sentence

import rdflib
from rdflib.plugins import sparql
from rdflib import RDF

import urllib2

_comm_query = sparql.prepareQuery(
    """SELECT ?act_1 ?act_2 ?comm WHERE {
          GRAPH <prov_graph> {
             {
                ?act_1 a prov:Activity .
                ?act_1 prov:qualifiedCommunication ?comm .
                ?comm a prov:Communication .
                ?comm prov:activity ?act_2 .
                ?act_2 a prov:Activity .
             } UNION {
                ?act_1 a prov:Activity .
                ?act_1 prov:wasInformedBy ?act_2 .
                ?act_2 a prov:Activity .
             }
          }
    }""", 
    initNs={"prov":PROV}
)

def _comm_binding(graph):
    results = graph.query(_comm_query)
    return results.bindings

def _comm_coverage(bindings, graph):
    if "?comm" in bindings:
        return [(bindings["?act_1"], RDF.type, PROV.Activity),
                (bindings["?comm"], RDF.type, PROV.Communication),
                (bindings["?act_2"], RDF.type, PROV.Activity),
                (bindings["?act_1"], PROV.qualifiedCommunication, bindings["?comm"]),
                (bindings["?comm"], PROV.activity, bindings["?act_2"])]
    else:
        return [(bindings["?act_1"], RDF.type, PROV.Activity),
                (bindings["?act_2"], RDF.type, PROV.Activity),
                (bindings["?act_1"], PROV.wasInformedBy, bindings["?act_2"])]

def _comm_string(bindings, history):
    sentence = {}
    
    sentence["subject"] = lex(bindings["?act_2"])
    sentence["verb"] = "inform"
    sentence["object"] = lex(bindings["?act_1"])
    
    sentence["features"] = {"tense": "past",
                            "passive": "true"}

    return realise_sentence({"sentence":sentence})

communication = transform.Template("Communication", _comm_binding, _comm_coverage, _comm_string)
