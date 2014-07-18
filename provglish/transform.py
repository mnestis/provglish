import ce
import inflect
import rdflib
from rdflib.plugins import sparql
import prov

prov.query_init()

nl = inflect.engine()


class Transformer():
    
    def __init__(self):
        self._registered_templates = []

    def transform(self, graph):
        from time import clock
        print clock(), "\tGenerating all possible sentences."
        sentences = self.render_graph(graph)

        print clock(), "\tRemoving duplicates."
        sentences_pool = self.remove_dup_coverage(sentences)

        print clock(), "\tChoosing the right sentences."
        return self.choose_sentences(sentences_pool)     

    def render_graph(self, graph):
        sentences = []
        
        for template in self._registered_templates:
            sentences.extend(template.generate_sentences(graph))
        
        return sentences

    def remove_dup_coverage(self, sentences):
        from random import randint
        ## Dict: hashes
        ## Key: the hash of the coverage
        ## Value: a list of sentences whose coverage matches that hash
        hashes = {}
        for sentence in sentences:
            if sentence.coverage_hash not in hashes:
                hashes[sentence.coverage_hash] = [sentence]
            else:
                hashes[sentence.coverage_hash].append(sentence)

        ## Remove sentences that cover the same triple  
        sentences_out = [] 
        
        for key in hashes:
            sentences_out.append(hashes[key][randint(0, len(hashes[key])-1)])
            
        return sentences_out
        
    def choose_sentence(self, to_be_covered, sentences):
        # If there's a triple that can only be covered by one sentence, we must pick that sentence.
        for triple in to_be_covered:
            if len(to_be_covered[triple])==1:
                return to_be_covered[triple][0]
        
        # Now we pick the sentence with the greatest coverage
        biggest = (0, None)
        for sentence in sentences:
            if len(sentence.coverage) > biggest[0]:
                biggest = (len(sentence.coverage), sentence)
    
        return biggest[1]
        
    def choose_sentences(self, sentences):
        ## Dict: to_be_covered
        ## Key: triple
        ## Value: a list of sentences that can cover that triple
        to_be_covered = {}

        for sentence in sentences:
            for triple in sentence.coverage:
                if triple not in to_be_covered:
                    to_be_covered[triple] = [sentence]
                else:
                    to_be_covered[triple].append(sentence)
        
        chosen_sentences = [] # A list that will hold the sentences we choose

        while to_be_covered:
            chosen_sentence = self.choose_sentence(to_be_covered, sentences)
            chosen_sentences.append(chosen_sentence)
            for triple in chosen_sentence.coverage:
                # If the triple details something other than class, remove all other sentences that cover it
                if triple[1] != rdflib.namespace.RDF.type:
                    # For each sentence that covers it
                    for sentence in to_be_covered[triple]:
                        # We need to remove the sentence from the lists of sentences that cover the *other* triples it covers
                        for a_triple in sentence.coverage:
                            if triple != a_triple:
                                if a_triple in to_be_covered:
                                    to_be_covered[a_triple].remove(sentence)
                        # Then remove the sentence itself from the pool
                        sentences.remove(sentence)
                # Remove any triples it covers from to_be_covered
                if triple in to_be_covered:
                    del to_be_covered[triple]
            
            if chosen_sentence in sentences:
                sentences.remove(chosen_sentence)
        
        return chosen_sentences

    def register_template(self, template):
        self._registered_templates.append(template)

class Template():    
    def __init__(self, name, bindings_function, coverage_function, string_function):
        self.__bindings_function = bindings_function
        self.__coverage_function = coverage_function
        self.__string_function = string_function
        self.__name = name
    
    def bindings(self, graph):
        return self.__bindings_function(graph)
    
    def coverage(self, bindings, graph):
        return self.__coverage_function(bindings, graph)
        
    def make_string(self, bindings):
        return self.__string_function(bindings)
    
    def generate_sentences(self, graph):
        sentences = []
        bindings = self.bindings(graph)
        for binding in bindings:
            coverage = self.coverage(binding, graph)
            sentence_string = self.make_string(binding)
            sentences.append(Sentence(sentence_string, coverage, binding))
        return sentences    
        
    def __str__(self):
        return self.__name
        
class Sentence():
    
    def __init__(self, sentence_string, coverage, bindings, tracked_ids=None):
        self._sentence_string = sentence_string
        self._coverage = coverage
        self._coverage_hash = self._calculate_coverage_hash()
        self._bindings = bindings
        self._tracked_ids = tracked_ids
        
    @property    
    def coverage(self):
        return self._coverage[:]
        
    @property
    def coverage_hash(self):
        return self._coverage_hash
        
    def _calculate_coverage_hash(self):
        coverage = sorted(self.coverage, cmp=Sentence._order_triples)
        return hash(tuple(coverage))
            
    def __str__(self):
        return self._sentence_string

    @staticmethod
    def _order_triples(tripleA, tripleB):
        if tripleA[0] != tripleB[0]:
            return (1 if tripleA[0] > tripleB[0] else -1)
        elif tripleA[1] != tripleB[1]:
            return (1 if tripleA[1] > tripleB[1] else -1)
        elif tripleA[2] != tripleB[2]:
            return (1 if tripleA[2] > tripleB[2] else -1)
        else:
            return 0

