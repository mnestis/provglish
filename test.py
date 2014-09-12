#!/usr/bin/python
from rdflib.graph import ConjunctiveGraph
from provglish import prov

g = ConjunctiveGraph()
prov.query_init()
prov.load_prov_ontology(g)

print "Loaded PROV ontology."

print "Parsing provenance graph..."
#g.parse("https://provenance.ecs.soton.ac.uk/store/documents/10148.ttl", format="turtle", publicID="prov_graph")
#g.parse("https://provenance.ecs.soton.ac.uk/store/documents/10064.ttl", format="turtle", publicID="prov_graph")
g.parse("https://provenance.ecs.soton.ac.uk/store/documents/28279.ttl", format="turtle", publicID="prov_graph")

print "\tDone."

print "The combined graph consists of %s triples." % (len(g),)

print "There are %s entities that are alternates of other entities." % (len(prov.fetch_all_alternates(g)))

groups = prov.fetch_all_alternate_groups(g)

print "These cluster into %s groups of entities that are alternates of one another." % (len(groups))
