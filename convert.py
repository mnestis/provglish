#!/usr/bin/python

if __name__=="__main__":
	from sys import argv
	
	input_filename = argv[1]
	#output_filename = argv[2]
	
	from provglish import ce
	graph = ce.parse(input_filename, "turtle")
	ce.convert_graph(graph)
