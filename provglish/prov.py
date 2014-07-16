import rdflib, os
from rdflib.plugins import sparql

_queries = {}
_inited = False

def query_init():
    _queries["less_precise_type"] = sparql.prepareQuery(
        """SELECT ?lessPreciseType WHERE {
            GRAPH <prov_graph> {
                ?thing a ?thing_class .
                ?thing a ?lessPreciseType
            }
            ?thing_class <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?lessPreciseType
        }"""
    )

    _queries["less_precise_prop"] = sparql.prepareQuery(
        """SELECT ?lessPreciseProp WHERE {
            GRAPH <prov_graph> {
                ?thing1 ?prop ?thing2 .
                ?thing1 ?lessPreciseProp ?thing2
            }
            ?prop <http://www.w3.org/2000/01/rdf-schema#subPropertyOf>+ ?lessPreciseProp
        }"""
    )
    
    _queries["exists_more_precise"] = sparql.prepareQuery(
        """ASK { 
            GRAPH <prov_graph> {
                ?thing a ?morePreciseClass
            }
            ?morePreciseClass <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?class .
        }"""
    )
  
    _inited = True

def load_prov_ontology(graph):
    graph.parse(os.path.dirname(__file__)+"/prov.owl",format="xml")
    return graph

def fetch_less_precise_type(thing, thing_class, graph):
    return graph.query(_queries["less_precise_type"], initBindings={"thing": thing, "thing_class": thing_class})

def fetch_less_precise_prop(thing1, prop, thing2, graph):
    return graph.query(_queries["less_precise_prop"], initBindings={"thing1": thing1, "thing2": thing2, "prop": prop})

def exists_more_precise(class_URI, subject_URI, graph):
    result = graph.query(_queries["exists_more_precise"], initBindings={"thing": subject_URI, "class": class_URI})
    return result.askAnswer
    
def root_things(graph):
    roots = graph.query("SELECT DISTINCT ?thing WHERE { ?thing ?x ?y . FILTER NOT EXISTS { ?a ?b ?thing }}")
    return list([root[0] for root in roots])
