import inflect

class Sentence():
    
    def __init__(self, subject, relationships):
        self.subject = subject
        self.relationships = relationships
    
    def __str__(self):
        nl = inflect.engine()
        
        if self.relationships == []:
            return "There is %s <%s>" % (nl.a(self.subject["class"]), self.subject["uri"])
        else:
            ce_string = "The %s <%s> " % (self.subject["class"], self.subject["uri"])
            
            for relationship in self.relationships[:-1]:
                ce_string += "%s the %s <%s> and " % (relationship["predicate"], relationship["object_class"], relationship["object_uri"])
            
            ce_string += "%s the %s <%s>." % (self.relationships[-1]["predicate"], self.relationships[-1]["object_class"], self.relationships[-1]["object_uri"])
            
            return ce_string
            
            
def parse(filename, file_format):
    import rdflib
    
    graph = rdflib.Graph()
    graph.parse(filename, format=file_format)

    return graph

def convert_graph(graph):
    import prov
    nl = inflect.engine()
    
    things = graph.query("""SELECT DISTINCT ?provThing ?class WHERE { ?provThing a ?class . FILTER regex(str(?class), "^http://www.w3.org/ns/prov#") }""")
    
    for subject_URI, subject_class_URI in things:
        
        if(prov.exists_more_precise(subject_class_URI, subject_URI, graph)):
            continue
        
        subject_URI = str(subject_URI)
        subject_class_URI = str(subject_class_URI)
        subject_class = CE.classes[subject_class_URI]
        
        print "There is %s %s." % (nl.a(subject_class), subject_URI)
        
        properties = graph.query("""SELECT DISTINCT ?relationship ?object ?object_class WHERE { <%s> ?relationship ?object . OPTIONAL { ?object a ?object_class} . FILTER (?relationship != rdf:type) }""" % (subject_URI,))
        
        for relationship_URI, object_URI, object_class_URI in properties:
            relationship_URI = str(relationship_URI)
            object_URI = str(object_URI)
            if object_class_URI != None:
                object_class = CE.classes[str(object_class_URI)]
            else:
                object_class = "prov thing"
                
            if prov.exists_more_precise(object_class_URI, object_URI, graph):
                continue
            
            if relationship_URI in CE.simple_predicates:
                relationship = CE.simple_predicates[relationship_URI]
            elif subject_class_URI in CE.qualified_predicates:
                if relationship_URI in CE.qualified_predicates[subject_class_URI]:
                    relationship = CE.qualified_predicates[subject_class_URI][relationship_URI]
                else:
                    raise Exception("Can't handle %s for type %s" % (relationship_URI, subject_class))
            else:
                raise Exception("Can't handle %s for type %s" % (relationship_URI, subject_class))
                
            print "The %s <%s> %s the %s <%s>." % (subject_class, subject_URI, relationship, object_class, object_URI)

