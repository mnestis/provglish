#!/usr/bin/python
import rdflib
import sys
from provglish import prov

graph = rdflib.graph.ConjunctiveGraph()
prov.load_prov_ontology(graph)
prov.init()

sys.exit()
