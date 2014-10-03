import re

def urn_from_uri(uri):
    """
    This function returns everything that comes after the last # or / in a 
    string.

    It casts to a string first, in case it is passed a class that models URIs,
    but need to be made strings before they'll have a string method available.
    """
    return re.split("[#/]", str(uri))[-1]
