from SPARQLWrapper import SPARQLWrapper, JSON

'''
Endpoints:
    - https://dbpedia.org/sparql
    - https://data.getty.edu//museum/collection/sparql
    - https://api.triplydb.com/datasets/smithsonian/american-art-museum/services/american-art-museum/sparql
    - https://query.wikidata.org/sparql (we may or may not use this, it depends on how difficult it is to query the other endpoints)
'''
endpoints = {
    'dbpedia': 'https://dbpedia.org/sparql',
    'getty': 'https://data.getty.edu//museum/collection/sparql',
    'smithsonian': 'https://api.triplydb.com/datasets/smithsonian/american-art-museum/services/american-art-museum/sparql',
    'wikidata': 'https://query.wikidata.org/sparql'
}

prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX gvp: <http://vocab.getty.edu/ontology#>
    PREFIX aat: <http://vocab.getty.edu/aat/>
    PREFIX ulan: <http://vocab.getty.edu/ulan/>
    PREFIX tgn: <http://vocab.getty.edu/tgn/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""

query = """
    %s
    
    SELECT * WHERE {
        ?sub r
        {
            ?sub rdfs:label "Vincent van Gogh".
        } UNION {
            ?sub rdfs:label "Vincent van Gogh"@en.
        }
    } LIMIT 2
""" % prefixes

try:
    for endpoint in endpoints:
        sparql = SPARQLWrapper(endpoints[endpoint])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        ret = sparql.query().convert()

        print("Endpoint: %s" % endpoint)
        for r in ret["results"]["bindings"]:
            print(r)
except Exception as e:
    print(e)