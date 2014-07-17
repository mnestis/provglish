import rdflib, os

def load_bravo():
    return load_fixture("bravo.ttl")

def load_fixture(filename):
    graph = rdflib.graph.ConjunctiveGraph()
    graph.parse(os.path.join(os.path.dirname(__file__), "test_fixtures/", filename), format="turtle", publicID="prov_graph")
    return graph
