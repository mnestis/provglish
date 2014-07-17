from helper_funcs import load_bravo, load_fixture
import unittest, rdflib
        
class Check_Transformer(unittest.TestCase):
    def test(self):
        from provglish import transform
        transformer = transform.Transformer()
        self.assertEqual(len(transformer._registered_templates), 0)
        transformer.register_template(transform.definitions)
        self.assertEqual(len(transformer._registered_templates), 1)
        
        from provglish import prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("bravo.ttl")
        prov.load_prov_ontology(graph)
        
        sentences = transformer.render_graph(graph)
        self.assertEqual(len(sentences), 9)
        
class Check_Template_str(unittest.TestCase):
    def test(self):
        from provglish import transform
        self.assertEqual(str(transform.definitions), "CE Definitions")

class Check_multi_prop_binding_function(unittest.TestCase):
    def test_count(self):
        """
        This simply checks that the binding function returns an object that has the right length.
        """
        import provglish.transform as transform
        import provglish.prov as prov
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
        import provglish.transform as transform
        import provglish.prov as prov
        reload(transform)
        graph = load_bravo()
        prov.load_prov_ontology(graph)
        
        binding = transform.multi_prop_binding(graph)[0]
        # We expect the results to be ordered -- perhaps this warrants its own test.
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#cake"))
        
        coverage = transform.multi_prop_coverage(binding, graph)
        
        self.assertEqual(len(coverage),3) # cake->Entity, cake->Derived, deriv->Derivation

    def test_bravo_deriv_count(self):
        import provglish.transform as transform
        import provglish.prov as prov
        reload(transform)
        graph = load_bravo()
        prov.load_prov_ontology(graph)
        
        binding = transform.multi_prop_binding(graph)[1]
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#deriv"))
        
        coverage = transform.multi_prop_coverage(binding, graph)
        self.assertEqual(len(coverage), 6)
        
    def test_bravo_ingredients_count(self):
        import provglish.transform as transform
        import provglish.prov as prov
        reload(transform)
        graph = load_bravo()
        prov.load_prov_ontology(graph)
        
        binding = transform.multi_prop_binding(graph)[2]
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#ingredients"))
        self.assertEqual(binding["?thing1_class"], rdflib.URIRef("http://www.w3.org/ns/prov#Collection"))
        
        coverage = transform.multi_prop_coverage(binding, graph)
        self.assertEqual(len(coverage), 10)
