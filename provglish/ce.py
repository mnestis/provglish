from provglish import transform, prov
from rdflib.plugins import sparql
import rdflib

import inflect

_nl = inflect.engine()

classes = {
    "http://www.w3.org/ns/prov#Entity": "entity",
    "http://www.w3.org/ns/prov#Activity": "activity", 
    "http://www.w3.org/ns/prov#Agent": "agent",
    "http://www.w3.org/ns/prov#Collection": "collection",
    "http://www.w3.org/ns/prov#EmptyCollection": "empty collection",
    "http://www.w3.org/ns/prov#Bundle": "provenance bundle",
    "http://www.w3.org/ns/prov#Person": "person",
    "http://www.w3.org/ns/prov#SoftwareAgent": "software agent",
    "http://www.w3.org/ns/prov#Organization": "organization",
    "http://www.w3.org/ns/prov#Location": "location",
    "http://www.w3.org/ns/prov#Influence": "influence",
    "http://www.w3.org/ns/prov#EntityInfluence": "entity-influence",
    "http://www.w3.org/ns/prov#Usage": "usage",
    "http://www.w3.org/ns/prov#Start": "start",
    "http://www.w3.org/ns/prov#End": "end",
    "http://www.w3.org/ns/prov#Derivation": "derivation",
    "http://www.w3.org/ns/prov#PrimarySource": "primary source",
    "http://www.w3.org/ns/prov#Quotation": "quotation",
    "http://www.w3.org/ns/prov#Revision": "revision",
    "http://www.w3.org/ns/prov#ActivityInfluence": "activity-influence",
    "http://www.w3.org/ns/prov#Generation": "generation",
    "http://www.w3.org/ns/prov#Communication": "communication",
    "http://www.w3.org/ns/prov#Invalidation": "invalidation",
    "http://www.w3.org/ns/prov#AgentInfluence": "agent-influence",
    "http://www.w3.org/ns/prov#Attribution": "attribution",
    "http://www.w3.org/ns/prov#Association": "association",
    "http://www.w3.org/ns/prov#Plan": "plan",
    "http://www.w3.org/ns/prov#Delegation": "delegation",
    "http://www.w3.org/ns/prov#InstantaneousEvent": "instantaneous event",
    "http://www.w3.org/ns/prov#Role": "role"
}

simple_predicates = {
    "http://www.w3.org/ns/prov#wasGeneratedBy": "was generated by",
    "http://www.w3.org/ns/prov#wasDerivedFrom": "was derived from",
    "http://www.w3.org/ns/prov#wasAttributedTo": "was attributed to",
    "http://www.w3.org/ns/prov#startedAtTime": "started at",
    "http://www.w3.org/ns/prov#used": "used",
    "http://www.w3.org/ns/prov#wasInformedBy": "was informed by",
    "http://www.w3.org/ns/prov#endedAtTime": "ended at",
    "http://www.w3.org/ns/prov#wasAssociatedWith": "was associated with",
    "http://www.w3.org/ns/prov#actedOnBehalfOf": "acted on behalf of",
    "http://www.w3.org/ns/prov#alternateOf": "is an alternate of",
    "http://www.w3.org/ns/prov#specializationOf": "is a specialization of",
    "http://www.w3.org/ns/prov#generatedAtTime": "was generated at",
    "http://www.w3.org/ns/prov#hadPrimarySource": "had as its primary source",
    "http://www.w3.org/ns/prov#value": "had as its value", # Check this one works...
    "http://www.w3.org/ns/prov#wasQuotedFrom": "was quoted from",
    "http://www.w3.org/ns/prov#wasRevisionOf": "was a revision of",
    "http://www.w3.org/ns/prov#invalidatedAtTime": "was invalidated at",
    "http://www.w3.org/ns/prov#wasInvalidatedBy": "was invalidated by",
    "http://www.w3.org/ns/prov#hadMember": "had as a member",
    "http://www.w3.org/ns/prov#wasStartedBy": "was started by",
    "http://www.w3.org/ns/prov#wasEndedBy": "was ended by",
    "http://www.w3.org/ns/prov#invalidated": "invalidated",
    "http://www.w3.org/ns/prov#influenced": "influenced",
    "http://www.w3.org/ns/prov#atLocation": "had as its location",
    "http://www.w3.org/ns/prov#generated": "generated",
    "http://www.w3.org/ns/prov#wasInfluencedBy": "was influenced by",
    "http://www.w3.org/ns/prov#qualifiedInfluence": "was influenced according to",
    "http://www.w3.org/ns/prov#qualifiedGeneration": "was generated according to",
    "http://www.w3.org/ns/prov#qualifiedDerivation": "was derived according to",
    "http://www.w3.org/ns/prov#qualifiedPrimarySource": "had its primary source according to",
    "http://www.w3.org/ns/prov#qualifiedQuotation": "was quoted according to",
    "http://www.w3.org/ns/prov#qualifiedRevision": "was revised according to",
    "http://www.w3.org/ns/prov#qualifiedAttribution": "was attributed according to",
    "http://www.w3.org/ns/prov#qualifiedInvalidation": "was invalidated according to",
    "http://www.w3.org/ns/prov#qualifiedStart": "was started according to",
    "http://www.w3.org/ns/prov#qualifiedUsage": "was used according to",
    "http://www.w3.org/ns/prov#qualifiedCommunication": "was informed according to",
    "http://www.w3.org/ns/prov#qualifiedAssociation": "was associated according to",
    "http://www.w3.org/ns/prov#qualifiedEnd": "was ended according to",
    "http://www.w3.org/ns/prov#qualifiedDelegation": "was delegated according to"
}