_def_binding_query = sparql.prepareQuery("""SELECT ?object ?class WHERE {
                                GRAPH <prov_graph>
                                {
                                    ?object a ?class .
                                }
                                FILTER regex( str(?class), "^http://www.w3.org/ns/prov#")}""")

def def_binding(graph):
    results = graph.query(_def_binding_query)
    return results.bindings
    
def def_coverage(bindings, graph):
    """Takes a single set of bindings and returns the triples that are covered by the template with those bindings."""
    rdf = rdflib.namespace.RDF    
        
    coverage_list = []
    
    # Add the type
    coverage_list.append((bindings["?object"], rdf.type, bindings["?class"]))

    # Add less specific types
    q_results = prov.fetch_less_precise_type(bindings["?object"], bindings["?class"], graph)
    for result in q_results.bindings:
        coverage_list.append((bindings["?object"], rdf.type, result["?lessPreciseType"]))

    return coverage_list


def def_string(bindings):
    return "There is %s <%s>.\n" % (nl.a(ce.classes[str(bindings["?class"])]), bindings["?object"])
    

definitions = Template("CE Definitions", def_binding, def_coverage, def_string)

_multi_prop_binding_query = sparql.prepareQuery("""
        SELECT ?thing1 ?relationship ?thing2 ?thing1_class ?thing2_class WHERE {
            GRAPH <prov_graph> {
                ?thing1 ?relationship ?thing2 .
                ?thing1 a ?thing1_class .
                ?thing2 a ?thing2_class
            }
            FILTER regex(str(?relationship), "^http://www.w3.org/ns/prov#")
        } ORDER BY ?thing1""")    
    
def multi_prop_binding(graph):
    results = graph.query(_multi_prop_binding_query)
    raw_bindings = results.bindings

    grouped_bindings = []
    current_subject = None
    most_precise_class = None
    
    for binding in raw_bindings:
        if binding["?thing1"] != current_subject:
            if most_precise_class != None:
                grouped_bindings[-1]["?thing1_class"] = most_precise_class
            current_subject = binding["?thing1"]
            most_precise_class = None
            grouped_bindings.append({"?thing1":binding["?thing1"], 
                                     "relationships": []})
        if not prov.exists_more_precise(binding["?thing2_class"], binding["?thing2"], graph):
            rel = {"?relationship": binding["?relationship"], 
                   "?thing2": binding["?thing2"],
                   "?thing2_class": binding["?thing2_class"]}
            if rel not in grouped_bindings[-1]["relationships"]:
                grouped_bindings[-1]["relationships"].append(rel)
        if most_precise_class == None:
            most_precise_class = binding["?thing1_class"]
        elif most_precise_class != binding["?thing1_class"]:
            if most_precise_class in [res[0] for res in prov.fetch_less_precise_type(binding["?thing1"], binding["?thing1_class"], graph)]:
                most_precise_class = binding["?thing1_class"]
            
    grouped_bindings[-1]["?thing1_class"] = most_precise_class        
                                                      
    return grouped_bindings
    
def multi_prop_coverage(bindings, graph):
    rdf = rdflib.namespace.RDF
    coverage_list = []
    
    covered_classes_dict = {}
    
    # First add the thing1 and its types
    coverage_list.append((bindings["?thing1"], rdf.type, bindings["?thing1_class"]))
    covered_classes_dict["?thing1"] = [bindings["?thing1_class"]]
    
    # Add supertypes of thing1_class:
    for supertype in prov.fetch_less_precise_type(bindings["?thing1"], bindings["?thing1_class"], graph):
        coverage_list.append((bindings["?thing1"], rdf.type, supertype[0]))
        covered_classes_dict["?thing1"].append(supertype[0])

    # Add all the relationship triples
    for rel in bindings["relationships"]:
        # The relationships themselves
        if (bindings["?thing1"], rel["?relationship"], rel["?thing2"]) not in coverage_list:
            coverage_list.append((bindings["?thing1"], rel["?relationship"], rel["?thing2"]))
        
        # And all the classes of the thing2s
        triple = (rel["?thing2"], rdf.type, rel["?thing2_class"])
        if triple not in coverage_list:
            coverage_list.append(triple)
        for superclass in prov.fetch_less_precise_type(rel["?thing2"], rel["?thing2_class"], graph):
            triple = (rel["?thing2"], rdf.type, superclass[0])
            if triple not in coverage_list:
                coverage_list.append(triple)
            
    return coverage_list

def multi_prop_string(bindings):
    thing1 = bindings["?thing1"]
    thing1_class = ce.classes[str(bindings["?thing1_class"])]
    
    sentence = "The %s <%s>" % (thing1_class, thing1)
    
    rel_strings = []
    for rel in bindings["relationships"]:
        thing2 = rel["?thing2"]
        thing2_class = ce.classes[str(rel["?thing2_class"])]
        if str(rel["?relationship"]) in ce.simple_predicates:
            relationship = ce.simple_predicates[str(rel["?relationship"])]
        else:
            relationship = ce.qualified_predicates[str(bindings["?thing1_class"])][str(rel["?relationship"])]
        rel_strings.append("\n\t%s the %s <%s>" % (relationship, thing2_class, thing2))
        
    for rel in rel_strings[:-1]:
        sentence += rel + " and"
        
    sentence += rel_strings[-1] + ".\n"
    
    return sentence
        
multi_prop = Template("CE Multi", multi_prop_binding, multi_prop_coverage, multi_prop_string)
