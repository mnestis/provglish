import rdflib, os

def load_bravo():
    graph = rdflib.graph.ConjunctiveGraph()
    graph.parse(os.path.join(os.path.dirname(__file__), "test_fixtures/bravo.ttl"), format="turtle", publicID="prov_graph")
    return graph