qualified_predicates = {
    "http://www.w3.org/ns/prov#Influence": {
        "http://www.w3.org/ns/prov#influencer": "entails influencing by",
        "http://www.w3.org/ns/prov#hadActivity": "entails influencing by", # Note the clash here!
        "http://www.w3.org/ns/prov#hadRole": "entails influencing as"
    },
    "http://www.w3.org/ns/prov#Generation": {
        "http://www.w3.org/ns/prov#activity": "entails generation by",
        "http://www.w3.org/ns/prov#atTime": "entails generation at",
    },
    "http://www.w3.org/ns/prov#Derivation": {
        "http://www.w3.org/ns/prov#entity": "entails derivation from",
        "http://www.w3.org/ns/prov#hadActivity": "entails derivation by",
        "http://www.w3.org/ns/prov#hadUsage": "entails derivation using a source according to",
        "http://www.w3.org/ns/prov#hadGeneration": "entails derivation generating a derivative according to"
    },
    "http://www.w3.org/ns/prov#PrimarySource": {
        "http://www.w3.org/ns/prov#entity": "entails derivation primarily from",
        "http://www.w3.org/ns/prov#hadActivity": "entails derivation by",
        "http://www.w3.org/ns/prov#hadUsage": "entails derivation primarily using a source according to",
        "http://www.w3.org/ns/prov#hadGeneration": "entails derivation generating a derivative according to"
    },
    "http://www.w3.org/ns/prov#Quotation": {
        "http://www.w3.org/ns/prov#entity": "entails quotation from",
        "http://www.w3.org/ns/prov#hadActivity": "entails quotation by",
        "http://www.w3.org/ns/prov#hadUsage": "entails quotation using a source according to",
        "http://www.w3.org/ns/prov#hadGeneration": "entails quotation generating a derivative according to"   
    },
    "http://www.w3.org/ns/prov#Revision": {
        "http://www.w3.org/ns/prov#entity": "entails revision from",
        "http://www.w3.org/ns/prov#hadActivity": "entails revision by",
        "http://www.w3.org/ns/prov#hadUsage": "entails revision using a source according to",
        "http://www.w3.org/ns/prov#hadGeneration": "entails revision generating a derivative according to"  
    },
    "http://www.w3.org/ns/prov#Attribution": {
        "http://www.w3.org/ns/prov#agent": "entails attribution to"
    },
    "http://www.w3.org/ns/prov#Invalidation": {
        "http://www.w3.org/ns/prov#activity": "entails invalidation by",
        "http://www.w3.org/ns/prov#atTime": "entails invalidation at"
    },
    "http://www.w3.org/ns/prov#Start": {
        "http://www.w3.org/ns/prov#hadActivity": "entails generation of a trigger by",
        "http://www.w3.org/ns/prov#atTime": "entails starting at",
        "http://www.w3.org/ns/prov#entity": "entails triggering by"
    },
    "http://www.w3.org/ns/prov#Usage": {
        "http://www.w3.org/ns/prov#atTime": "entails usage at",
        "http://www.w3.org/ns/prov#entity": "entails usage of"
    },
    "http://www.w3.org/ns/prov#Communication": {
        "http://www.w3.org/ns/prov#activity": "entails informing by"
    },
    "http://www.w3.org/ns/prov#Association": {
        "http://www.w3.org/ns/prov#hadPlan": "entails association planned according to",
        "http://www.w3.org/ns/prov#hadRole": "entails association as",
        "http://www.w3.org/ns/prov#agent": "entails association with"
    },
    "http://www.w3.org/ns/prov#End": {
        "http://www.w3.org/ns/prov#hadActivity": "entails generation of a trigger by",
        "http://www.w3.org/ns/prov#atTime": "entails ending at",
        "http://www.w3.org/ns/prov#entity": "entails triggering by"
    },
    "http://www.w3.org/ns/prov#Delegation": {
        "http://www.w3.org/ns/prov#hadActivity": "entails delegation of",
        "http://www.w3.org/ns/prov#agent": "entails delegation by"
    }
}

_def_binding_query = sparql.prepareQuery("""SELECT ?object ?class WHERE {
                                GRAPH <prov_graph>
                                {
                                    ?object a ?class .
                                }
                                FILTER regex( str(?class), "^http://www.w3.org/ns/prov#")}""")

def _def_binding(graph):
    results = graph.query(_def_binding_query)
    return results.bindings
    
