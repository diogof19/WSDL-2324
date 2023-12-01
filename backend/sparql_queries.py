from SPARQLWrapper import SPARQLWrapper, JSON, XML, CSV
from models.artist import Artist
from models.artwork import Artwork
from globals import BACKUP_DATABASE_HOST

import os

f'''
Endpoints:
    - https://dbpedia.org/sparql
    - https://data.getty.edu//museum/collection/sparql
    - https://api.triplydb.com/datasets/smithsonian/american-art-museum/services/american-art-museum/sparql
      http://{BACKUP_DATABASE_HOST}:8890/sparql
    - https://query.wikidata.org/sparql (we may or may not use this, it depends on how difficult it is to query the other endpoints)
'''

endpoints = {
    'dbpedia': 'https://dbpedia.org/sparql',
    'getty': 'https://data.getty.edu//museum/collection/sparql',
    'smithsonian': f'http://{BACKUP_DATABASE_HOST}:8890/sparql',
    'wikidata': 'https://query.wikidata.org/sparql',
    'getty_vocab': 'https://vocab.getty.edu/sparql'
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
    PREFIX dbp: <http://dbpedia.org/property/>
"""

def search_and_save(query, endpoint_name, results, result_type):
    sparql = SPARQLWrapper(endpoints[endpoint_name])
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    
    ret = sparql.query().convert()
    
    for r in ret["results"]["bindings"]:
        #Check if the artist is already in the results
        match_id = None

        if endpoint_name == 'getty' and 'exact_match' in r:
            query = """
                %s

                SELECT DISTINCT ?exact_match WHERE {
                    <%s> skos:exactMatch ?exact_match.
                    FILTER regex(str(?exact_match),"^https:\\\\/\\\\/wikidata\\\\.org\\\\/.*", "i")
                }
            """ % (prefixes, r['exact_match']['value'])

            sparql = SPARQLWrapper(endpoints['getty_vocab'])
            sparql.setReturnFormat(JSON)
            sparql.setQuery(query)

            ret_2 = sparql.query().convert()

            print(ret_2)

            match_id = ret_2['results']['bindings'][0]['exact_match']['value'].split('/')[-1]

        found = False

        for result in results:
            if endpoint_name == 'getty' and 'wikidata' in result.uris and match_id == result.uris['wikidata'].split('/')[-1]:
                found = True

                result.add_uri(endpoint_name, r['uri']['value'])

                if 'image' in r and (not result.has_image() or 'Redirect/file' in result.image):
                    result.add_image(r['image']['value'])
            elif endpoint_name == 'saam' and r['dbpedia']['value'] == result.uris['dbpedia']:
                found = True

                result.add_uri(endpoint_name, r['saam']['value'])

                if 'image' in r and (not result.has_image() or 'Redirect/file' in result.image):
                    result.add_image(r['image']['value'])

            break                
            
        if found:
            continue
        
        artist = result_type(r['name']['value'])
        artist.add_uri(endpoint_name, r['uri']['value'])
        
        if 'image' in r:
            artist.add_image(r['image']['value'])

        if 'wikidata' in r:
            artist.add_uri('wikidata', r['wikidata']['value'])
        else:
            print(r)
        
        results.append(artist)
        

def artist_search(search_term):
    results = []

    search_term = '.*'.join(search_term.split(' '))
    
    #DBPedia
    query = """
        %s

        SELECT DISTINCT ?uri (SAMPLE(?name) AS ?name) ?image ?wikidata WHERE {
            ?uri rdf:type dbo:Person, dbo:Artist;
                rdfs:label ?name.
            OPTIONAL {
                ?uri owl:sameAs ?wikidata.
                FILTER regex(?wikidata, "^http:\\\\/\\\\/www\\\\.wikidata\\\\.org\\\\/.*", "i")
            }
            OPTIONAL {
                ?uri dbo:thumbnail ?image.
            }
            ?redirect dbo:wikiPageRedirects ?uri
            FILTER (regex(?redirect, ".*%s.*", "i") || regex(?name, ".*%s.*", "i"))
            FILTER (lang(?name) = "en")  
        }
    """ % (prefixes, search_term, search_term)
    
    search_and_save(query, 'dbpedia', results, Artist)
    
    #Getty Museum
    query = """
        %s
        
        SELECT DISTINCT ?uri ?name ?exact_match WHERE {
            ?uri rdf:type crm:E21_Person;
                rdfs:label ?name.
            OPTIONAL {
                ?uri skos:exactMatch ?exact_match.
                FILTER regex(str(?exact_match), "^http:\\\\/\\\\/vocab\\\\.getty\\\\.edu\\\\/.*", "i")
            }
            FILTER regex(?name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    search_and_save(query, 'getty', results, Artist)
    
    #Smithsonian Museum
    
    query = """
        %s
        
        SELECT DISTINCT ?uri (SAMPLE(?name) AS ?name) ?dbpedia WHERE {
            ?uri rdf:type cidoc:E39_Actor;
              cidoc:P1_is_identified_by ?name.
            OPTIONAL {
                ?uri owl:sameAs ?dbpedia.
                FILTER regex(?dbpedia, "^http:\\\\/\\\\/dbpedia\\\\.org\\\\/.*", "i")
            }
            ?name rdfs:label ?name.
            FILTER regex(?name, ".*%s.*", "i")
            FILTER (lang(?name) = "en")
        }
    """ % (prefixes, search_term)
    
    search_and_save(query, 'smithsonian', results, Artist)

    #Wikidata
    query = """
        %s
        
        SELECT DISTINCT ?uri ?name WHERE {
            ?uri wdt:P31 ?profession;
                rdfs:label ?name .
            ?profession wdt:P31 wd:Q88789639.
            FILTER regex(?name, ".*%s.*", "i")
            FILTER (lang(?name) = "en")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
        }
    """ % (prefixes, search_term)
    
    '''
    SELECT DISTINCT ?uri ?name WHERE {
        ?uri wdt:P106 ?profession.
        ?profession wdt:P31 wd:Q88789639.
        ?uri wdt:P31 wd:Q5;
                rdfs:label ?name .

        FILTER regex(?name, ".*vincent.*", "i")
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
    } LIMIT 20
    '''

    #search_and_save(query, 'wikidata', results, Artist)

    return results

def artwork_search(search_term):
    results = []

    search_term = '.*'.join(search_term.split(' '))

    #DBPedia
    query = """
        %s

        SELECT DISTINCT ?uri ?name ?image ?wikidata WHERE {
            ?uri rdf:type dbo:Artwork;
                rdfs:label ?name.
            OPTIONAL {
                ?uri owl:sameAs ?wikidata.
                FILTER regex(?wikidata, "^http:\\\\/\\\\/www\\\\.wikidata\\\\.org\\\\/.*", "i")
            }
            OPTIONAL {
                ?uri dbo:thumbnail ?image.
            }
            ?redirect dbo:wikiPageRedirects ?uri
            FILTER (regex(?redirect, ".*%s.*", "i") || regex(?name, ".*%s.*", "i"))
            FILTER (lang(?name) = "en")
        }
    """ % (prefixes, search_term, search_term)

    search_and_save(query, 'dbpedia', results, Artwork)

    #Getty Museum
    query = """
        %s

        SELECT DISTINCT ?uri ?name ?image ?exact_match WHERE {
            ?uri rdf:type crm:E22_Human-Made_Object;
                rdfs:label ?name.
            OPTIONAL {
                ?uri skos:exactMatch ?exact_match.
                FILTER regex(str(?exact_match), "^http:\\\\/\\\\/vocab\\\\.getty\\\\.edu\\\\/.*", "i")
            }
            OPTIONAL {                
                ?uri getty:thumbnailUrl ?image.
            }
            FILTER regex(?name, ".*%s.*", "i")
            FILTER (lang(?name) = "en")
        }
    """ %  (prefixes, search_term)

    #search_and_save(query, 'getty', results, Artwork)

    #Smithsonian Museum 
    #TODO: I don't know if this is the right query has_representation does seem to work
    query = """
        %s
        
        SELECT DISTINCT ?uri (SAMPLE(?name) AS ?name) ?image WHERE {
            ?uri rdf:type cidoc:E22_Man-Made_Object;
                rdfs:label ?name.
            OPTIONAL {
                ?uri owl:sameAs ?dbpedia;
                FILTER regex(?dbpedia, "^http:\\\\/\\\\/dbpedia\\\\.org\\\\/.*", "i")
            }
            OPTIONAL {
                ?uri cidoc:P138i_has_representation ?image.
            }
            FILTER regex(?name, ".*%s.*", "i")
            FILTER (lang(?name) = "en")
        }
    """ % (prefixes, search_term)
    
    #search_and_save(query, 'smithsonian', results, Artwork)

    #Wikidata
    query = """
        %s

        SELECT DISTINCT ?uri ?name ?image WHERE {
            ?uri wdt:P31 wd:Q3305213;
                wdt:P1476 ?name.
            OPTIONAL {
                ?uri wdt:P18 ?image.
            }
            FILTER regex(?name, ".*%s.*", "i")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
            }
    """ % (prefixes, search_term)

    #search_and_save(query, 'wikidata', results, Artwork)

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
def retrieve_artist_info(uris: dict):
    for key in uris.keys():
        uris[key] = '<%s>' % uris[key]
    
    # TO DO: 
    # - birthPlace may have multiple values
    # - birthName doesn't always exist
    if 'dbpedia' in uris.keys():
        query = """
        %s
        
        SELECT ?name ?image ?birthDate ?birthPlace ?deathDate ?deathPlace ?biography ?wikipediaLink ?movement WHERE {
            %s dbo:birthName ?name;
               dbo:birthDate ?birthDate;
               dbo:birthPlace ?bPlace.
               
            ?bPlace dbp:name ?birthPlace.

            OPTIONAL {
                %s dbo:thumbnail ?image.
            }
            
            OPTIONAL {
                %s dbo:deathDate ?deathDate;
                    dbo:deathPlace ?dPlace.
                ?dPlace dbp:name ?deathPlace.
            }
            
            OPTIONAL {
                %s dbo:movement ?movementPage.
                ?movementPage rdfs:label ?movement.
                FILTER langMatches(lang(?movement),'en')
            }

            %s dbo:abstract ?biography.
            FILTER langMatches(lang(?biography),'en')

            %s foaf:isPrimaryTopicOf ?wikipediaLink
        }
        """ % (prefixes, uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'])
        
        print(query)
                        
        sparql = SPARQLWrapper(endpoints['dbpedia'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artist_result = ret["results"]["bindings"][0]
        
        artist = Artist(artist_result['name']['value'])    
        artist.add_uri('dbpedia', uris['dbpedia'])
        artist.add_birth_date(artist_result['birthDate']['value'])
        artist.add_birth_place(artist_result['birthPlace']['value'])
        if 'deathDate' in artist_result:
            artist.add_death_date(artist_result['deathDate']['value'])
        if 'deathPlace' in artist_result:
            artist.add_death_place(artist_result['deathPlace']['value'])
        artist.add_biography('dbpedia', artist_result['biography']['value'])
        artist.add_movement(artist_result['movement']['value'])
        artist.add_wikipedia_link(artist_result['wikipediaLink']['value'])
        artist.add_image(artist_result['image']['value'])
    
    
    if 'getty' in uris.keys():
        query = """
        %s
        
        SELECT ?name ?birthYear ?birthPlace ?deathYear ?deathPlace ?biography ?gettyLink WHERE {
            %s crm:P1_is_identified_by ?identify.
            ?identify a crm:E33_E41_Linguistic_Appellation;
                    crm:P190_has_symbolic_content ?name.

            OPTIONAL {
                %s crm:P98i_was_born ?born.
                ?born crm:P4_has_time-span ?birth_timespan.
                ?birth_timespan crm:P82a_begin_of_the_begin ?birthYear.
            }

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
                        crm:P190_has_symbolic_content ?biography.

            %s crm:P129i_is_subject_of ?gettyLink.
            ?gettyLink crm:P2_has_type aat:300264578.
        }
        """ % (prefixes, uris['getty'], uris['getty'], uris['getty'], uris['getty'], uris['getty'], uris['getty'], uris['getty'])
        
        sparql = SPARQLWrapper(endpoints['getty'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artist_result = ret["results"]["bindings"][0]
        
        if 'artist' not in locals():
            artist = Artist(artist_result['name']['value'])
            artist.add_birth_date(artist_result['birthYear']['value'])
            artist.add_birth_place(artist_result['birthPlace']['value'])
            if 'deathYear' in artist_result:
                artist.add_death_date(artist_result['deathYear']['value'])
            if 'deathPlace' in artist_result:
                artist.add_death_place(artist_result['deathPlace']['value'])
        
        artist.add_uri('getty', uris['getty'])
        artist.add_biography('getty', artist_result['biography']['value'])
        artist.add_getty_link(artist_result['gettyLink']['value'])
        
    if 'smithsonian' in uris.keys():
        query = """
        %s

        SELECT ?name ?birthYear ?birthPlace ?deathYear ?deathPlace (GROUP_CONCAT(?bio;separator="\n") AS ?biography) WHERE {
            %s rdfs:label ?name;
               cidoc:P92i_was_brought_into_existence_by ?birth.
            
            ?birth cidoc:P4_has_time-span ?birthSpan;
                   cidoc:P7_took_place_at ?birthPlaceAt.
            ?birthSpan rdfs:label ?birthYear.
            ?birthPlaceAt rdfs:label ?birthPlace.
            
            OPTIONAL {
                %s cidoc:P93i_was_taken_out_of_existence_by ?death.
                ?death cidoc:P4_has_time-span ?deathSpan;
                       cidoc:P7_took_place_at ?deathPlaceAt.
                ?deathSpan rdfs:label ?deathYear.
                ?deathPlaceAt rdfs:label ?deathPlace.
                
                %s cidoc:P129i_is_subject_of ?subjectOf.
                ?subjectOf cidoc:P2_has_type aat:300080102;
                           rdf:value ?bio.
            }
        }
        """ % (prefixes, uris['smithsonian'], uris['smithsonian'], uris['smithsonian'])
    
        sparql = SPARQLWrapper(endpoints['smithsonian'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artist_result = ret["results"]["bindings"][0]
        
        if 'artist' not in locals():
            artist = Artist(artist_result['name']['value'])
            artist.add_birth_date(artist_result['birthYear']['value'])
            artist.add_birth_place(artist_result['birthPlace']['value'])
            if 'deathYear' in artist_result:
                artist.add_death_date(artist_result['deathYear']['value'])
            if 'deathPlace' in artist_result:
                artist.add_death_place(artist_result['deathPlace']['value'])
        
        artist.add_biography('smithsonian', artist_result['biography']['value'])
        artist.add_uri('smithsonian', uris['smithsonian'])
        
    return artist

def get_artworks_by_artist(uris: dict):
    artworks = []
    
    for key in uris.keys():
        uris[key] = '<%s>' % uris[key]
    
    # This will probably not be used - we can use all artworks info when the function is done
    if 'getty' in uris.keys():
        query = """
            %s
            
            SELECT ?uri ?name ?image WHERE {
                ?production crm:P14_carried_out_by %s.
                ?uri crm:P108i_was_produced_by ?production;
                        crm:P1_is_identified_by ?identify;
                        crm:P138i_has_representation ?image.
                ?identify crm:P2_has_type gettyth:object-title-primary;
                            crm:P190_has_symbolic_content ?name.
            }
        """ % (prefixes, uris['getty'])
        
        sparql = SPARQLWrapper(endpoints['getty'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        
        for r in ret["results"]["bindings"]:
            artwork = Artwork(r['name']['value'])
            artwork.add_uri('getty', r['uri']['value'])
            artwork.add_image(r['image']['value'])
            artworks.append(artwork)
    
    return artworks

def get_similar_artists_by_movement(movement: str):
    artists = []
    
    query = """
        %s
        
        SELECT ?uri (SAMPLE(?name) AS ?name) ?image WHERE {
            ?uri dbo:movement ?movementPage.
            ?movementPage rdfs:label "%s"@en.
            
            ?uri rdf:type dbo:Person, dbo:Artist;
                 rdfs:label ?name.
            FILTER (lang(?name) = "en") 
            
            OPTIONAL {
                ?uri dbo:thumbnail ?image.
            }
        }
    """ % (prefixes, movement)
    
    print(query)
    
    sparql = SPARQLWrapper(endpoints['dbpedia'])
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    
    ret = sparql.query().convert()
    
    for r in ret["results"]["bindings"]:
        artist = Artist(r['name']['value'])
        artist.add_uri('dbpedia', r['uri']['value'])
        
        if 'image' in r:
            artist.add_image(r['image']['value'])
        
        artists.append(artist)
        
    return artists
    
    