# Common Queries for ML tasks 
This document highlights some of the most common knowldge-base queries for machine learning tasks. It discusses the implementation and performance of these queries in sparql.

For the initial experiment: I am using
Sparql Client: isql
Sparql Server: Virtuoso Open Link

The document outline:
* Exploring the Dataset
* Section 2
    * Subsection 2.1
* Section 3

## Exploring the Dataset

### Finding all the classes and the number of instances of each class

```sparql
SELECT ?class (count(?instance) as ?numberOfInstances) 
WHERE {
    ?instance a ?class .
}
group by ?class
order by desc(?numberOfInstances)
```

## Section 2

## Section 3


***
conclusion