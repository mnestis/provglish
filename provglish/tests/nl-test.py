import unittest
import subprocess
from time import sleep
import os
import provglish
from provglish import prov
from provglish.nl import tools
from helper_funcs import load_fixture

nlgserv = None

def setUpModule():
    global nlgserv
    print "Starting up nlgserv..."
    nlgserv = subprocess.Popen(["nlgserv", "localhost", "8080"],
                               stdout=open(os.devnull, "w"),
                               stderr=open(os.devnull, "w"),
                               preexec_fn=os.setsid)
    sleep(60)
    print "Commencing testing..."

def tearDownModule():
    global nlgserv
    print "Shutting down nlgserv..."
    os.killpg(nlgserv.pid, subprocess.signal.SIGTERM)
    nlgserv.wait()

class TestServerSetup(unittest.TestCase):
    
    def test_server_there(self):
        sentence = {}
        
        sentence["subject"] = "John"
        sentence["verb"] = "kick"
        sentence["object"] = "Steve"
        
        output = tools.realise_sentence({"sentence": sentence})
        self.assertEqual(output, "John kicks Steve.")
    
class TestUsage(unittest.TestCase):
    def test_string(self):
        graph = load_fixture("nl_templates/usage.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.usage.generate_sentences(graph)

        self.assertEqual(len(sentences), 3)
