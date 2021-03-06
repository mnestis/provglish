from helper_funcs import load_fixture
import unittest, rdflib
        
class Check_Transformer(unittest.TestCase):
    def test(self):
        from provglish import transform
        from provglish import ce
        reload(transform)
        transformer = transform.Transformer()
        self.assertEqual(len(transformer._registered_templates), 0)
        transformer.register_template(ce.templates[0])
        self.assertEqual(len(transformer._registered_templates), 1)
        
        from provglish import prov
        reload(prov)
        prov.query_init()
        graph = load_fixture("bravo.ttl")
        prov.load_prov_ontology(graph)
        
        sentences = transformer.render_graph(graph)
        self.assertEqual(len(sentences), 9)
        
class Check_Transformer_transform(unittest.TestCase):
    def test(self):
        from provglish import ce
        graph = load_fixture("bravo.ttl")
        ce.transformer.register_template(ce.templates[1])
        sentences = ce.transformer.transform(graph)
        self.assertEqual(len(sentences), 3)

class Check_Template_str(unittest.TestCase):
    def test(self):
        from provglish import transform
        from provglish import ce
        self.assertEqual(str(ce.templates[0]), "CE Definitions")

class Check_sentence_init(unittest.TestCase):
    def test(self):
        from provglish import transform
        s = transform.Sentence(lambda x, y: "This is a string", ((1,2,3),(4,5,6)), None)
        self.assertEqual(str(s),"This is a string")
        self.assertEqual(s.coverage_hash, hash(((1,2,3),(4,5,6))))

class Check_Sentence_order_triples(unittest.TestCase):
    def test(self):
        from provglish import transform
        ot = transform.Sentence._order_triples
        self.assertEqual(ot((0,0,0),(0,0,0)), 0)
        self.assertEqual(ot((0,0,0),(0,0,1)), -1)
        self.assertEqual(ot((0,0,1),(0,0,0)), 1)
        self.assertEqual(ot((0,0,1),(0,1,0)), -1)
        self.assertEqual(ot((0,1,0),(0,0,1)), 1)
        self.assertEqual(ot((0,1,0),(1,0,0)), -1)
        self.assertEqual(ot((1,0,0),(0,1,0)), 1)

class Check_sentence_string_with_history(unittest.TestCase):
    def test(self):
        from provglish import transform
        
        def generate_string(bindings, history):
            if "test" in history:
                return "The string is %s." % (history["test"])
            else:
                return "This isn't the string you're looking for."

        sentence = transform.Sentence(generate_string, [], {})

        self.assertEqual(str(sentence), "This isn't the string you're looking for.")
        self.assertEqual(sentence.generate_string({}), "This isn't the string you're looking for.")
        self.assertEqual(sentence.generate_string({"test": "working"}), "The string is working.")
