import re
import nltk

def urn_from_uri(uri):
    """
    This function returns everything that comes after the last # or / in a 
    string.

    It casts to a string first, in case it is passed a class that models URIs,
    but need to be made strings before they'll have a string method available.
    """
    return re.split("[#/]", str(uri))[-1]

def plural_p(word):
    """
    This function is really messy, and there is probably a better, more reliable
    way to do this. Basically, it's using a POS tagger to tag a single word.

    (The POS tagger is designed to work on sentences rather than single words,
    however performance isn't actually terrible here, surprisingly)

    If that tag is NNS or NNPS, then it is a plural.
    """
    return re.match("NNP?S", nltk.pos_tag([word])[0][1])
