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
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX la: <https://linked.art/ns/terms/>
    PREFIX getty: <http://data.getty.edu/local/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
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

def artist_search(search_term):
    results = {'getty': [], 'dbpedia': []}
    
    #Getty Museum
    query = """
        %s
        
        SELECT DISTINCT ?artist ?artist_name WHERE {
            ?artist rdf:type crm:E21_Person ;
                rdfs:label ?artist_name .
            FILTER regex(?artist_name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    sparql = SPARQLWrapper(endpoints['getty'])
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    ret = sparql.query().convert()
    
    for r in ret["results"]["bindings"]:
        results['getty'].append(r)
    
    """ print("Endpoint: getty")
    for r in ret["results"]["bindings"]:
        print(r) """
        
    #DBPedia
    query = """
        %s

        SELECT DISTINCT ?artist (SAMPLE(?artist_name) AS ?sample_name) WHERE {
            ?artist rdf:type dbo:Person, dbo:Artist;
                rdfs:label ?artist_name.
            FILTER regex(?artist_name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    sparql = SPARQLWrapper(endpoints['dbpedia'])
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    ret = sparql.query().convert()
    
    for r in ret['results']['bindings']:
        results['dbpedia'].append(r)
    
    """ print("Endpoint: dbpedia")
    for r in ret["results"]["bindings"]:
        print(r) """
        
    return results

'''
Info we want from the artist:
- Name                          Getty Museum, DBPedia
- Birth date                    Getty Museum, DBPedia
- Death date (if applicable)    Getty Museum, DBPedia
- Birth place                   Getty Museum, DBPedia
- Death place (if applicable)   Getty Museum, DBPedia
- Description                   Getty Museum, DBPedia
- Image (if possible)           Getty Museum, DBPedia
- Artworks                      Getty Museum, DBPedia
- Exhibitions (if applicable)   Getty Museum

'''
def retrieve_artist_info(artist_uri):
    
    #Getty Museum
    query = """
        %s
        
        SELECT * WHERE {
            <%s> rdfs:label ?artist_name ;
                crm:P98i_was_born ?birth_place ;
                crm:P100i_died_in ?death_place ;
                crm:P1_is_identified_by ?description ;
                crm:P1_is_identified_by ?image .
        }
    """ % (prefixes, artist_uri)
    
    
    return

try:
    """ for endpoint in endpoints:
        sparql = SPARQLWrapper(endpoints[endpoint])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        ret = sparql.query().convert()

        print("Endpoint: %s" % endpoint)
        for r in ret["results"]["bindings"]:
            print(r) """
except Exception as e:
    print(e)