class CE():
    classes = {
        "http://www.w3.org/ns/prov#Entity": "entity",
        "http://www.w3.org/ns/prov#Activity": "activity", 
        "http://www.w3.org/ns/prov#Agent": "agent",
        "http://www.w3.org/ns/prov#Collection": "collection",
        "http://www.w3.org/ns/prov#EmptyCollection": "empty collection",
        "http://www.w3.org/ns/prov#Bundle": "provenance bundle",
        "http://www.w3.org/ns/prov#Person": "person",
        "http://www.w3.org/ns/prov#SoftwareAgent": "software agent",
        "http://www.w3.org/ns/prov#Organization": "organization",
        "http://www.w3.org/ns/prov#Location": "location",
        "http://www.w3.org/ns/prov#Influence": "influence",
        "http://www.w3.org/ns/prov#EntityInfluence": "entity-influence",
        "http://www.w3.org/ns/prov#Usage": "usage",
        "http://www.w3.org/ns/prov#Start": "start",
        "http://www.w3.org/ns/prov#End": "end",
        "http://www.w3.org/ns/prov#Derivation": "derivation",
        "http://www.w3.org/ns/prov#PrimarySource": "primary source",
        "http://www.w3.org/ns/prov#Quotation": "quotation",
        "http://www.w3.org/ns/prov#Revision": "revision",
        "http://www.w3.org/ns/prov#ActivityInfluence": "activity-influence",
        "http://www.w3.org/ns/prov#Generation": "generation",
        "http://www.w3.org/ns/prov#Communication": "communication",
        "http://www.w3.org/ns/prov#Invalidation": "invalidation",
        "http://www.w3.org/ns/prov#AgentInfluence": "agent-influence",
        "http://www.w3.org/ns/prov#Attribution": "attribution",
        "http://www.w3.org/ns/prov#Association": "association",
        "http://www.w3.org/ns/prov#Plan": "plan",
        "http://www.w3.org/ns/prov#Delegation": "delegation",
        "http://www.w3.org/ns/prov#InstantaneousEvent": "instantaneous event",
        "http://www.w3.org/ns/prov#Role": "role"
    }

    simple_predicates = {
        "http://www.w3.org/ns/prov#wasGeneratedBy": "was generated by",
        "http://www.w3.org/ns/prov#wasDerivedFrom": "was derived from",
        "http://www.w3.org/ns/prov#wasAttributedTo": "was attributed to",
        "http://www.w3.org/ns/prov#startedAtTime": "started at",
        "http://www.w3.org/ns/prov#used": "used",
        "http://www.w3.org/ns/prov#wasInformedBy": "was informed by",
        "http://www.w3.org/ns/prov#endedAtTime": "ended at",
        "http://www.w3.org/ns/prov#wasAssociatedWith": "was associated with",
        "http://www.w3.org/ns/prov#actedOnBehalfOf": "acted on behalf of",
        "http://www.w3.org/ns/prov#alternateOf": "is an alternate of",
        "http://www.w3.org/ns/prov#specializationOf": "is a specialization of",
        "http://www.w3.org/ns/prov#generatedAtTime": "was generated at",
        "http://www.w3.org/ns/prov#hadPrimarySource": "had as its primary source",
        "http://www.w3.org/ns/prov#value": "had as its value", # Check this one works...
        "http://www.w3.org/ns/prov#wasQuotedFrom": "was quoted from",
        "http://www.w3.org/ns/prov#wasRevisionOf": "was a revision of",
        "http://www.w3.org/ns/prov#invalidatedAtTime": "was invalidated at",
        "http://www.w3.org/ns/prov#wasInvalidatedBy": "was invalidated by",
        "http://www.w3.org/ns/prov#hadMember": "had as a member",
        "http://www.w3.org/ns/prov#wasStartedBy": "was started by",
        "http://www.w3.org/ns/prov#wasEndedBy": "was ended by",
        "http://www.w3.org/ns/prov#invalidated": "invalidated",
        "http://www.w3.org/ns/prov#influenced": "influenced",
        "http://www.w3.org/ns/prov#atLocation": "had as its location",
        "http://www.w3.org/ns/prov#generated": "generated",
        "http://www.w3.org/ns/prov#wasInfluencedBy": "was influenced by",
        "http://www.w3.org/ns/prov#qualifiedInfluence": "was influenced according to",
        "http://www.w3.org/ns/prov#qualifiedGeneration": "was generated according to",
        "http://www.w3.org/ns/prov#qualifiedDerivation": "was derived according to",
        "http://www.w3.org/ns/prov#qualifiedPrimarySource": "had its primary source according to",
        "http://www.w3.org/ns/prov#qualifiedQuotation": "was quoted according to",
        "http://www.w3.org/ns/prov#qualifiedRevision": "was revised according to",
        "http://www.w3.org/ns/prov#qualifiedAttribution": "was attributed according to",
        "http://www.w3.org/ns/prov#qualifiedInvalidation": "was invalidated according to",
        "http://www.w3.org/ns/prov#qualifiedStart": "was started according to",
        "http://www.w3.org/ns/prov#qualifiedUsage": "was used according to",
        "http://www.w3.org/ns/prov#qualifiedCommunication": "was informed according to",
        "http://www.w3.org/ns/prov#qualifiedAssociation": "was associated according to",
        "http://www.w3.org/ns/prov#qualifiedEnd": "was ended according to",
        "http://www.w3.org/ns/prov#qualifiedDelegation": "was delegated according to"
    }

    qualified_predicates = {
        "http://www.w3.org/ns/prov#Influence": {
            "http://www.w3.org/ns/prov#influencer": "entails influencing by",
            "http://www.w3.org/ns/prov#hadActivity": "entails influencing by", # Note the clash here!
            "http://www.w3.org/ns/prov#hadRole": "entails influencing as"
        },
        "http://www.w3.org/ns/prov#Generation": {
            "http://www.w3.org/ns/prov#activity": "entails generation by",
            "http://www.w3.org/ns/prov#atTime": "entails generation at",
        },
        "http://www.w3.org/ns/prov#Derivation": {
            "http://www.w3.org/ns/prov#entity": "entails derivation from",
            "http://www.w3.org/ns/prov#hadActivity": "entails derivation by",
            "http://www.w3.org/ns/prov#hadUsage": "entails derivation using a source according to",
            "http://www.w3.org/ns/prov#hadGeneration": "entails derivation generating a derivative according to"
        },
        "http://www.w3.org/ns/prov#PrimarySource": {
            "http://www.w3.org/ns/prov#entity": "entails derivation primarily from",
            "http://www.w3.org/ns/prov#hadActivity": "entails derivation by",
            "http://www.w3.org/ns/prov#hadUsage": "entails derivation primarily using a source according to",
            "http://www.w3.org/ns/prov#hadGeneration": "entails derivation generating a derivative according to"
        },
        "http://www.w3.org/ns/prov#Quotation": {
            "http://www.w3.org/ns/prov#entity": "entails quotation from",
            "http://www.w3.org/ns/prov#hadActivity": "entails quotation by",
            "http://www.w3.org/ns/prov#hadUsage": "entails quotation using a source according to",
            "http://www.w3.org/ns/prov#hadGeneration": "entails quotation generating a derivative according to"   
        },
        "http://www.w3.org/ns/prov#Revision": {
            "http://www.w3.org/ns/prov#entity": "entails revision from",
            "http://www.w3.org/ns/prov#hadActivity": "entails revision by",
            "http://www.w3.org/ns/prov#hadUsage": "entails revision using a source according to",
            "http://www.w3.org/ns/prov#hadGeneration": "entails revision generating a derivative according to"  
        },
        "http://www.w3.org/ns/prov#Attribution": {
            "http://www.w3.org/ns/prov#agent": "entails attribution to"
        },
        "http://www.w3.org/ns/prov#Invalidation": {
            "http://www.w3.org/ns/prov#activity": "entails invalidation by",
            "http://www.w3.org/ns/prov#atTime": "entails invalidation at"
        },
        "http://www.w3.org/ns/prov#Start": {
            "http://www.w3.org/ns/prov#hadActivity": "entails generation of a trigger by",
            "http://www.w3.org/ns/prov#atTime": "entails starting at",
            "http://www.w3.org/ns/prov#entity": "entails triggering by"
        },
        "http://www.w3.org/ns/prov#Usage": {
            "http://www.w3.org/ns/prov#atTime": "entails usage at",
            "http://www.w3.org/ns/prov#entity": "entails usage of"
        },
        "http://www.w3.org/ns/prov#Communication": {
            "http://www.w3.org/ns/prov#activity": "entails informing by"
        },
        "http://www.w3.org/ns/prov#Association": {
            "http://www.w3.org/ns/prov#hadPlan": "entails association planned according to",
            "http://www.w3.org/ns/prov#hadRole": "entails association as",
            "http://www.w3.org/ns/prov#agent": "entails association with"
        },
        "http://www.w3.org/ns/prov#End": {
            "http://www.w3.org/ns/prov#hadActivity": "entails generation of a trigger by",
            "http://www.w3.org/ns/prov#atTime": "entails ending at",
            "http://www.w3.org/ns/prov#entity": "entails triggering by"
        },
        "http://www.w3.org/ns/prov#Delegation": {
            "http://www.w3.org/ns/prov#hadActivity": "entails delegation of",
            "http://www.w3.org/ns/prov#agent": "entails delegation by"
        }
    }
