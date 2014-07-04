#!/usr/bin/python

import rdflib
from provglish import transform
from provglish import prov

graph = rdflib.graph.ConjunctiveGraph()
graph.parse("bravo.ttl",format="turtle", publicID="prov_graph")
prov.load_prov_ontology(graph)

bindings = transform.definitions.bindings(graph)
for binding in bindings:
    print transform.definitions.make_string(binding)
    triples = transform.definitions.coverage(binding, graph)
    for triple in triples:
        print "\t(%s, %s, %s)" % triple
        
print "\n\n"

bindings = transform.properties.bindings(graph)
for binding in bindings:
    print transform.properties.make_string(binding)
    triples = transform.properties.coverage(binding, graph)
    for triple in triples:
        print "\t(%s, %s, %s)" % triple
