import rdflib

prov_graph = rdflib.Graph()
prov_graph.parse("http://www.w3.org/ns/prov.owl", format="xml")

def exists_more_precise(class_URI, subject_URI, graph):
    if (prov_graph + graph).query("""SELECT ?morePreciseClass WHERE 
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
