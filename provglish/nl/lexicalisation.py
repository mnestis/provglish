import re
import urlparse

from nltk import load
tagger = load("taggers/maxent_treebank_pos_tagger/english.pickle")
pos_tag = tagger.tag

def tokenise_uri_part(uri_part):
    tokens = re.findall("[0-9a-fA-F]{10,}|API|(?:Mc|Mac)?[A-Z][a-z]+|[A-Z]+s?(?![a-z])|[a-z]+|[0-9]+", uri_part)
    return list([token.lower() for token in tokens])

def get_uri_parts(uri):
    parsed_uri = urlparse.urlsplit(uri)
    
    split_path = parsed_uri.path.strip("/").split("/")
    if parsed_uri.query != "":
        split_path.append(parsed_uri.query)
    if parsed_uri.fragment != "":
        split_path.append(parsed_uri.fragment)

    return split_path

def agent_uri_to_noun_phrase_spec(uri):
    return entity_uri_to_noun_phrase_spec(uri)

def extract_noun_components(part_tokens, part_tags):
    head_noun = []
    for noun_index, tag in enumerate(reversed(part_tags)):
        if tag == "NN" or \
           tag == "NNS" or \
           tag == "NNP" or \
           tag == "NNPS" or \
           tag == "CD" or \
           tag == "-NONE-" or \
           tag == "LS":
            head_noun.insert(0, part_tokens[-(noun_index+1)])
        else:
            break
            
    modifiers = []
    for mod_index, tag in enumerate(reversed(part_tags[:-noun_index])):
        if tag == "JJ" or \
           tag == "JJR" or \
           tag == "JJS" or \
           tag == "VBD" or \
           tag == "VBN": # These last ones are a bit of a fudge...
            modifiers.insert(0, part_tokens[-(noun_index + mod_index+1)])
        else:
            break
                
    return head_noun, modifiers


def entity_uri_to_noun_phrase_spec(uri):
    uri_parts = get_uri_parts(uri)

    if len(uri_parts) < 1:
        return uri
    
    last_part_tokens = tokenise_uri_part(uri_parts[-1])
    if len(uri_parts) > 1:
        penultimate_part_tokens = tokenise_uri_part(uri_parts[-2])
    else:
        penultimate_part_tokens = []
    
    last_POSed = pos_tag(last_part_tokens)
    pen_POSed = pos_tag(penultimate_part_tokens)

    if len(last_POSed) > 0:
        last_tokens, last_tags = zip(*pos_tag(last_part_tokens))
    else:
        last_tokens = []
        last_tags = []

    if len(pen_POSed) > 0:
        pen_tokens, pen_tags = zip(*pos_tag(penultimate_part_tokens))
    else:
        pen_tokens = []
        pen_tags = []

    # First try and find a noun in the last part of the URI
    if last_tags.count("NN") + \
       last_tags.count("NNS") + \
       last_tags.count("NNP") + \
       last_tags.count("NNPS") > 0:
        # the head is all the elements from the end that are:
        ## NN, NNS, NNP, NNPS, CD, -NONE-
        head_noun, modifiers = extract_noun_components(last_tokens, last_tags)
        
        locations  = []
        if "NN" in last_tags:
            locations.append(("NN", last_tags.index("NN")))
        if "NNS" in last_tags:
            locations.append(("NNS", last_tags.index("NNS")))
        if "NNP" in last_tags:
            locations.append(("NNP", last_tags.index("NNP")))
        if "NNPS" in last_tags:
            locations.appedn(("NNPS", last_tags.index("NNPS")))

        if len(locations) > 0:
            locations.sort(key=lambda x: x[1])
            if locations[-1][0] == "NNS" or locations[-1][0] == "NNPS":
                plural = True
            else:
                plural = False
        else:
            plural = False


    # If there's only a number there, try the part before last.
    elif ("CD" in last_tags or \
          "-NONE-" in last_tags or \
          "LS" in last_tags) and \
         ("NN" in pen_tags or \
          "NNP" in pen_tags or \
          "NNPS" in pen_tags or \
          "NNS" in pen_tags):
        head_noun, modifiers = extract_noun_components(pen_tokens, pen_tags)
        head_noun.extend(last_tokens)
        plural = False

    else:
        return uri_parts[-1]

    mod_string = reduce(lambda a, b: a + " " + b, modifiers, "").lower()
    head_noun_string = reduce(lambda a, b: a + " " + b, head_noun, "").lower()

    spec = {"type": "noun_phrase",
            "head": head_noun_string,
            "modifiers": [mod_string],
            "features": {"number": "plural" if plural else "singular"}}

    return spec

def uri_contains_verb(uri):
    parts = get_uri_parts(uri)

    if len(parts) == 0:
        return False
    
    tokens = tokenise_uri_part(parts[-1])
    tokens.insert(0, "I") # Horrible fudge to coerce the thing to work
    if len(tokens) != 0:
        tokens, tags = zip(*pos_tag(tokens))
    else:
        tags = []

    if "VB" in tags or \
       "VBD" in tags or \
       "VBG" in tags or \
       "VBN" in tags or \
       "VBP" in tags or \
       "VBZ" in tags:
        verb_present = True
    else:
        verb_present = False

    if len(parts) > 1:
        tokens = tokenise_uri_part(parts[-1])
        if len(tokens) != 0:
            tokens, tags = zip(*pos_tag(tokens))
        else:
            tags = []

        if "VB" in tags or \
           "VBD" in tags or \
           "VBG" in tags or \
           "VBN" in tags or \
           "VBP" in tags or \
           "VBZ" in tags:
            verb_present = True

    return verb_present

def activity_uri_to_verb_phrase_spec(uri):
    parts = get_uri_parts(uri)

    if len(parts) == 0:
        return uri

    tokens = tokenise_uri_part(parts[-1])
    tokens.insert(0, "I") # Messy, but should help it to work
    
    verb_tags = ["VB",
                 "VBD",
                 "VBG",
                 "VBN",
                 "VBP",
                 "VBZ"]

    modifier_tags = ["RB",
                    "RBR",
                    "RBS",
                    "JJ",
                    "JJR",
                    "JJS"]

    verb_head = []
    pre_modifiers = []
    post_modifiers = []

    for token, tag in pos_tag(tokens):
        if tag in verb_tags:
            verb_head.append(token)
        elif tag == "RP":
            verb_head.append(token)
        elif tag in modifier_tags:
            if len(verb_head)==0:
                pre_modifiers.append(token)
            else:
                post_modifiers.append(token)

    spec = {"type": "verb_phrase",
            "head": reduce(lambda a,b:a+" "+b, verb_head, "").lower().strip(),}
            #"pre-modifiers": [reduce(lambda a,b:a+" "+b, pre_modifiers, "").lower().strip()],
            #"post-modifiers": [reduce(lambda a,b:a+" "+b, post_modifiers, "").lower().strip()],}

    return spec


def activity_uri_to_noun_phrase_spec(uri):
    parts = get_uri_parts(uri)
    
    if len(parts) == 0:
        return uri
    else:
        tokens = tokenise_uri_part(parts[-1])

    return reduce(lambda a,b: a + " " + b, tokens, "").lower()

def lexicalise_uri(uri, classes):
    if prov["Agent"] in classes:
        agent_uri_to_noun_phrase_spec(uri)
    elif prov["Entity"] in classes:
        entity_uri_to_noun_phrase_spec(uri)
    elif prov["Activity"] in classes:
        activity_uri_to_verb_phrase_spec(uri)
