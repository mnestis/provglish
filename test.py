#!/usr/bin/python

import rdflib
from provglish import transform
from provglish import prov

from random import randint

from sys import argv

graph = rdflib.graph.ConjunctiveGraph()
print "Parsing input file:", argv[1]
graph.parse(argv[1],format="turtle", publicID="prov_graph")
print "Loading the PROV ontology."
prov.load_prov_ontology(graph)

print "Instantiating the transform engine."
tran = transform.Transformer()
tran.register_template(transform.definitions)
tran.register_template(transform.properties)
tran.register_template(transform.two_props)

print "Generating all possible sentences."
all_sentences = tran.render_graph(graph)

print "Removing duplicates."
## Dict: hashes
## Key: the hash of the coverage
## Value: a list of sentences whose coverage matches that hash
hashes = {}
for sentence in all_sentences:
    if sentence.coverage_hash not in hashes:
        hashes[sentence.coverage_hash] = [sentence]
    else:
        hashes[sentence.coverage_hash].append(sentence)

## Remove sentences that cover the same triple  
sentences_pool = [] 
        
for key in hashes:
    sentences_pool.append(hashes[key][randint(0, len(hashes[key])-1)])

print "Choosing the right sentences."
## Dict: to_be_covered
## Key: triple
## Value: a list of sentences that can cover that triple
to_be_covered = {}

for sentence in sentences_pool:
    for triple in sentence.coverage:
        if triple not in to_be_covered:
            to_be_covered[triple] = [sentence]
        else:
            to_be_covered[triple].append(sentence)

def choose_sentence(to_be_covered, sentences_pool):
    # If there's a triple that can only be covered by one sentence, we must pick that sentence.
    for triple in to_be_covered:
        if len(to_be_covered[triple])==1:
            return to_be_covered[triple][0]
    
    # Now we pick the sentence with the greatest coverage
    biggest = (0, None)
    for sentence in sentences_pool:
        if len(sentence.coverage) > biggest[0]:
            biggest = (len(sentence.coverage), sentence)
    
    return biggest[1]

chosen_sentences = [] # A list that will hold the sentences we choose

while to_be_covered:
    chosen_sentence = choose_sentence(to_be_covered, sentences_pool)
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
                sentences_pool.remove(sentence)
        # Remove any triples it covers from to_be_covered
        if triple in to_be_covered:
            del to_be_covered[triple]
    
    if chosen_sentence in sentences_pool:
        sentences_pool.remove(chosen_sentence)
            
print "Writing output to:", argv[2]            
output_file = open(argv[2], "w")
output_file.writelines([str(sentence)+"\n" for sentence in chosen_sentences])
output_file.flush()
output_file.close()
