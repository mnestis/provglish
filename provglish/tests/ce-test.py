import unittest
from helper_funcs import load_fixture
import rdflib

class Check_multi_prop_binding_function(unittest.TestCase):
    def test_count(self):
        """
        This simply checks that the binding function returns an object that has the right length.
        """
        import provglish.ce as ce
        import provglish.prov as prov
        graph = load_fixture("bravo.ttl")
        self.assertNotEqual(len(graph), 0)
        prov.load_prov_ontology(graph)
        results = ce._multi_prop_binding(graph)

        self.assertEqual(len(results), 3) # Three subjects, cake, ingredients, and deriv.
        
        for result in results:
            if result["?thing1"] == rdflib.URIRef("https://example.net/#cake"):
                self.assertEqual(len(result["relationships"]), 1) # derived according to deriv
            elif result["?thing1"] == rdflib.URIRef("https://example.net/#deriv"):
                print result["relationships"]
                self.assertEqual(len(result["relationships"]), 2) # derived from ingredients, by baking
            elif result["?thing1"] == rdflib.URIRef("https://example.net/#ingredients"):
                self.assertEqual(len(result["relationships"]), 4) # had member, ent/coll flour egg sugar butter.
            else:
                self.fail()
                
class Check_multi_prop_coverage_function(unittest.TestCase):
    def test_bravo_cake_count(self):
        import provglish.ce as ce
        import provglish.prov as prov
        graph = load_fixture("bravo.ttl")
        prov.load_prov_ontology(graph)
        
        binding = ce._multi_prop_binding(graph)[0]
        # We expect the results to be ordered -- perhaps this warrants its own test.
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#cake"))
        
        coverage = ce._multi_prop_coverage(binding, graph)
        
        self.assertEqual(len(coverage),3) # cake->Entity, cake->Derived, deriv->Derivation

    def test_bravo_deriv_count(self):
        import provglish.ce as ce
        import provglish.prov as prov
        graph = load_fixture("bravo.ttl")
        prov.load_prov_ontology(graph)
        
        binding = ce._multi_prop_binding(graph)[1]
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#deriv"))
        
        coverage = ce._multi_prop_coverage(binding, graph)
        self.assertEqual(len(coverage), 6)
        
    def test_bravo_ingredients_count(self):
        import provglish.ce as ce
        import provglish.prov as prov
        graph = load_fixture("bravo.ttl")
        prov.load_prov_ontology(graph)
        
        binding = ce._multi_prop_binding(graph)[2]
        self.assertEqual(binding["?thing1"], rdflib.URIRef("https://example.net/#ingredients"))
        self.assertEqual(binding["?thing1_class"], rdflib.URIRef("http://www.w3.org/ns/prov#Collection"))
        
        coverage = ce._multi_prop_coverage(binding, graph)
        self.assertEqual(len(coverage), 10)
        
class Check_multi_prop_string_function(unittest.TestCase):
    def test_cake(self):
        import provglish.ce as ce
        import provglish.prov as prov
        graph = load_fixture("bravo.ttl")
        prov.load_prov_ontology(graph)
        
        bindings = ce._multi_prop_binding(graph)
        for binding in bindings:
            sentence = ce._multi_prop_string(binding, {})
        # We're not going to actually test the string itself, but assume that if there's no exception, it's worked.
        
