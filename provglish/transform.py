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
    
    def __str__(self):
        return self.__name
        
class Sentence():
    
    def __init__(self, sentence_string, coverage, tracked_ids):
        self.__sentence_string = sentence_string
        self.__coverage = coverage
        self.__tracked_ids
        
    def __str__(self):
        return self.__sentence_string

def def_binding(graph):
    results = graph.query("""SELECT ?object ?class WHERE {
                                GRAPH <myGraph>
                                {
                                    ?object a ?class .
                                }
                                FILTER regex( str(?class), "^http://www.w3.org/ns/prov#")}""")
    return results.bindings
    
def def_coverage(bindings, graph):
    """Takes a single set of bindings and returns the triples that are covered by the template with those bindings."""
        
    results = graph.query("""SELECT ?s ?p ?o WHERE {
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o .
                                                    }
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ) .
                                                    FILTER ( ?o = <%s> )
                                                } UNION
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o .
                                                    }
                                                    ?s a ?moreSpecificClass .
                                                    ?moreSpecificClass <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?o .
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?moreSpecificClass = <%s> ) . 
                                                    FILTER ( ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> )
                                                }
                                            }""" % (bindings["?object"], bindings["?class"], bindings["?object"], bindings["?class"]))
    return list(results)


def def_string(bindings):
    return "\x1b[32mThere is %s <%s>.\x1b[0m" % (nl.a(ce.CE.classes[str(bindings["?class"])]), bindings["?object"])
    

definitions = Template("CE Definitions", def_binding, def_coverage, def_string)


def prop_binding(graph):
    results = graph.query("""SELECT ?thing1 ?relationship ?thing2 ?thing1_class ?thing2_class WHERE {
                                GRAPH <myGraph>
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
    
    results = graph.query("""SELECT ?s ?p ?o WHERE {
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o
                                                    }
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?p = <%s> ) .
                                                    FILTER ( ?o = <%s> ) .
                                                } UNION
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o .
                                                    }
                                                    ?s ?moreSpecificProperty ?o .
                                                    ?moreSpecificProperty <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> ?p .
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?moreSpecificProperty = <%s> ) .
                                                    FILTER ( ?o = <%s> )
                                                } UNION
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o .
                                                    }
                                                    FILTER ( ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ) .
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?o = <%s> )
                                                } UNION
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o .
                                                    }
                                                    FILTER ( ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ) .
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?o = <%s> )
                                                } UNION
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o .
                                                    }
                                                    ?moreSpecificClass <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?o .
                                                    FILTER ( ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ) .
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?moreSpecificClass = <%s> )
                                                } UNION
                                                {
                                                    GRAPH <myGraph>
                                                    {
                                                        ?s ?p ?o .
                                                    }
                                                    ?moreSpecificClass <http://www.w3.org/2000/01/rdf-schema#subClassOf>+ ?o .
                                                    FILTER ( ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ) .
                                                    FILTER ( ?s = <%s> ) .
                                                    FILTER ( ?moreSpecificClass = <%s> )
                                                }
                                            }""" % (bindings["?thing1"], bindings["?relationship"], bindings["?thing2"], 
                                                    bindings["?thing1"], bindings["?relationship"], bindings["?thing2"],
                                                    bindings["?thing1"], bindings["?thing1_class"],
                                                    bindings["?thing2"], bindings["?thing2_class"],
                                                    bindings["?thing1"], bindings["?thing1_class"],
                                                    bindings["?thing2"], bindings["?thing2_class"]))
                                            
    return list(results)
    
def prop_string(bindings):
    
    if str(bindings["?relationship"]) in ce.CE.simple_predicates:
        return "\x1b[32mThe %s <%s> %s the %s <%s>.\x1b[0m" % (ce.CE.classes[str(bindings["?thing1_class"])], 
                                                bindings["?thing1"], 
                                                ce.CE.simple_predicates[str(bindings["?relationship"])], 
                                                ce.CE.classes[str(bindings["?thing2_class"])],
                                                bindings["?thing2"])
    else:
        return "\x1b[32mThe %s <%s> %s the %s <%s>.\x1b[0m" % (ce.CE.classes[str(bindings["?thing1_class"])],
                                                bindings["?thing1"],
                                                ce.CE.qualified_predicates[str(bindings["?thing1_class"])][str(bindings["?relationship"])],
                                                ce.CE.classes[str(bindings["?thing2_class"])],
                                                bindings["?thing2"])
    
properties = Template("CE Properties", prop_binding, prop_coverage, prop_string)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


