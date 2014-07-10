import rdflib, os
from rdflib.plugins import sparql

_less_precise_type_query = sparql.prepareQuery(
    """SELECT ?lessPreciseType WHERE {
        GRAPH <prov_graph> {
            ?thing a ?thing_class .
            ?thing a ?lessPreciseType
        }
        ?thing_class <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?lessPreciseType
    }"""
)

_less_precise_prop_query = sparql.prepareQuery(
    """SELECT ?lessPreciseProp WHERE {
        GRAPH <prov_graph> {
            ?thing1 ?prop ?thing2 .
            ?thing1 ?lessPreciseProp ?thing2
        }
        ?prop <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> ?lessPreciseProp
    }"""
)

def load_prov_ontology(graph):
    graph.parse(os.path.dirname(__file__)+"/prov.owl",format="xml")
    return graph

def fetch_less_precise_type(thing, thing_class, graph):
    return graph.query(_less_precise_type_query, initBindings={"thing": thing, "thing_class": thing_class})

def fetch_less_precise_prop(thing1, prop, thing2, graph):
    return graph.query(_less_precise_prop_query, initBindings={"thing1": thing1, "thing2": thing2, "prop": prop})

def exists_more_precise(class_URI, subject_URI, graph):
    if graph.query("""SELECT ?morePreciseClass WHERE 
                                    { 
                                        ?morePreciseClass <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ <%s> .
                                        <%s> a ?morePreciseClass
                                    }""" % (class_URI, subject_URI)):
        return True
    else:
        return False

def root_things(graph):
    roots = graph.query("SELECT DISTINCT ?thing WHERE { ?thing ?x ?y . FILTER NOT EXISTS { ?a ?b ?thing }}")
    return list([root[0] for root in roots])
