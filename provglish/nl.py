from provglish import transform, prov
from rdflib.plugins import sparql
import rdflib
from prov import PROV
import lexicalisation as lex
from nlg_tools import SETTINGS, realise_sentence
import urllib2

_ag_der_ent_by_act_query = sparql.prepareQuery(
    """SELECT ?agent ?entity ?activity ?deriv WHERE {
          GRAPH <prov_graph>
          {
             ?activity <http://www.w3.org/ns/prov#wasAssociatedWith> ?agent .
             ?entity <http://www.w3.org/ns/prov#qualifiedDerivation> ?deriv .
             ?deriv <http://www.w3.org/ns/prov#hadActivity> ?activity .
          }
    }""")

def _ag_der_ent_by_act_binding(graph):
    results = graph.query(_ag_der_ent_by_act_query)
    return results.bindings

def _ag_der_ent_by_act_coverage(bindings, graph):
    rdf = rdflib.namespace.RDF

    coverage_list = []
    
    coverage_list.append((bindings["?activity"], PROV.wasAssociatedWith, bindings["?agent"]))
    coverage_list.append((bindings["?activity"], RDF.type, PROV.Activity))
    coverage_list.append((bindings["?agent"], RDF.type, PROV.Agent))
    coverage_list.append((bindings["?entity"], PROV.qualifiedDerivation, bindings["?deriv"]))
    coverage_list.append((bindings["?entity"], RDF.type, PROV.Entity))
    coverage_list.append((bindings["?deriv"], RDF.type, PROV.Derivation))
    coverage_list.append((bindings["?deriv"], PROV.hadActivity, bindings["?activity"]))

    return coverage_list

def _ag_der_ent_by_act_string(bindings):
    
    sentence = {
        "subject": lex.urn_from_uri(bindings["?agent"]),
        "verb": lex.urn_from_uri(bindings["?activity"]),
        "object": {"type": "noun_phrase",
                   "head": lex.urn_from_uri(bindings["?entity"]),
                   "determiner": "a",
                   "features": [{"number": "plural" if lex.plural_p(lex.urn_from_uri(bindings["?entity"])) else "singular"}]},
        "features": [{"tense":"past"}]
    }

    return realise_sentence({"sentence": sentence})

_ag_der_ent_by_act_template = transform.Template("Agent derived entity by activity",
                                                 _ag_der_ent_by_act_binding,
                                                 _ag_der_ent_by_act_coverage,
                                                 _ag_der_ent_by_act_string)
