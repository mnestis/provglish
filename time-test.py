#!/usr/bin/python
import rdflib
import sys
from provglish import prov
from provglish import transform

graph = rdflib.graph.ConjunctiveGraph()
prov.load_prov_ontology(graph)
prov.init()

sys.exit()
