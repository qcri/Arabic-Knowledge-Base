# Twitter Data statistics
## Summary
number of classes (entity types) = 3  
number of entities = 4,496,736  
number of relation types = 23  
number of triples = 40,584,729  

Note: All other entities like locations are treated as literal values with no properties describing them.


## Find the number of classes (entity types) in the graph
```sparql
PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX  dcterms: <http://purl.org/dc/terms/>
PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX  sioc: <http://rdfs.org/sioc/ns#>
PREFIX  sto:  <https://w3id.org/i40/sto#>

SELECT  (COUNT(DISTINCT ?class) AS ?numClasses)
WHERE
  { GRAPH <http://twitter.com/>
      {   { ?entity  rdf:type  ?class }
        UNION
          { ?entity  sioc:type  ?class }
      }
  }
```
The query ran in 0.948 sec and returned 3.
Note: The tweet doesn't have the ```rdf:type``` predicate. The excel ontology says it does. It is actually has the ```sioc:type``` predicate.

## Find the number of properties (relation types) in the graph
```sparql
PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX  dcterms: <http://purl.org/dc/terms/>
PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX  sioc: <http://rdfs.org/sioc/ns#>
PREFIX  sto:  <https://w3id.org/i40/sto#>

SELECT  COUNT(DISTINCT ?predicate)
WHERE
  { GRAPH <http://twitter.com/>
      { ?s  ?predicate  ?o }
  }
```
The query ran in 4.175 sec and returned 23 as the number of predicates currently in the database.

## Find the classes in the graph and thier frequncy
```sparql
PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX  dcterms: <http://purl.org/dc/terms/>
PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX  sioc: <http://rdfs.org/sioc/ns#>
PREFIX  sto:  <https://w3id.org/i40/sto#>

SELECT  ?class (count(*) AS ?class_frequency)
WHERE
  { GRAPH <http://twitter.com/>
      {   { ?entity  rdf:type  ?class }
        UNION
          { ?entity  sioc:type  ?class }
      }
  }
GROUP BY ?class
ORDER BY DESC(?class_frequency)
```
The query ran in 0.264 sec and returned the three classes in this Twitter graph:
```
http://rdfs.org/sioc/ns#microblogPost, 4,155,480
http://www.ontologydesignpatterns.org/ont/dul/IOLite.owl#MultimediaObject, 341,256
http://rdfs.org/sioc/types#UserAccount, 138,960
```

## Find the number of distinct entities and literals in the graph
```sparql
PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX  iol:  <http://www.ontologydesignpatterns.org/ont/dul/IOLite.owl#>
PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX  dcterms: <http://purl.org/dc/terms/>
PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX  sioc: <http://rdfs.org/sioc/ns#>
PREFIX  sto:  <https://w3id.org/i40/sto#>

SELECT  (COUNT(DISTINCT ?s) AS ?numEntities)
WHERE
  { GRAPH <http://twitter.com/>
      {   { ?s  rdf:type  sioc:UserAccount }
        UNION
          { ?s  sioc:type  sioc:microblogPost }
        UNION
          { ?s  rdf:type  iol:MultimediaObject }
      }
  }
```
The query ran in 3.39 sec and returned 4,496,736
The total number of subjects and objects is 17,446,226

1 Rows. -- 72683 msec.

## Find the predicates (relation types) and their frequencies
```sparql
set blobs on;
SPARQL define output:format "CSV"
PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX  dcterms: <http://purl.org/dc/terms/>
PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX  sioc: <http://rdfs.org/sioc/ns#>
PREFIX  sto:  <https://w3id.org/i40/sto#>

SELECT  ?predicate (count(*) AS ?predicate_frequency)
WHERE
  { GRAPH <http://twitter.com/>
      { ?s  ?predicate  ?o }
  }
GROUP BY ?predicate
ORDER BY DESC(?predicate_frequency)
```
The query ran in 0.183 sec and returned 23 predictaes and their freqency
```
"predicate","predicate_frequency"
"http://rdfs.org/sioc/ns#id",4635699
"http://purl.org/dc/terms/language",4294467
"http://purl.org/dc/terms/created",4294443
"http://rdfs.org/sioc/ns#content",4155737
"http://rdfs.org/sioc/ns#has_creator",4155480
"http://rdfs.org/sioc/ns#type",4155480
"https://w3id.org/seas/device",3888586
"http://rdfs.org/sioc/ns#mentions",3025232
"http://purl.org/dc/terms/references",2556731
"https://w3id.org/i40/sto#hasTag",1571946
"http://rdfs.org/sioc/ns#links_to",889577
"http://rdfs.org/sioc/ns#reply_of",509280
"http://rdfs.org/sioc/ns#link",482302
"http://www.w3.org/1999/02/22-rdf-syntax-ns#type",480216
"http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#mediaType",341256
"http://rdfs.org/sioc/ns#creator_of",239574
"http://www.geonames.org/ontology#locatedIn",149853
"http://rdfs.org/sioc/ns#avatar",140653
"http://xmlns.com/foaf/0.1/name",139756
"http://rdfs.org/sioc/ns#has_group",138961
"http://rdfs.org/sioc/ns#name",138960
"http://rdfs.org/sioc/ns#description",115035
"http://www.w3.org/ns/prov#wasQuotedFrom",85505
```
Note: In the ontology: ```sioc:follows``` and some other predicates are in the ontology but don't occur in the graph.

## Find the number of triples in the graph
```sparql
PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX  dcterms: <http://purl.org/dc/terms/>
PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX  sioc: <http://rdfs.org/sioc/ns#>
PREFIX  sto:  <https://w3id.org/i40/sto#>

SELECT  (COUNT(?s) AS ?triples)
WHERE
  { GRAPH <http://twitter.com/>
      { ?s  ?p  ?o }
  }
```
The query ran in 0.076 sec and returned 40584729.