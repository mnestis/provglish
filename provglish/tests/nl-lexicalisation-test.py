import unittest
from rdflib import URIRef

class Check_uri_tokenisation(unittest.TestCase):
    def test(self):
        from provglish.nl.lexicalisation import tokenise_uri
    
        #Basic tests
        self.assertEqual(tokenise_uri("https://example.net/food/cake/cheesecake"), ["food", "cake", "cheesecake"])
        self.assertEqual(tokenise_uri("https://example.net/food/cake#cheesecake"), ["food", "cake", "cheesecake"])
        self.assertEqual(tokenise_uri("https://example.net/food#cake/cheesecake"), ["food", "cake", "cheesecake"])
        self.assertEqual(tokenise_uri("https://example.net/food?cake=cheesecake"), ["food", "cake", "cheesecake"])
        self.assertEqual(tokenise_uri(URIRef("https://example.net/food/cake/cheesecake")), ["food", "cake", "cheesecake"])

        # Testing interesting features
        
        self.assertEqual(tokenise_uri("https://example.net/people/ClayMcFarlen"), ["people", "Clay", "McFarlen"])
        self.assertEqual(tokenise_uri("https://example.net/giveFeedback"), ["give", "Feedback"])
        self.assertEqual(tokenise_uri("https://example.net/understanding_URITokenisation"), ["understanding", "URI", "Tokenisation"])

class Check_stubs(unittest.TestCase):
    def test(self):

        from provglish.nl.lexicalisation import entity_uri_to_noun_phrase_spec
        from provglish.nl.lexicalisation import activity_uri_to_verb_phrase_spec

        self.assertRaises(NotImplementedError, entity_uri_to_noun_phrase_spec, "https://example.net/fishing")
        self.assertRaises(NotImplementedError, activity_uri_to_verb_phrase_spec, "https://example.net/fishing")
