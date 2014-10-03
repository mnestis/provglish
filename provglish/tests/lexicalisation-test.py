import unittest

class Check_urn_extraction(unittest.TestCase):
    def test(self):
        from provglish.lexicalisation import urn_from_uri
        from rdflib import URIRef

        self.assertEqual(urn_from_uri("https://example.net/food/cake/cheesecake"), "cheesecake")
        self.assertEqual(urn_from_uri("https://example.net/food/cake#cheesecake"), "cheesecake")
        self.assertEqual(urn_from_uri("https://example.net/food#cake/cheesecake"), "cheesecake")
        self.assertEqual(urn_from_uri(URIRef("https://example.net/food/cake/cheesecake")), "cheesecake")
