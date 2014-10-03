import unittest

class Check_urn_extraction(unittest.TestCase):
    def test(self):
        from provglish.lexicalisation import urn_from_uri
        from rdflib import URIRef

        self.assertEqual(urn_from_uri("https://example.net/food/cake/cheesecake"), "cheesecake")
        self.assertEqual(urn_from_uri("https://example.net/food/cake#cheesecake"), "cheesecake")
        self.assertEqual(urn_from_uri("https://example.net/food#cake/cheesecake"), "cheesecake")
        self.assertEqual(urn_from_uri(URIRef("https://example.net/food/cake/cheesecake")), "cheesecake")

class Check_plural_p(unittest.TestCase):
    def test(self):
        from provglish.lexicalisation import plural_p

        self.assertTrue(plural_p("cats"))
        self.assertTrue(plural_p("trees"))
        self.assertFalse(plural_p("swimming"))
        self.assertFalse(plural_p("cat"))
        self.assertFalse(plural_p("tree"))
