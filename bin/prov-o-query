#!/usr/bin/python

import rdflib

g = rdflib.Graph()
g.parse("http://www.w3.org/ns/prov.owl", format="xml")

from sys import argv

query_string = reduce(lambda a, b: a+b, argv[1:], "")
print query_string

results = g.query("""
                    SELECT DISTINCT ?prov WHERE
                        {
                            ?prov ?p ?o .
                            FILTER regex(str(?prov), "^http://www.w3.org/ns/prov#") .
                            FILTER regex(str(?prov), "%s")
                        } ORDER BY str(?prov)
                    """ % (query_string))
                    
for result in results:
    print "\n\n\nThere is a term <%s>\n" % result[0]
    relationships = g.query("""
                                SELECT DISTINCT ?predicate ?object WHERE
                                    {
                                        <%s> ?predicate ?object
                                    } ORDER BY str(?predicate)
                            """ % (result[0],))
    for relationship in relationships:
        print "\t%s %s" % (relationship[0], relationship[1])
