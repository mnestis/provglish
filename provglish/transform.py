import inflect
import rdflib
from rdflib.plugins import sparql
import prov

prov.query_init()

nl = inflect.engine()

class Transformer():
    
    def __init__(self):
        self._registered_templates = []
        self._history = {}

    def transform(self, graph):
        prov.load_prov_ontology(graph)
        sentences = self.render_graph(graph)
        sentences_pool = self.remove_dup_coverage(sentences)
        chosen_sentences = sentences_pool
        #chosen_sentences = self.choose_sentences(sentences_pool)     
        ordered_sentences = self.order_sentences(graph, chosen_sentences)
        return ordered_sentences

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

        previous = len(to_be_covered) + 1
        while to_be_covered:
            if len(to_be_covered) == previous:
                print "Breaking due to lack of progress."
                break
            else:
                previous = len(to_be_covered)
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

#            if not sentences:
 #               break

        return chosen_sentences

    def order_sentences(self, graph, chosen_sentences, topology_based=True):

        from pprint import pprint

        filtered_graph = filter(lambda a: a[1].startswith("http://www.w3.org/ns/prov#"), list(graph.get_context("prov_graph")))
      
        if topology_based:
            from toposort import toposort, toposort_flatten
            
            node_graph = {}
            for triple in filtered_graph:
                if triple[0] not in node_graph:
                    node_graph[triple[0]] = set()
                if triple[2] not in node_graph[triple[0]]:
                    node_graph[triple[0]].add(triple[2])

            topological_node_order = list(reversed(toposort_flatten(node_graph)))

            ordered_sentences = []

            for node in topological_node_order:
                for sentence in chosen_sentences:
                    if node in map(lambda a: a[0], sentence.coverage):
                        if sentence not in ordered_sentences:
                            ordered_sentences.append(sentence)
                if len(ordered_sentences) == len(chosen_sentences):
                    return ordered_sentences

            for sentence in chosen_sentences:
                if sentence not in ordered_sentences:
                    ordered_sentences.append(sentence)

            return ordered_sentences

    def generate_paragraph(self, sentences):
        paragraph = ""
        for sentence in sentences:
            paragraph += sentence.generate_string(self._history) + "\n"
            
        return paragraph

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
        
    def generate_sentences(self, graph):
        sentences = []
        bindings = self.bindings(graph)
        for binding in bindings:
            coverage = self.coverage(binding, graph)
            sentences.append(Sentence(self.__string_function, coverage, binding))
        return sentences    
        
    def __str__(self):
        return self.__name
        
class Sentence():
    
    def __init__(self, string_generator, coverage, bindings, tracked_ids=None):
        self._string_generator = string_generator
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
        return self._string_generator(self._bindings, {})

    def generate_string(self, history):
        return self._string_generator(self._bindings, history)

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
