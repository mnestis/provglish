#!/usr/bin/python

import rdflib
from provglish import transform
from provglish import prov

from random import randint

graph = rdflib.graph.ConjunctiveGraph()
graph.parse("bravo.ttl",format="turtle", publicID="prov_graph")
prov.load_prov_ontology(graph)

tran = transform.Transformer()
tran.register_template(transform.definitions)
tran.register_template(transform.properties)
tran.register_template(transform.two_props)
sentences = tran.render_graph(graph)

hashes = {}
for sentence in sentences:
    if sentence.coverage_hash not in hashes:
        hashes[sentence.coverage_hash] = [sentence]
    else:
        hashes[sentence.coverage_hash].append(sentence)
        
for key in hashes:
    print "The hash %s is matched by ^^%s^^ sentences" % (key, len(hashes[key]))
    hashes[key] = hashes[key][randint(0, len(hashes[key])-1)]

for key in hashes:
    print hashes[key]

coverage = {}
for key in hashes:
    for triple in hashes[key].coverage:
        if triple not in coverage:
            coverage[triple] = 1
        else:
            coverage[triple] += 1

for key in coverage:
    print "This is covered by %s sentences:\n%s" % (coverage[key], key)
