import unittest, os, rdflib

def load_bravo():
    graph = rdflib.graph.ConjunctiveGraph()
    graph.parse(os.path.join(os.path.dirname(__file__), "test_fixtures/bravo.ttl"), format="turtle", publicID="prov_graph")
    return graph

class Check_PROV_graph_not_empty(unittest.TestCase):
    def test(self):
        import prov
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

class Check_prov_fetch_less_precise(unittest.TestCase):
    def test_type(self):
        import prov
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


class Check_multi_prop_binding_function(unittest.TestCase):
    def test_count(self):
        """
        This simply checks that the binding function returns an object that has the right length.
        """
        import transform, prov
        reload(transform)
        graph = load_bravo()
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)
        results = transform.multi_prop_binding(graph)

        self.assertEqual(len(results), 3) # Three subjects, cake, ingredients, and deriv.
        
        for result in results:
            if result["?thing1"] == rdflib.URIRef("https://example.net/#cake"):
                self.assertEqual(len(result["relationships"]), 1) # derived according to deriv
            elif result["?thing1"] == rdflib.URIRef("https://example.net/#deriv"):
                print result["relationships"]
                self.assertEqual(len(result["relationships"]), 3) # derived from ent/coll ingredients, by baking
            elif result["?thing1"] == rdflib.URIRef("https://example.net/#ingredients"):
                self.assertEqual(len(result["relationships"]), 8) # had member, ent/coll flour egg sugar butter.
            else:
                self.fail()
                
class Check_multi_prop_coverage_function(unittest.TestCase):
    def test_bravo_cake_count(self):
        import transform, prov
        reload(transform)
        graph = load_bravo()
        prov.load_prov_ontology(graph)
        
        binding = transform.multi_prop_binding(graph)[0]
        # We expect the results to be ordered -- perhaps this warrants its own test.
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#cake"))
        
        coverage = transform.multi_prop_coverage(binding, graph)
        
        self.assertEqual(len(coverage),3) # cake->Entity, cake->Derived, deriv->Derivation

    def test_bravo_deriv_count(self):
        import transform, prov
        reload(transform)
        graph = load_bravo()
        prov.load_prov_ontology(graph)
        
        binding = transform.multi_prop_binding(graph)[1]
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#deriv"))
        
        coverage = transform.multi_prop_coverage(binding, graph)
        self.assertEqual(len(coverage), 6)
        
    def test_bravo_ingredients_count(self):
        import transform, prov
        reload(transform)
        graph = load_bravo()
        prov.load_prov_ontology(graph)
        
        binding = transform.multi_prop_binding(graph)[2]
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#ingredients"))
        
        coverage = transform.multi_prop_coverage(binding, graph)
        self.assertEqual(len(coverage), 10)
