import unittest, rdflib
from helper_funcs import load_fixture

class Check_PROV_graph_not_empty(unittest.TestCase):
    def test(self):
        import provglish.prov as prov
        graph = rdflib.graph.ConjunctiveGraph()
        prov.load_prov_ontology(graph)
        self.assertNotEqual(len(graph),0)

class Check_that_exception_thrown_if_query_before_init(unittest.TestCase):
    def test(self):
        import provglish.prov as prov
        reload(prov)
        graph = rdflib.graph.ConjunctiveGraph()
        graph = load_fixture("bravo.ttl")
        self.assertRaises(prov.QueriesNotInitedError, prov.fetch_all_alternates, [graph])
        
    def test_to_string(self):
        import provglish.prov as prov
        reload(prov)
        x = prov.QueriesNotInitedError()
        self.assertEqual(str(x), repr("prov.query_init() not executed before attempting to query"))

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
        graph = load_fixture("bravo.ttl")
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)
        results = prov.fetch_less_precise_type(rdflib.URIRef("https://example.net/#ingredients"),rdflib.URIRef("http://www.w3.org/ns/prov#Collection"), graph)
        types = list(results)
        self.assertEqual(len(types), 1)
        self.assertEqual(len(types[0]), 1)
        self.assertEqual(types[0][0], rdflib.URIRef("http://www.w3.org/ns/prov#Entity"))
        
    def test_property(self):
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("bravo-influence.ttl")
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)
        results = prov.fetch_less_precise_prop(rdflib.URIRef("https://example.net/#cake"),
                                               rdflib.URIRef("http://www.w3.org/ns/prov#qualifiedDerivation"),
                                               rdflib.URIRef("https://example.net/#deriv"),
                                               graph)
        props = list(results)
        self.assertEqual(len(props), 1)
        self.assertEqual(len(props[0]), 1)
        self.assertEqual(props[0][0], rdflib.URIRef("http://www.w3.org/ns/prov#qualifiedInfluence"))

class Check_prov_exists_more_precise(unittest.TestCase):
    def test(self):
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("bravo.ttl")
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)
        self.assertTrue(prov.exists_more_precise(rdflib.URIRef("http://www.w3.org/ns/prov#Entity"),
                                                 rdflib.URIRef("https://example.net/#ingredients"),
                                                 graph))
        self.assertFalse(prov.exists_more_precise(rdflib.URIRef("http://www.w3.org/ns/prov#Collection"),
                                                  rdflib.URIRef("https://example.net/#ingredients"),
                                                  graph))

class Check_alternates(unittest.TestCase):
    def test_all(self):
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("charlie.ttl")
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)
        
        self.assertEqual(len(prov.fetch_all_alternates(graph)), 9)
        
    def test_groups(self):
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("charlie.ttl")
        self.assertNotEqual(len(graph),0)
        prov.load_prov_ontology(graph)
        
        groups = prov.fetch_all_alternate_groups(graph)
        self.assertEqual(len(groups), 3)
        for group in groups:
            self.assertEqual(len(group), 3)

    def test_related(self):
        from rdflib import URIRef
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("charlie.ttl")
        self.assertNotEqual(len(graph),0)
        prov.load_prov_ontology(graph)

        alternates = prov.fetch_related_alternates(graph, "https://example.net/#bravo")
        self.assertEqual(len(alternates),3)
        self.assertTrue(URIRef("https://example.net/#bravo") in alternates)
        self.assertTrue(URIRef("https://example.net/#bravo-1") in alternates)
        self.assertTrue(URIRef("https://example.net/#bravo-2") in alternates)

        alternates = prov.fetch_related_alternates(graph, URIRef("https://example.net/#alpha"))
        self.assertEqual(len(alternates),3)
        self.assertTrue(URIRef("https://example.net/#alpha") in alternates)
        self.assertTrue(URIRef("https://example.net/#alpha-1") in alternates)
        self.assertTrue(URIRef("https://example.net/#alpha-2") in alternates)

        alternates = prov.fetch_related_alternates(graph, "https://example.net/NOT_A_VALID_URI")
        self.assertEqual(len(alternates),1)

class Check_fetch_all_prov_things(unittest.TestCase):
    def test(self):
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("bravo.ttl")
        self.assertNotEqual(len(graph),0)
        prov.load_prov_ontology(graph)

        things = prov.fetch_all_prov_things(graph)
        self.assertEqual(len(things), 7)

        graph = load_fixture("charlie.ttl")
        self.assertNotEqual(len(graph),0)
        prov.load_prov_ontology(graph)

        things = prov.fetch_all_prov_things(graph)
        self.assertEqual(len(things), 9) 

class Check_fetch_all_agents(unittest.TestCase):
    def test(self):
        from rdflib import URIRef
        import provglish.prov as prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("charlie.ttl")
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)

        agents = prov.fetch_all_agents(graph)
        self.assertEqual(len(agents), 3)
        self.assertTrue(URIRef("https://example.net/#alpha") in agents)
        self.assertTrue(URIRef("https://example.net/#bravo") in agents)
        self.assertTrue(URIRef("https://example.net/#charlie") in agents)
