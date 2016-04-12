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
    def test_usage_string(self):
        graph = load_fixture("nl_templates/usage.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.usage.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 3)
        self.assertIn("Act 1 used something at 2014-10-10T10:00:00+01:00.", strings)
        self.assertIn("Act 2 used ent 2.", strings)
        self.assertIn("Act 3 used ent 3 at 2014-11-11T11:00:00+00:00.", strings)
        
class TestGeneration(unittest.TestCase):
    def test_generation_string(self):
        graph = load_fixture("nl_templates/generation.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.generation.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 3)
        self.assertIn("Ent 1 was generated at 2014-10-10T11:00:00+01:00.", strings)
        self.assertIn("Ent 2 was generated by act 2.", strings)
        self.assertIn("Ent 3 was generated at 2014-10-11T12:00:00+01:00 by act 3.", strings)

class TestDelegation(unittest.TestCase):
    def test_delegation_string(self):
        graph = load_fixture("nl_templates/delegation.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.delegation.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 2)
        self.assertIn("John acted on behalf of james.", strings)
        self.assertIn("Jack did fetching on behalf of jill.", strings)

class TestAssociation(unittest.TestCase):
    def test_association_string(self):
        graph = load_fixture("nl_templates/association.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.association.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Swimming was associated with john.", strings)

    def test_association_qualified_string(self):
        graph = load_fixture("nl_templates/association_qualified.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.association.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Swimming was associated with john.", strings)

class TestAgent(unittest.TestCase):
    def test_agent_string(self):
        graph = load_fixture("nl_templates/agent.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.agent.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Fred was an agent.", strings)

class TestAttribution(unittest.TestCase):
    def test_attribution_string(self):
        graph = load_fixture("nl_templates/attribution.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.attribution.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Entity was attributed to agent.", strings)

    def test_attribution_qualified_string(self):
        graph = load_fixture("nl_templates/attribution_qualified.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.attribution.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Entity was attributed to agent.", strings)

class TestCommunication(unittest.TestCase):
    def test_communication_string(self):
        graph = load_fixture("nl_templates/communication.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.communication.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Baking was informed by reading.", strings)

    def test_communication_qualified_string(self):
        graph = load_fixture("nl_templates/communication_qualified.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.communication.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Baking was informed by reading.", strings)

class TestEntity(unittest.TestCase):
    def test_entity_string(self):
        graph = load_fixture("nl_templates/entity.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.entity.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Ball was an entity.", strings)

class TestInvalidation(unittest.TestCase):
    def test_invalidation_string(self):
        graph = load_fixture("nl_templates/invalidation.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.invalidation.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 3)
        self.assertIn("Ent 1 was invalidated at 2014-10-10T11:00:00+01:00.", strings)
        self.assertIn("Ent 2 was invalidated by act 2.", strings)
        self.assertIn("Ent 3 was invalidated at 2014-10-11T11:00:00+01:00 by act 3.", strings)

class TestActivity(unittest.TestCase):
    def test_activity(self):
        graph = load_fixture("nl_templates/activity.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.activity.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Activity was an activity.", strings)

    def test_activity_start(self):
        graph = load_fixture("nl_templates/activity_start.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.activity_start.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Activity was an activity that started at 2011-11-16T16:05:00+00:00.", strings)

    def test_activity_end(self):
        graph = load_fixture("nl_templates/activity_end.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.activity_end.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Activity was an activity that ended at 2015-11-16T16:05:00+00:00.", strings)

    def test_activity_times(self):
        graph = load_fixture("nl_templates/activity_times.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.activity_duration.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        self.assertEqual(len(sentences), 1)
        self.assertIn("Activity was an activity that started at 2015-11-16T16:05:00+00:00 and ended at 2016-11-16T16:05:00+00:00.", strings)

class TestEnd(unittest.TestCase):
    def test_end(self):
        graph = load_fixture("nl_templates/end.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.end.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        print strings

        self.assertEqual(len(sentences), 4)
        self.assertIn("The end of activity 1 was triggered by trigger 1.", strings)
        self.assertIn("The activity 2 was ended by ender 2.", strings)
        self.assertIn("The activity 3 was ended at 2014-10-10T11:00:00+01:00.", strings)
        self.assertIn("The activity 4 was ended at 2014-10-10T11:00:00+01:00 by ender 4.", strings)

class TestStart(unittest.TestCase):
    def test_start(self):
        graph = load_fixture("nl_templates/start.ttl")
        graph = prov.load_prov_ontology(graph)
        sentences = provglish.nl.templates.start.generate_sentences(graph)

        strings = []
        for sentence in sentences:
            strings.append(str(sentence))

        print strings

        self.assertEqual(len(sentences), 4)
        self.assertIn("The start of activity 1 was triggered by trigger 1.", strings)
        self.assertIn("The activity 2 was started by starter 2.", strings)
        self.assertIn("The activity 3 was started at 2014-10-10T11:00:00+01:00.", strings)
        self.assertIn("The activity 4 was started at 2014-10-10T11:00:00+01:00 by starter 4.", strings)
