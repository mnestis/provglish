import ce
import inflect
import rdflib

nl = inflect.engine()


class Tranformer():
    
    def __init__(self):
        self.__registered_templates = []

    def register_template(self, template):
        self.__registered_templates.append(template)


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
        self.__sentence_string = sentence_string
        self.__coverage = coverage
        self.__bindings = bindings
        self.__tracked_ids = tracked_ids
        
    def __str__(self):
        return self.__sentence_string

def def_binding(graph):
    results = graph.query("""SELECT ?object ?class WHERE {
                                GRAPH <prov_graph>
                                {
                                    ?object a ?class .
                                }
                                FILTER regex( str(?class), "^http://www.w3.org/ns/prov#")}""")
    return results.bindings
    
def def_coverage(bindings, graph):
    """Takes a single set of bindings and returns the triples that are covered by the template with those bindings."""
    rdf = rdflib.namespace.RDF    
        
    coverage_list = []
    
    # Add the type
    coverage_list.append((bindings["?object"], rdf.type, bindings["?class"]))

    # Add less specific types
    q_result = graph.query("""SELECT ?lessSpecificType WHERE {
                                GRAPH <prov_graph> {
                                    <%s> a ?lessSpecificType
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?lessSpecificType
                            }""" % (bindings["?object"], bindings["?class"]))

    return coverage_list


def def_string(bindings):
    return "\x1b[32mThere is %s <%s>.\x1b[0m\n" % (nl.a(ce.CE.classes[str(bindings["?class"])]), bindings["?object"])
    

definitions = Template("CE Definitions", def_binding, def_coverage, def_string)


def prop_binding(graph):
    results = graph.query("""SELECT ?thing1 ?relationship ?thing2 ?thing1_class ?thing2_class WHERE {
                                GRAPH <prov_graph>
                                {
                                    ?thing1 ?relationship ?thing2 . 
                                    FILTER regex( str(?relationship), "^http://www.w3.org/ns/prov#") . 
                                    ?thing1 a ?thing1_class .
                                    FILTER regex( str(?thing1_class), "^http://www.w3.org/ns/prov#") .
                                    ?thing2 a ?thing2_class .
                                    FILTER regex( str(?thing2_class), "^http://www.w3.org/ns/prov#")    
                                }                          
                            }""")
                            
    return results.bindings
    
def prop_coverage(bindings, graph):
    """Takes a single set of bindings and returns the triples that are covered by the template with those bindings."""
    
    rdf = rdflib.namespace.RDF
    
    coverage_list = []
    
    # Add the relationship triple:
    coverage_list.append((bindings["?thing1"], bindings["?relationship"], bindings["?thing2"]))
    
    # Add any less specific relationships:
    q_results = graph.query("""SELECT ?lessSpecificRelationship WHERE {
                                GRAPH <prov_graph> {
                                    <%s> ?lessSpecificRelationship <%s>
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subPropertyOf>+ ?lessSpecificRelationship
                            }""" % (bindings["?thing1"], bindings["?thing2"], bindings["?relationship"]))
    for result in q_results:
        coverage_list.append((bindings["?thing1"], result[0], bindings["?thing2"]))               
    
    # Add the types:
    coverage_list.append((bindings["?thing1"], rdf.type, bindings["?thing1_class"]))
    coverage_list.append((bindings["?thing2"], rdf.type, bindings["?thing2_class"]))
    
    # Add any less specific types:
    ## thing1
    q_results = graph.query("""SELECT ?lessSpecificType WHERE {
                                GRAPH <prov_graph> {
                                    <%s> a ?lessSpecificType
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?lessSpecificType
                            }""" % (bindings["?thing1"], bindings["?thing1_class"]))
    for result in q_results:
        coverage_list.append((bindings["?thing1"], rdf.type, result[0]))
    ## thing2
    q_results = graph.query("""SELECT ?lessSpecificType WHERE {
                                GRAPH <prov_graph> {
                                    <%s> a ?lessSpecificType
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?lessSpecificType
                            }""" % (bindings["?thing2"], bindings["?thing2_class"]))
    for result in q_results:
        coverage_list.append((bindings["?thing2"], rdf.type, result[0]))
    
    return coverage_list
    
def prop_string(bindings):
    
    if str(bindings["?relationship"]) in ce.CE.simple_predicates:
        return "\x1b[32mThe %s <%s>\n\t%s the %s <%s>.\x1b[0m\n" % (ce.CE.classes[str(bindings["?thing1_class"])], 
                                                bindings["?thing1"], 
                                                ce.CE.simple_predicates[str(bindings["?relationship"])], 
                                                ce.CE.classes[str(bindings["?thing2_class"])],
                                                bindings["?thing2"])
    else:
        return "\x1b[32mThe %s <%s>\n\t%s the %s <%s>.\x1b[0m\n" % (ce.CE.classes[str(bindings["?thing1_class"])],
                                                bindings["?thing1"],
                                                ce.CE.qualified_predicates[str(bindings["?thing1_class"])][str(bindings["?relationship"])],
                                                ce.CE.classes[str(bindings["?thing2_class"])],
                                                bindings["?thing2"])
    
