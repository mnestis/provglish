import unittest

class NoNlgServTest(unittest.TestCase):
    def test(self):
        """
        Not entirely sure this test will always pass. It relies on the fact that
        the nlgserv server *should* not be running at this point in the test script.
        
        However, it is conceivable that this might be the case, unfortunately, I can't
        think of an easy way of preventing this, and yet to have the test still be effective.
        """
        from provglish.nl.tools import realise_sentence, RealisationException

        sentence = {"sentence": {"subject": "John",
                                 "verb": "love",
                                 "object": "cake"}}

        self.assertRaises(RealisationException, realise_sentence, sentence)
