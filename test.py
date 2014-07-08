#!/usr/bin/python

import rdflib
from provglish import transform
from provglish import prov

graph = rdflib.graph.ConjunctiveGraph()
graph.parse("bravo.ttl",format="turtle", publicID="prov_graph")
prov.load_prov_ontology(graph)

for sentence in transform.definitions.generate_sentences(graph):
    print sentence
    
for sentence in transform.properties.generate_sentences(graph):
    print sentence
    
for sentence in transform.two_props.generate_sentences(graph):
    print sentence

