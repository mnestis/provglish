import re
import urlparse

def tokenise_uri(uri):
    parsed_uri = urlparse.urlsplit(uri)

    # We only care about the path and the fragment (and very occasionally the query)
    # We'll call it all the path to save typing
    path = parsed_uri.path
    if parsed_uri.query != "":
        path += "?" + parsed_uri.query
    if parsed_uri.fragment != "":
        path += "#" + parsed_uri.fragment

    return re.findall("[0-9a-fA-F]{10,}|API|(?:Mc|Mac)?[A-Z][a-z]+|[A-Z]+s?(?![a-z])|[a-z]+|[0-9]+", path)

def entity_uri_to_noun_phrase_spec(uri):
    raise NotImplementedError()

def activity_uri_to_verb_phrase_spec(uri):
    raise NotImplementedError()
