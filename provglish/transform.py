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
        prov.load_prov_ontology(graph)
        sentences = self.render_graph(graph)
        sentences_pool = self.remove_dup_coverage(sentences)
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
