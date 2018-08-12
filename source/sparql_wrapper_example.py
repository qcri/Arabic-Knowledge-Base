"""Module that sends sparql queries and returns the response and the time
   Usage:
        python sparql_wrapper_example.py -e endpoint_URI -q query_file -f 
           return_format -o output_file  -t -v
        query_file: a file that contains a sparql query
        return_format: one of [json, xml, turtle, n3, rdf, rdfxml, csv, tsv]
    Example Usage:
        python sparql_wrapper_example.py -e "http://192.168.10.2:8890/sparql" 
            -q ../sparql-queries/query_1.rq -v -t
"""

__author__ = 'Aisha Mohamed'


import sys
import getopt
import time

from SPARQLWrapper import SPARQLWrapper

def execute_query(endpoint_URI, query, return_format=None):
    start_time = time.time()
    sparql = SPARQLWrapper(endpoint_URI)
    sparql.setQuery(query)
    if return_format:
        sparql.setReturnFormat(return_format)
    
    try:
        if return_format:
            results = sparql.query().convert() # string
        else:
            results = sparql.query() # string
        end_time = time.time() - start_time
    except Exception as e: 
        print("Failed to query", e)
        return
    print("The output as a string")
    print(results)
    print("Time = {} sec ".format(end_time))
    return results, time



def read_query_from_file(
        file="/home/amohamed/Arabic-Knowledge-Base/sparql-queries/query_1.rq"):
    file = open(file,"r")
    query = file.read()
    return query


def main(argv):
    endpoint_URI = "http://192.168.10.2:8890/sparql"
    query = read_query_from_file()
    return_format = None
    output_file = "sparql_response"
    time = True
    verbose = False
    try:
        opts, remainder = getopt.getopt(
            argv[1:], "e:q:f:o:tv",
            [
                "endpoint_URI=", "query_file=", "return_format=", 
                "output_file=", "time", "verbose"
                ]
            )
        for opt, arg in opts:
            if opt in ("-e", "--endpoint_URI"):
                endpoint_URI = arg
            elif opt in ("-q", "--query_file"):
                query = read_query_from_file(arg)
            elif opt in ("-f", "--return_format"):
                return_format = arg
            elif opt in ("-o", "--output_file"):
                output_file = arg
            elif opt in ('-v', '--verbose'):
                verbose = True
            elif opt in ('-t', '--time'):
                time = True
    except getopt.GetoptError:
        sys.exit("Usage: %s -e endpoint_URI -q query_file -f return_format -o \
            output_file" % sys.argv[0])

    if verbose:
        print(
            "{0}\n \
            endpoint_URI {1}\n \
            query {2}\n \
            return_format {3}\n \
            output_file {4}".format(
                argv[0], endpoint_URI, query, return_format, output_file)
            )
    execute_query(endpoint_URI, query, return_format)
    return


if __name__ == "__main__":
    main(sys.argv)


