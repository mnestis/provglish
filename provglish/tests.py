import unittest

class Check_PROV_graph_not_empty(unittest.TestCase):
    def test(self):
        import prov, rdflib
        graph = rdflib.graph.ConjunctiveGraph()
        prov.load_prov_ontology(graph)
        self.assertNotEqual(len(graph),0)

class Check_that_prov_queries_not_populated_before_init(unittest.TestCase):
    def test(self):
        import prov
        reload(prov)
        self.assertEqual(len(prov._queries), 0)
        
class Check_that_prov_queries_are_populated_after_init(unittest.TestCase):
    def test(self):
        import prov
        reload(prov)
        prov.query_init()
        self.assertNotEqual(len(prov._queries), 0)
