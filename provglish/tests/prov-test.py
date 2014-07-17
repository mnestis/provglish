import unittest, rdflib
from helper_funcs import load_bravo

class Check_PROV_graph_not_empty(unittest.TestCase):
    def test(self):
        import provglish.prov as prov
        graph = rdflib.graph.ConjunctiveGraph()
        prov.load_prov_ontology(graph)
        self.assertNotEqual(len(graph),0)
        
class Check_that_prov_queries_not_populated_before_init(unittest.TestCase):
    def test(self):
        import provglish.prov as prov
        reload(prov)
        self.assertEqual(len(prov._queries), 0)

class Check_that_prov_queries_are_populated_after_init(unittest.TestCase):
    def test(self):
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        self.assertNotEqual(len(prov._queries), 0)
        
class Check_prov_fetch_less_precise(unittest.TestCase):
    def test_type(self):
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_bravo()
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)
        results = prov.fetch_less_precise_type(rdflib.URIRef("https://example.net/#ingredients"),rdflib.URIRef("http://www.w3.org/ns/prov#Collection"), graph)
        types = list(results)
        self.assertEqual(len(types), 1)
        self.assertEqual(len(types[0]), 1)
        self.assertEqual(types[0][0], rdflib.URIRef("http://www.w3.org/ns/prov#Entity"))
        
    def test_property(self):
        pass
