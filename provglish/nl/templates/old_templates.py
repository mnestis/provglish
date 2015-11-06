from provglish import transform, prov
from rdflib.plugins import sparql
import rdflib
from provglish.prov import PROV
import provglish.lexicalisation as lex
from provglish.nl.tools import SETTINGS, realise_sentence
import urllib2

from provglish.nl.lexicalisation import activity_uri_to_verb_phrase_spec as verb_spec
from provglish.nl.lexicalisation import agent_uri_to_noun_phrase_spec as ag_spec
from provglish.nl.lexicalisation import entity_uri_to_noun_phrase_spec as ent_spec

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
    coverage_list.append((bindings["?activity"], rdf.type, PROV.Activity))
    coverage_list.append((bindings["?agent"], rdf.type, PROV.Agent))
    coverage_list.append((bindings["?entity"], PROV.qualifiedDerivation, bindings["?deriv"]))
    coverage_list.append((bindings["?entity"], rdf.type, PROV.Entity))
    coverage_list.append((bindings["?deriv"], rdf.type, PROV.Derivation))
    coverage_list.append((bindings["?deriv"], PROV.hadActivity, bindings["?activity"]))

    return coverage_list

def _ag_der_ent_by_act_string(bindings, history):
    
    sentence = {
        "subject": ent_spec(bindings["?agent"]),
        "verb": verb_spec(bindings["?activity"]),
        "object": ent_spec(bindings["?entity"]),
        "features": {"tense":"past"}
    }

    return realise_sentence({"sentence": sentence})

_ag_der_ent_by_act_template = transform.Template("Agent derived entity by activity",
                                                 _ag_der_ent_by_act_binding,
                                                 _ag_der_ent_by_act_coverage,
                                                 _ag_der_ent_by_act_string)

_der_ent_by_act_query = sparql.prepareQuery(
    """SELECT ?entity ?activity ?deriv WHERE {
          GRAPH <prov_graph>
          {
             ?entity <http://www.w3.org/ns/prov#qualifiedDerivation> ?deriv .
             ?deriv <http://www.w3.org/ns/prov#hadActivity> ?activity .
          }
    }""")

def _der_ent_by_act_binding(graph):
    results = graph.query(_der_ent_by_act_query)
    return results.bindings

def _der_ent_by_act_coverage(bindings, graph):
    rdf = rdflib.namespace.RDF

    coverage_list = []
    
    coverage_list.append((bindings["?activity"], rdf.type, PROV.Activity))
    coverage_list.append((bindings["?entity"], PROV.qualifiedDerivation, bindings["?deriv"]))
    coverage_list.append((bindings["?entity"], rdf.type, PROV.Entity))
    coverage_list.append((bindings["?deriv"], rdf.type, PROV.Derivation))
    coverage_list.append((bindings["?deriv"], PROV.hadActivity, bindings["?activity"]))

    return coverage_list

def _der_ent_by_act_string(bindings, history):
    
    sentence = {
        "verb": verb_spec(bindings["?activity"]),
        "object": ent_spec(bindings["?entity"]),
        "features": {"tense":"past",
                     "passive":"true"}
    }

    return realise_sentence({"sentence": sentence})

_der_ent_by_act_template = transform.Template("Derived entity by activity",
                                                 _der_ent_by_act_binding,
                                                 _der_ent_by_act_coverage,
                                                 _der_ent_by_act_string)


_collection_enum_query = sparql.prepareQuery(
    """SELECT DISTINCT ?collection ?member WHERE {
          GRAPH <prov_graph> {
             ?collection a prov:Collection .
             ?collection prov:hadMember ?member
          }
    } ORDER BY ?collection ?member""", initNs={"prov":PROV})

def _collection_enum_bindings(graph):
    memberships = graph.query(_collection_enum_query)
    raw_bindings = memberships.bindings

    grouped_bindings = []
    current_collection = None

    for binding in raw_bindings:
        if binding["?collection"] != current_collection:
            current_collection = binding["?collection"]
            grouped_bindings.append({"?collection": current_collection,
                                     "?members": []})
        grouped_bindings[-1]["?members"].append(binding["?member"])

    return grouped_bindings

def _collection_enum_coverage(bindings, graph):
    rdf = rdflib.namespace.RDF
    coverage = []

    coverage.append((bindings["?collection"], rdf.type, PROV.Collection))
    coverage.append((bindings["?collection"], rdf.type, PROV.Entity))

    for member in bindings["?members"]:
        coverage.append((bindings["?collection"], PROV.hadMember, member))
        coverage.append((member, rdf.type, PROV.Entity))

    return coverage

def _collection_enum_string(bindings, history):
    
    collection_lex = lex.urn_from_uri(bindings["?collection"])
    collection_pl_p = lex.plural_p(collection_lex)

    sentence = {"subject": {"type":"noun_phrase",
                            "determiner":"the",
                            "head": collection_lex,
                            "features": {"number": "plural" if collection_pl_p else "singular"}},
                "verb": "be" if collection_pl_p else "contain",
                "object": {"type": "coordinated_phrase",
                           "conjunction": "and",
                           "coordinates":[]},
                "features": {"tense":"past"}}

    for member in bindings["?members"]:
        member_lex = lex.urn_from_uri(member)
        member_pl_p = lex.plural_p(member_lex)
        sentence["object"]["coordinates"].append({"type": "noun_phrase",
                                                  "head": member_lex,
                                                  "features": {"number": "plural" if member_pl_p else "singular"}})

    return realise_sentence({"sentence": sentence})

_collection_enum_template = transform.Template("Collection details",
                                               _collection_enum_bindings,
                                               _collection_enum_coverage,
                                               _collection_enum_string)
