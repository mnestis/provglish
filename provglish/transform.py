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

    def render_graph(self, graph):
        sentences = []
        
        for template in self._registered_templates:
            sentences.extend(template.generate_sentences(graph))
        
        return sentences

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
    return "\x1b[32mThere is %s <%s>.\x1b[0m\n" % (nl.a(ce.CE.classes[str(bindings["?class"])]), bindings["?object"])
    

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
        grouped_bindings[-1]["relationships"].append({"?relationship": binding["?relationship"], 
                                                      "?thing2": binding["?thing2"],
                                                      "?thing2_class": binding["?thing2_class"]})
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
        if rel["?thing2"] not in covered_classes_dict:
            covered_classes_dict[rel["?thing2"]] = []
        if rel["?thing2_class"] not in covered_classes_dict[rel["?thing2"]]:
            covered_classes_dict[rel["?thing2"]].append(rel["?thing2_class"])
            coverage_list.append((rel["?thing2"], rdf.type, rel["?thing2_class"]))
            
    return coverage_list

def multi_prop_string(bindings):
    thing1 = bindings["?thing1"]
    thing1_class = ce.CE.classes[str(bindings["?thing1_class"])]
    
    sentence = "The %s <%s>" % (thing1_class, thing1)
    
    rel_strings = []
    for rel in bindings["relationships"]:
        thing2 = rel["?thing2"]
        thing2_class = ce.CE.classes[str(rel["?thing2_class"])]
        if str(rel["?relationship"]) in ce.CE.simple_predicates:
            relationship = ce.CE.simple_predicates[str(rel["?relationship"])]
        else:
            relationship = ce.CE.qualified_predicates[str(bindings["?thing1_class"])][str(rel["?relationship"])]
        rel_strings.append("\n\t%s the %s <%s>" % (relationship, thing2_class, thing2))
        
    for rel in rel_strings[:-1]:
        sentence += rel + " and"
        
    sentence += rel_strings[-1] + ".\n"
    
    return sentence
        
multi_prop = Template("CE Multi", multi_prop_binding, multi_prop_coverage, multi_prop_string)