def _def_coverage(bindings, graph):
    """Takes a single set of bindings and returns the triples that are covered by the template with those bindings."""
    rdf = rdflib.namespace.RDF    
        
    coverage_list = []
    
    # Add the type
    coverage_list.append((bindings["?object"], rdf.type, bindings["?class"]))

    # Add less specific types
    q_results = prov.fetch_less_precise_type(bindings["?object"], bindings["?class"], graph)
    for result in q_results.bindings:
        coverage_list.append((bindings["?object"], rdf.type, result["?lessPreciseType"]))

    return coverage_list


def _def_string(bindings):
    return "there is %s named <%s>.\n" % (_nl.a(classes[str(bindings["?class"])]), bindings["?object"])

_multi_prop_binding_query = sparql.prepareQuery("""
        SELECT ?thing1 ?relationship ?thing2 ?thing1_class ?thing2_class WHERE {
            GRAPH <prov_graph> {
                ?thing1 ?relationship ?thing2 .
                ?thing1 a ?thing1_class .
                ?thing2 a ?thing2_class
            }
            FILTER regex(str(?relationship), "^http://www.w3.org/ns/prov#")
        } ORDER BY ?thing1""")    
    
def _multi_prop_binding(graph):
    results = graph.query(_multi_prop_binding_query)
    raw_bindings = results.bindings

    grouped_bindings = []
    current_subject = None
    most_precise_class = None
    
    for binding in raw_bindings:
        if binding["?thing1"] != current_subject:
            if most_precise_class != None:
                grouped_bindings[-1]["?thing1_class"] = most_precise_class
            current_subject = binding["?thing1"]
            most_precise_class = None
            grouped_bindings.append({"?thing1":binding["?thing1"], 
                                     "relationships": []})
        if not prov.exists_more_precise(binding["?thing2_class"], binding["?thing2"], graph):
            rel = {"?relationship": binding["?relationship"], 
                   "?thing2": binding["?thing2"],
                   "?thing2_class": binding["?thing2_class"]}
            if rel not in grouped_bindings[-1]["relationships"]:
                grouped_bindings[-1]["relationships"].append(rel)
        if most_precise_class == None:
            most_precise_class = binding["?thing1_class"]
        elif most_precise_class != binding["?thing1_class"]:
            if most_precise_class in [res[0] for res in prov.fetch_less_precise_type(binding["?thing1"], binding["?thing1_class"], graph)]:
                most_precise_class = binding["?thing1_class"]
            
    grouped_bindings[-1]["?thing1_class"] = most_precise_class        
                                                      
    return grouped_bindings
    
def _multi_prop_coverage(bindings, graph):
    rdf = rdflib.namespace.RDF
    coverage_list = []
    
    covered_classes_dict = {}
    
    # First add the thing1 and its types
    coverage_list.append((bindings["?thing1"], rdf.type, bindings["?thing1_class"]))
    covered_classes_dict["?thing1"] = [bindings["?thing1_class"]]
    
    # Add supertypes of thing1_class:
    for supertype in prov.fetch_less_precise_type(bindings["?thing1"], bindings["?thing1_class"], graph):
        coverage_list.append((bindings["?thing1"], rdf.type, supertype[0]))
        covered_classes_dict["?thing1"].append(supertype[0])

    # Add all the relationship triples
    for rel in bindings["relationships"]:
        # The relationships themselves
        if (bindings["?thing1"], rel["?relationship"], rel["?thing2"]) not in coverage_list:
            coverage_list.append((bindings["?thing1"], rel["?relationship"], rel["?thing2"]))
        
        # And all the classes of the thing2s
        triple = (rel["?thing2"], rdf.type, rel["?thing2_class"])
        if triple not in coverage_list:
            coverage_list.append(triple)
        for superclass in prov.fetch_less_precise_type(rel["?thing2"], rel["?thing2_class"], graph):
            triple = (rel["?thing2"], rdf.type, superclass[0])
            if triple not in coverage_list:
                coverage_list.append(triple)
            
    return coverage_list

def _multi_prop_string(bindings):
    thing1 = bindings["?thing1"]
    thing1_class = classes[str(bindings["?thing1_class"])]
    
    sentence = "the %s <%s>" % (thing1_class, thing1)
    
    rel_strings = []
    for rel in bindings["relationships"]:
        thing2 = rel["?thing2"]
        thing2_class = classes[str(rel["?thing2_class"])]
        if str(rel["?relationship"]) in simple_predicates:
            relationship = simple_predicates[str(rel["?relationship"])]
        else:
            relationship = qualified_predicates[str(bindings["?thing1_class"])][str(rel["?relationship"])]
        rel_strings.append("\n\t%s the %s <%s>" % (relationship, thing2_class, thing2))
        
    for rel in rel_strings[:-1]:
        sentence += rel + " and"
        
    sentence += rel_strings[-1] + ".\n"
    
    return sentence

templates = [transform.Template("CE Definitions", _def_binding, _def_coverage, _def_string),
             transform.Template("CE Multi", _multi_prop_binding, _multi_prop_coverage, _multi_prop_string)]

transformer = transform.Transformer()
for template in templates:
    transformer.register_template(template)
