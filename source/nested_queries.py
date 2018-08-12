"""Module that sends nested sparql queries and returns the response and the time
   Usage:
        python sparql_wrapper_example.py -e endpoint_URI -i inner_query_file -o 
           outer_query_file -f return_format -t -v
        inner_query_file: a file that contains a sparql query
        return_format: one of [json, xml, turtle, n3, rdf, rdfxml, csv, tsv]
    Example Usage:
        python sparql_wrapper_example.py -e "http://192.168.10.2:8890/sparql" 
            -i ../sparql-queries/inner_query.rq -o outer_query -v -t

NOTE:
- nested queries shouldn't contain order by ?result_of_inner_query
- nested queries that contain non english letters are not accepted 
- nested queries shouldn't project the ?result_of_inner_query
- know how to replace the link with a prefix in the returned inner result 
    (use regular expressions) to parse, how to assign the prefixes?,
    should I keep a dict of all prefixes in a query or for an endpoint?
- records that has , in it. Eg: :Worcester,_Massachusetts
"""

__author__ = 'Aisha Mohamed'


import sys
import getopt
import time
from cStringIO import StringIO
import csv
import re

import pandas as pd
from SPARQLWrapper import SPARQLWrapper


def read_query(
        file="/home/amohamed/Arabic-Knowledge-Base/sparql-queries/query_1.rq"):
    file = open(file,"r")
    query = file.read()
    return query


def remove_prefix(record, query):
    prefix, record = record[:record.rfind("/")+1] , record[record.rfind("/")+1]
    if prefix == "<http://dbpedia.org/resource/>":
        return "", ":"+record
    elif prefix == "http://ar.dbpedia.org/resource/":
        prefix_statement = "PREFIX ar: <http://ar.dbpedia.org/resource/>"
        return prefix_statement, "ar:"+record
    elif prefix == "http://bg.dbpedia.org/resource/":
        prefix_statement = "PREFIX bg: <http://ar.dbpedia.org/resource/>"
        return prefix_statement, "bg:"+record
    return "", ":"+record


def nested_query(endpoint_URI, inner_query, outer_query,
    return_format=None, time_query=True, verbose=False):
    start_time = time.time()
    sparql = SPARQLWrapper(endpoint_URI)

    # Do the inner query
    sparql.setQuery(inner_query)
    sparql.setReturnFormat('csv')

    try:            
        inner_result = sparql.query().convert() # string
        inner_time = time.time() - start_time
    except Exception as e: 
        print("Failed to send the inner query", e)
        return

    # Convert the result of the inner query to a data frame
    inner_result_file = StringIO(inner_result)
    # reset the pointer first
    inner_result_file.seek(0)
    inner_df = pd.read_csv(inner_result_file, sep=',') # to get the values and the header: # print df
    header = inner_df.columns.values[0]

    if verbose:
        print("Finneshed the inner query ")
        print("    Inner query time = {} sec ".format(inner_time))
        print("    Inner query response size = {} rows ".format(inner_df.shape[0]))
    
    successes = 0 # Number of successful queries
    failures = 0 # Number of Failed queries
    outer_frames = [] # a list of the returned dataframes for each recored
    outer_start_time = time.time()
    for col, row in inner_df.iterrows():
        record = row[header]
        if ",_" in record:
            record = record[:record.find(",_")]
        #prefixes, record = remove_prefix(record, outer_query)
        #query = prefixes + outer_query.replace("?"+header, record)
        query = outer_query.replace("?"+header, record.replace("http://dbpedia.org/resource/", ":"))
        print query
        sparql.setQuery(query)
        sparql.setReturnFormat('csv')        
        try:            
            result = sparql.query().convert() # string
            # Convert the result of the inner query to a data frame
            result_file = StringIO(result)
            # reset the pointer first
            result_file.seek(0)
            df = pd.read_csv(result_file, sep=',') # to get the values and the header: # print df
            df[header] = record.replace("http://dbpedia.org/resource/", "")
            outer_frames.append(df)
            successes = successes + 1
        except Exception as e: 
            print("Failed to send the query", e)
            failures = failures + 1
            print(failures)
            continue
    
    final_df = pd.concat(outer_frames)
    end_time = time.time()
    if verbose:
        print("Finneshed the outer query ")
        print("    Outer query time = {} sec ".format(end_time - outer_start_time))
        print("    Total nested query time = {} sec ".format(end_time - start_time))
        print("    Final query response size = {} rows ".format(final_df.shape[0]))
        print(successes, failures)
        print(final_df.columns)
    
    final_df.to_csv('out.csv', index=False)
    return


def main(argv):
    endpoint_URI = "http://192.168.10.2:8890/sparql"
    inner_query = read_query()
    return_format = None
    outer_query = ""
    time_query = True
    verbose = False
    try:
        opts, remainder = getopt.getopt(
            argv[1:], "e:i:o:f:tv",
            [
                "endpoint_URI=", "i_query_file=", "o_query_file=", 
                "return_format=", "time", "verbose"
                ]
            )
        for opt, arg in opts:
            if opt in ("-e", "--endpoint_URI"):
                endpoint_URI = arg
            elif opt in ("-i", "--i_query_file"):
                inner_query = read_query(arg)
            elif opt in ("-o", "--o_query_file"):
                outer_query = read_query(arg)
            elif opt in ("-f", "--return_format"):
                return_format = arg
            elif opt in ('-v', '--verbose'):
                verbose = True
            elif opt in ('-t', '--time'):
                time_query = True
    except getopt.GetoptError:
        sys.exit("Usage: %s -e endpoint_URI -i innner_query_file -f return_format -o \
            outer_query_file" % sys.argv[0])

    if verbose:
        print(
            "{0}\n \
            endpoint_URI {1}\n \
            inner_query {2}\n \
            outer_query {3}\n \
            return_format {4}".format(
                argv[0], endpoint_URI, inner_query, outer_query, return_format))
    nested_query(endpoint_URI, inner_query, outer_query, return_format, 
        time_query, verbose)
    return


if __name__ == "__main__":
    main(sys.argv)
