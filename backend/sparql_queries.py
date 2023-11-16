from SPARQLWrapper import SPARQLWrapper, JSON, XML, CSV
from models.artist import Artist

'''
Endpoints:
    - https://dbpedia.org/sparql
    - https://data.getty.edu//museum/collection/sparql
    - https://api.triplydb.com/datasets/smithsonian/american-art-museum/services/american-art-museum/sparql
      http://localhost:8890/sparql
    - https://query.wikidata.org/sparql (we may or may not use this, it depends on how difficult it is to query the other endpoints)
'''
endpoints = {
    'dbpedia': 'https://dbpedia.org/sparql',
    'getty': 'https://data.getty.edu//museum/collection/sparql',
    'smithsonian': 'http://localhost:8890/sparql',
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
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX purl: <http://purl.org/dc/elements/1.1/>
    PREFIX gettyth: <https://data.getty.edu/local/thesaurus/>
"""

def search_and_save(query, endpoint_name, results):
    sparql = SPARQLWrapper(endpoints[endpoint_name])
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    
    ret = sparql.query().convert()
    
    for r in ret["results"]["bindings"]:
        print(r)
    
    return
    
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
    
    query = """
        %s
        
        SELECT DISTINCT ?artist (SAMPLE(?artist_name) AS ?artist_name) WHERE {
            ?artist rdf:type cidoc:E39_Actor ;
              cidoc:P1_is_identified_by ?name.
            ?name rdfs:label ?artist_name.
            FILTER regex(?artist_name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    query = """
        describe <person-institution/4778>   
    """
    
    
    search_and_save(query, 'smithsonian', results)
    
    #Wikidata
    query = """
        %s
        
        SELECT DISTINCT ?artist ?artist_name WHERE {
            ?artist wdt:P31 ?professsion;
                rdfs:label ?artist_name .
            ?profession wdt:P31 wd:Q88789639.
            FILTER regex(?artist_name, ".*%s.*", "i")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
        }
    """ % (prefixes, search_term)
    
    '''
    SELECT DISTINCT ?artist ?artist_name WHERE {
        ?artist wdt:P106 ?professsion.
        ?profession wdt:P31 wd:Q88789639.
        ?artist wdt:P31 wd:Q5;
                rdfs:label ?artist_name .

        FILTER regex(?artist_name, ".*vincent.*", "i")
        FILTER(LANG(?artist_name) = "en")
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
    } LIMIT 20
    '''

    #search_and_save(query, 'wikidata', results)
    
    return results

'''
Info we want from the artist:
- Name                          Getty Museum, DBPedia, Smithsonian Museum
- Birth date                    Getty Museum, DBPedia, Smithsonian Museum
- Death date (if applicable)    Getty Museum, DBPedia, Smithsonian Museum
- Birth place                   Getty Museum, DBPedia, Smithsonian Museum
- Death place (if applicable)   Getty Museum, DBPedia, Smithsonian Museum
- Description                   Getty Museum, DBPedia, Smithsonian Museum
- Image (if possible)           Getty Museum, DBPedia,
- Artworks                      Getty Museum, DBPedia
- Exhibitions (if applicable)   Getty Museum

'''
def retrieve_artist_info(artist_uri):
    
    #Getty Museum
    
    # Artist info
    query = """
        %s
        
        SELECT ?name ?birthYear ?birthPlace ?deathYear ?deathPlace ?bibliography ?gettyLink WHERE {
            %s crm:P1_is_identified_by ?identify.
            ?identify a crm:E33_E41_Linguistic_Appellation;
                    crm:P190_has_symbolic_content ?name.

            %s crm:P98i_was_born ?born.
            ?born crm:P4_has_time-span ?birth_timespan.
            ?birth_timespan crm:P82a_begin_of_the_begin ?birthYear.

            %s crm:P67i_is_referred_to_by ?birth_referred.
            ?birth_referred crm:P2_has_type gettyth:birth-place-description;
                            crm:P190_has_symbolic_content ?birthPlace.

            OPTIONAL {
                %s crm:P100i_died_in ?death.
                ?death crm:P4_has_time-span ?death_timespan.
                ?death_timespan crm:P67i_is_referred_to_by ?death_referred.
                ?death_referred crm:P190_has_symbolic_content ?deathYear.

                %s crm:P67i_is_referred_to_by ?death_place_referred.
                ?death_place_referred crm:P2_has_type gettyth:death-place-description;
                                        crm:P190_has_symbolic_content ?deathPlace;

            }

            %s crm:P67i_is_referred_to_by ?bib_referred.
            ?bib_referred rdfs:label "Artist/Maker Biography";
                        purl:format "text/html"; #the other option is text/markdown
                        crm:P190_has_symbolic_content ?bibliography.

            %s crm:P129i_is_subject_of ?gettyLink.
            ?gettyLink crm:P2_has_type aat:300264578.
        }
    """ % (prefixes, artist_uri, artist_uri, artist_uri, artist_uri, artist_uri, artist_uri, artist_uri)
    
    #Artist artworks - but only the info needed as a thumbnail to link to the actual page
    query = """
        %s
        
        SELECT ?artWork ?name ?image WHERE {
            ?production crm:P14_carried_out_by %s.
            ?artWork crm:P108i_was_produced_by ?production;
                    crm:P1_is_identified_by ?identify;
                    crm:P138i_has_representation ?image.
            ?identify crm:P2_has_type gettyth:object-title-primary;
                        crm:P190_has_symbolic_content ?name.
        }
    """ % (prefixes, artist_uri)
    
    # Dbpedia
    
    query = """
        %s
        
        SELECT ?name ?birthDate ?birthPlace ?deathDate ?deathPlace ?bibliography ?wikipediaLink ?movement WHERE {
            %s dbo:birthName ?name;
               dbo:birthDate ?birthDate;
               dbo:birthPlace ?bPlace.
               
            ?bPlace dbp:name ?birthPlace.

            OPTIONAL {
                    %s dbo:deathDate ?deathDate;
                       dbo:deathPlace ?dPlace.
                    
                    ?dPlace dbp:name ?deathPlace.
                    
                    %s dbo:movement ?movementPage.
                    ?movementPage rdfs:label ?movement
                    FILTER langMatches(lang(?movement),'en')
            }

            %s dbo:abstract ?bibliography.
            FILTER langMatches(lang(?bibliography),'en')

            %s foaf:isPrimaryTopicOf ?wikipediaLink
        }
    """ % (prefixes, artist_uri, artist_uri, artist_uri, artist_uri, artist_uri)
    
    
    
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
    results = artist_search("alma thomas")
    for result in results:
        """ if result.uris.keys().__len__() < 2:
            continue """
        print(result.name)
        print(result.uris)
        print(result.thumbnail)
        print()
except Exception as e:
    print(e)