properties = Template("CE Properties", prop_binding, prop_coverage, prop_string)
    
def two_prop_bindings(graph):
    results = graph.query("""SELECT ?thing1 ?relationship12 ?thing2 ?relationship13 ?thing3 ?thing1_class ?thing2_class ?thing3_class WHERE {
                            GRAPH <prov_graph> {
                                ?thing1 ?relationship12 ?thing2 .
                                ?thing1 ?relationship13 ?thing3 .
                                ?thing1 a ?thing1_class .
                                ?thing2 a ?thing2_class .
                                ?thing3 a ?thing3_class .
                                FILTER ( ?thing2 != ?thing3)
                            }
                          }""")
                          
    return results.bindings

def two_prop_coverage(bindings, graph):
    
    coverage_list = []
    rdf = rdflib.namespace.RDF
    
    # Add the two relationships
    coverage_list.append((bindings["?thing1"], bindings["?relationship12"], bindings["?thing2"]))
    coverage_list.append((bindings["?thing1"], bindings["?relationship13"], bindings["?thing3"]))
    
    # Add the three object types
    coverage_list.append((bindings["?thing1"], rdf.type, bindings["?thing1_class"]))
    coverage_list.append((bindings["?thing2"], rdf.type, bindings["?thing2_class"]))
    coverage_list.append((bindings["?thing3"], rdf.type, bindings["?thing3_class"]))
    
    # Add the relationship superproperties
    ## relationship12
    q_results = graph.query("""SELECT ?lessPreciseProp WHERE {
                                GRAPH <prov_graph> {
                                    <%s> ?lessPreciseProp <%s>.
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subPropertyOf>+ ?lessPreciseProp .
                            }""" % (bindings["?thing1"], bindings["?thing2"], bindings["?relationship12"]))
    for result in q_results:
        coverage_list.append((bindings["?thing1"], result[0], bindings["?relationship12"]))

    ## relationship13
    q_results = graph.query("""SELECT ?lessPreciseProp WHERE {
                                GRAPH <prov_graph> {
                                    <%s> ?lessPreciseProp <%s>.
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subPropertyOf>+ ?lessPreciseProp .
                            }""" % (bindings["?thing1"], bindings["?thing3"], bindings["?relationship13"]))
    for result in q_results:
        coverage_list.append((bindings["?thing1"], result[0], bindings["?relationship13"]))
    
    # Add the object supertypes
    ## thing1
    q_results = graph.query("""SELECT ?lessPreciseClass WHERE {
                                GRAPH <prov_graph> {
                                    <%s> a ?lessPreciseClass .
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?lessPreciseClass .
                            }""" % (bindings["?thing1"], bindings["?thing1_class"]))
    for result in q_results:
        coverage_list.append((bindings["?thing1"], rdf.type, result[0]))
    ## thing2
    q_results = graph.query("""SELECT ?lessPreciseClass WHERE {
                                GRAPH <prov_graph> {
                                    <%s> a ?lessPreciseClass .
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?lessPreciseClass .
                            }""" % (bindings["?thing2"], bindings["?thing2_class"]))  
    for result in q_results:
        coverage_list.append((bindings["?thing2"], rdf.type, result[0]))
    ## thing3
    q_results = graph.query("""SELECT ?lessPreciseClass WHERE {
                                GRAPH <prov_graph> {
                                    <%s> a ?lessPreciseClass .
                                }
                                <%s> <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?lessPreciseClass .
                            }""" % (bindings["?thing3"], bindings["?thing3_class"]))   
    for result in q_results:
        coverage_list.append((bindings["?thing3"], rdf.type, result[0]))
    
    return coverage_list
    
def two_prop_string(bindings):
    
    thing1 = str(bindings["?thing1"])
    thing2 = str(bindings["?thing2"])
    thing3 = str(bindings["?thing3"])
    
    thing1_class = ce.CE.classes[str(bindings["?thing1_class"])]
    thing2_class = ce.CE.classes[str(bindings["?thing2_class"])]
    thing3_class = ce.CE.classes[str(bindings["?thing3_class"])]
    
    if str(bindings["?relationship12"]) in ce.CE.simple_predicates:
        relationship12 = ce.CE.simple_predicates[str(bindings["?relationship12"])]
    else:
        relationship12 = ce.CE.qualified_predicates[str(bindings["?thing1_class"])][str(bindings["?relationship12"])]
        
    if str(bindings["?relationship13"]) in ce.CE.simple_predicates:
        relationship13 = ce.CE.simple_predicates[str(bindings["?relationship13"])]
    else:
        relationship13 = ce.CE.qualified_predicates[str(bindings["?thing1_class"])][str(bindings["?relationship13"])]
        
    return "\x1b[32mThe %s <%s>\n\t%s the %s <%s>\n\tand %s the %s <%s>.\x1b[0m\n" % (thing1_class, thing1,
                                                                    relationship12, thing2_class, thing2,
                                                                    relationship13, thing3_class, thing3)
        
two_props = Template("CE two properties", two_prop_bindings, two_prop_coverage, two_prop_string)
    
    
