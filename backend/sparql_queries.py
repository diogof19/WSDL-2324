from SPARQLWrapper import SPARQLWrapper, JSON
from models.artist import Artist

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

def search_and_save(query, endpoint_name, results):
    sparql = SPARQLWrapper(endpoints[endpoint_name])
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    ret = sparql.query().convert()
    
    for r in ret["results"]["bindings"]:
        #Check if the artist is already in the results
        found = False
        for result in results:
            if result.name == r['artist_name']['value']:
                found = True
                result.add_uri(endpoint_name, r['artist']['value'])
                
                if 'image' in r and not result.has_thumbnail():
                    result.add_thumbnail(r['image']['value'])
                
                break
            
        if found:
            continue
        
        artist = Artist(r['artist_name']['value'])
        artist.add_uri(endpoint_name, r['artist']['value'])
        
        if 'image' in r:
            artist.add_thumbnail(r['image']['value'])
        
        results.append(artist)

def artist_search(search_term):
    results = []
    
    #DBPedia
    query = """
        %s

        SELECT DISTINCT ?artist (SAMPLE(?artist_name) AS ?artist_name) ?image WHERE {
            ?artist rdf:type dbo:Person, dbo:Artist;
                rdfs:label ?artist_name.
            OPTIONAL {
                ?artist dbo:thumbnail ?image.
            }
            FILTER regex(?artist_name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    #search_and_save(query, 'dbpedia', results)
    
    #Getty Museum
    query = """
        %s
        
        SELECT DISTINCT ?artist ?artist_name WHERE {
            ?artist rdf:type crm:E21_Person ;
                rdfs:label ?artist_name .
            FILTER regex(?artist_name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    #search_and_save(query, 'getty', results)
    
    #Smithsonian Museum
    #DIDN'T TEST BECAUSE ENDPOINT IS DOWN
    query = """
        %s
        
        SELECT DISTINCT ?artist ?artist_name WHERE {
            ?artist rdf:type la:Actor ;
                rdfs:label ?artist_name .
            FILTER regex(?artist_name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    #search_and_save(query, 'smithsonian', results)
    
    #Wikidata
    query = """
        %s
        
        SELECT DISTINCT ?artist ?artist_name WHERE {
            ?artist wdt:P31 wd:Q5 ;
                rdfs:label ?artist_name .
            FILTER regex(?artist_name, ".*%s.*", "i")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
        }
    """ % (prefixes, search_term)

    search_and_save(query, 'wikidata', results)
    
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
    results = artist_search("Vincent")
    for result in results:
        print(result.name)
        print(result.uris)
        print(result.thumbnail)
        print()
except Exception as e:
    print(e)