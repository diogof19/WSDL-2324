from SPARQLWrapper import SPARQLWrapper, JSON, XML, CSV
from models.artist import Artist
from models.artwork import Artwork
from globals import BACKUP_DATABASE_HOST
import copy

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
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX amart: <http://collection.americanart.si.edu/id/ontologies/>
"""

def search_and_save(query : str, endpoint_name : str, results : list[Artist | Artwork], result_type : type) -> None:
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

            if len(ret_2['results']['bindings']) > 0:
                match_id = ret_2['results']['bindings'][0]['exact_match']['value'].split('/')[-1]

        found = False

        for result in results:
            if endpoint_name == 'getty' and 'wikidata' in result.uris and match_id == result.uris['wikidata'].split('/')[-1]:
                found = True

                result.add_uri(endpoint_name, r['uri']['value'])
                result.add_uri('getty_vocab', r['exact_match']['value'])

                if 'image' in r and (not result.has_image() or 'Redirect/file' in result.image):
                    result.add_image(r['image']['value'])
            elif endpoint_name == 'smithsonian' and 'dbpedia' in result.uris and 'dbpedia' in r and r['dbpedia']['value'] == result.uris['dbpedia']:
                found = True

                result.add_uri(endpoint_name, r['uri']['value'])

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
        
        results.append(artist)
        

def artist_search(search_term : str, exact_match : bool = False) -> list[Artist]:
    results = []

    search_term = '.*'.join(search_term.split(' '))
    
    #DBPedia
    filter_expression = 'regex(?name, ".*%s.*", "i")' % search_term + (' || regex(?redirect, ".*%s.*", "i")' % search_term if not exact_match else '')

    query = (
        '%s\n\n' % prefixes +
        f'SELECT DISTINCT ?uri (SAMPLE(?name) AS ?name) ?image ?wikidata WHERE {{\n'
        f'?uri rdf:type dbo:Person, dbo:Artist; rdfs:label ?name.\n'
        f'OPTIONAL {{\n'
        f'?uri owl:sameAs ?wikidata.\n'
        f'FILTER regex(?wikidata, "^http:\\\\/\\\\/www\\\\.wikidata\\\\.org\\\\/.*", "i")\n'
        f'}}\n'
        f'OPTIONAL {{\n'
        f'?uri dbo:thumbnail ?image.\n'
        f'}}\n'
        f'{"" if exact_match else "?redirect dbo:wikiPageRedirects ?uri"}\n'
        f'FILTER ({filter_expression})\n'
        f'FILTER (lang(?name) = "en")\n'
        f'}}'
    )
    
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
    
    # TODO: I can't find the dbpedia relationship, so I we're not checking if it exist in dbpedia results to join
    query = """
        %s
        
        SELECT DISTINCT ?uri (SAMPLE(?name) as ?name)  WHERE {
            ?uri rdf:type cidoc:E21_Person;
                    cidoc:P1_is_identified_by ?dName.
            FILTER regex(?uri, "^http.*")
            
            ?dName rdfs:label ?name.
            FILTER regex(?name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    search_and_save(query, 'smithsonian', results, Artist)

    return results

def artwork_search(search_term : str) -> list[Artwork]:
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
            
            FILTER (regex(?name, ".*%s.*", "i"))
            FILTER (lang(?name) = "en")
        }
    """ % (prefixes, search_term)

    search_and_save(query, 'dbpedia', results, Artwork)

    #Getty Museum
    query = """
        %s

        SELECT DISTINCT ?uri ?name ?image ?exact_match WHERE {
            ?uri rdf:type crm:E22_Human-Made_Object.
            
            {
    			SELECT (SAMPLE(?name) as ?name) {
      				?uri rdfs:label ?name.
      				FILTER regex(?name, ".*%s.*", "i")
    			}
  			}
            
            OPTIONAL {
                ?uri skos:exactMatch ?exact_match.
                FILTER regex(str(?exact_match), "^http:\\\\/\\\\/vocab\\\\.getty\\\\.edu\\\\/.*", "i")
            }
            OPTIONAL {                
                ?uri getty:thumbnailUrl ?image.
            }
        }
    """ %  (prefixes, search_term)

    search_and_save(query, 'getty', results, Artwork)

    #Smithsonian Museum
    query = """
        %s
        
        SELECT DISTINCT ?uri (SAMPLE(?name) AS ?name) (SAMPLE(?image) AS ?image) ?dbpedia WHERE {
            ?uri rdf:type cidoc:E22_Man-Made_Object; cidoc:P102_has_title ?title.
            ?title rdfs:label ?name.
            OPTIONAL {
                ?uri owl:sameAs ?dbpedia.
                FILTER regex(?dbpedia, "^http:\\\\/\\\\/dbpedia\\\\.org\\\\/.*", "i")
            }
            OPTIONAL {
                ?uri cidoc:P138i_has_representation ?image.
            }
            FILTER regex(?uri, "^http.*")
            FILTER regex(?name, ".*%s.*", "i")
        }
    """ % (prefixes, search_term)
    
    search_and_save(query, 'smithsonian', results, Artwork)

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

def retrieve_artist_info(uris: dict):
    original_uris = copy.deepcopy(uris)
    for key in uris.keys():
        uris[key] = '<%s>' % uris[key]
    
    if 'wikidata' in uris.keys():
        query = """
            %s
            
            SELECT ?name ?birthDate ?birthPlace ?deathDate ?deathPlace ?deathManner ?movement WHERE {
                { 
                    SELECT (SAMPLE(?name) as ?name) WHERE {
                        %s rdfs:label ?name.
                        FILTER langMatches(lang(?name),'en').
                    }
                } 
                
                OPTIONAL {
                    %s wdt:P569 ?birthDate.
                }
                
                OPTIONAL {
                    { 
                        SELECT (SAMPLE(?birthPlace) as ?birthPlace) WHERE {
                            %s wdt:P19 ?bPlace.
                            ?bPlace rdfs:label ?birthPlace.
                            FILTER langMatches(lang(?birthPlace),'en').
                        }
                    } 
                }
                
                OPTIONAL {
                    %s wdt:P570 ?deathDate.
                }
                
                OPTIONAL {
                    { 
                        SELECT (SAMPLE(?deathPlace) as ?deathPlace) WHERE {
                            %s wdt:P20 ?dPlace.
                            ?dPlace rdfs:label ?deathPlace.
                            FILTER langMatches(lang(?deathPlace),'en').
                        }
                    } 
                }
                
                OPTIONAL {
                    %s wdt:P1196 ?dManner.
                    ?dManner rdfs:label ?deathManner.
                    FILTER langMatches(lang(?deathManner),'en').
                }
                    
                OPTIONAL {
                    { 
                        SELECT (GROUP_CONCAT(?mov;separator=",") AS ?movement) WHERE {
                            %s wdt:P135 ?movementPage.
                            ?movementPage rdfs:label ?mov.
                            FILTER langMatches(lang(?mov),'en').
                        }
                    } 
                }
            }
        """ % (prefixes, uris['wikidata'], uris['wikidata'], uris['wikidata'], uris['wikidata'], uris['wikidata'], uris['wikidata'], uris['wikidata'])
        
        sparql = SPARQLWrapper(endpoints['wikidata'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artist_result = ret["results"]["bindings"][0]
        
        artist = Artist(artist_result['name']['value'])    
        artist.add_uri('wikidata', original_uris['wikidata'])
        
        if 'birthDate' in artist_result:
            artist.add_birth_date(artist_result['birthDate']['value'].split('T')[0])
        
        if 'birthPlace' in artist_result:
            artist.add_birth_place(artist_result['birthPlace']['value'])
        
        if 'deathDate' in artist_result:
            artist.add_death_date(artist_result['deathDate']['value'].split('T')[0])
        
        if 'deathPlace' in artist_result:
            artist.add_death_place(artist_result['deathPlace']['value'])
        
        if 'deathManner' in artist_result:
            artist.add_death_manner(artist_result['deathManner']['value'])
        
        if 'movement' in artist_result:
            movements = artist_result['movement']['value'].split(',')
            for movement in movements:
                artist.add_movement(movement)
    
    if 'dbpedia' in uris.keys():
        query = """
        %s
        
        SELECT (SAMPLE(?name) AS ?name) ?image ?birthDate (SAMPLE(?birthPlace) AS ?birthPlace) ?deathDate ?deathPlace ?biography ?wikipediaLink ?movement WHERE {
            %s rdfs:label ?name.
            
            OPTIONAL {
                %s dbo:birthDate ?birthDate.
            }
            
            OPTIONAL {
                %s dbo:birthPlace ?bPlace.
                ?bPlace dbp:name ?birthPlace.
            }
            
            OPTIONAL {
                %s dbo:thumbnail ?image.
            }
            
            OPTIONAL {
                %s dbo:deathDate ?deathDate;
                    dbo:deathPlace ?dPlace.
                ?dPlace dbp:name ?deathPlace.
            }
            
            OPTIONAL {
                { 
                    SELECT (GROUP_CONCAT(?mov;separator=",") AS ?movement) WHERE {
                        %s dbo:movement ?movementPage.
                    ?movementPage rdfs:label ?mov.
                    FILTER langMatches(lang(?mov),'en').
                    }
                } 
            }

            OPTIONAL {
                %s dbo:abstract ?biography.
                FILTER langMatches(lang(?biography),'en').
            }

            OPTIONAL {
                %s foaf:isPrimaryTopicOf ?wikipediaLink.
            }
        }
        """ % (prefixes, uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'])
        
        sparql = SPARQLWrapper(endpoints['dbpedia'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artist_result = ret["results"]["bindings"][0]
        
        if 'artist' not in locals():
            artist = Artist(artist_result['name']['value'])
            
            if 'birthDate' in artist_result:
                artist.add_birth_date(artist_result['birthDate']['value'])
            
            if 'birthPlace' in artist_result:
                artist.add_birth_place(artist_result['birthPlace']['value'])
            
            if 'deathDate' in artist_result:
                artist.add_death_date(artist_result['deathDate']['value'])
            
            if 'deathPlace' in artist_result:
                artist.add_death_place(artist_result['deathPlace']['value'])
        
        artist.add_uri('dbpedia', original_uris['dbpedia'])
        
        if 'biography' in artist_result:
            artist.add_biography('dbpedia', artist_result['biography']['value'])
        
        if 'movement' in artist_result:
            movements = artist_result['movement']['value'].split(',')
            for movement in movements:
                artist.add_movement(movement)
        
        if 'wikipediaLink' in artist_result:
            artist.add_wikipedia_link(artist_result['wikipediaLink']['value'])
        
        if 'image' in artist_result:
            artist.add_image(artist_result['image']['value'])
    
    if 'getty' in uris.keys():
        query = """
        %s
        
        SELECT ?name ?lifeDates ?birthYear ?birthPlace ?deathYear ?deathPlace ?biography ?gettyLink WHERE {
            %s crm:P1_is_identified_by ?identify.
            ?identify a crm:E33_E41_Linguistic_Appellation;
                    crm:P190_has_symbolic_content ?name.

            OPTIONAL {
                %s crm:P67i_is_referred_to_by ?bDateReferred.
                ?bDateReferred crm:P2_has_type gettyth:life-dates-description;
  				               cidoc:P190_has_symbolic_content ?lifeDates
            }
            
            OPTIONAL {
                %s crm:P98i_was_born ?born.
                ?born crm:P4_has_time-span ?birth_timespan.
                ?birth_timespan crm:P82a_begin_of_the_begin ?birthYear.
            }

            OPTIONAL {
                %s crm:P67i_is_referred_to_by ?birth_referred.
                ?birth_referred crm:P2_has_type gettyth:birth-place-description;
                                crm:P190_has_symbolic_content ?birthPlace.
            }

            OPTIONAL {
                %s crm:P100i_died_in ?death.
                ?death crm:P4_has_time-span ?death_timespan.
                ?death_timespan crm:P67i_is_referred_to_by ?death_referred.
                ?death_referred crm:P190_has_symbolic_content ?deathYear.
            }
            
            OPTIONAL {
                %s crm:P67i_is_referred_to_by ?death_place_referred.
                ?death_place_referred crm:P2_has_type gettyth:death-place-description;
                                      crm:P190_has_symbolic_content ?deathPlace;
            }

            OPTIONAL {
                %s crm:P67i_is_referred_to_by ?bib_referred.
                ?bib_referred rdfs:label "Artist/Maker Biography";
                            purl:format "text/html"; #the other option is text/markdown
                            crm:P190_has_symbolic_content ?biography.
            }

            OPTIONAL {
                %s crm:P129i_is_subject_of ?gettyLink.
                ?gettyLink crm:P2_has_type aat:300264578.
            }
        }
        """ % (prefixes, uris['getty'], uris['getty'], uris['getty'], uris['getty'], uris['getty'], uris['getty'], uris['getty'], uris['getty'])
        
        sparql = SPARQLWrapper(endpoints['getty'])
        sparql.setMethod('POST')
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artist_result = ret["results"]["bindings"][0]
        
        if 'artist' not in locals():
            artist = Artist(artist_result['name']['value'])
            
            if 'lifeDates' in artist_result:
                lifeDates = artist_result['lifeDates']['value']
                if '–' in lifeDates:
                    artist.add_birth_date(lifeDates.split('–')[0].strip())
                    artist.add_death_date(lifeDates.split('–')[1].strip())
                else:
                    artist.add_birth_date(lifeDates.split('born ')[1].strip())
            
            if 'birthYear' in artist_result:
                artist.add_birth_date(artist_result['birthYear']['value'])
            
            if 'birthPlace' in artist_result:
                artist.add_birth_place(artist_result['birthPlace']['value'])
            
            if 'deathYear' in artist_result:
                artist.add_death_date(artist_result['deathYear']['value'])
            
            if 'deathPlace' in artist_result:
                artist.add_death_place(artist_result['deathPlace']['value'])
        
        artist.add_uri('getty', original_uris['getty'])
        
        if 'biography' in artist_result:
            artist.add_biography('getty', artist_result['biography']['value'])
        
        if 'gettyLink' in artist_result:
            artist.add_getty_link(artist_result['gettyLink']['value'])
        
    if 'smithsonian' in uris.keys():
        query = """
        %s

        SELECT (SAMPLE(?name) as ?name) ?birthDate ?deathDate ?pBiography ?biography WHERE {
            %s cidoc:P1_is_identified_by ?dName.
             ?dName rdfs:label ?name.           

            OPTIONAL {
                %s cidoc:P98i_was_born ?birth.

                OPTIONAL {
                    ?birth cidoc:P4_has_time-span ?birthSpan.
                    ?birthSpan cidoc:P82_at_some_time_within ?birthDate
                }
            }

            OPTIONAL {
                %s cidoc:P100i_died_in ?death.

                OPTIONAL {
                    ?death cidoc:P4_has_time-span ?deathSpan.
                    ?deathSpan cidoc:P82_at_some_time_within ?deathDate.
                }
            }
  
            OPTIONAL {
                {
                    SELECT  (GROUP_CONCAT(?pBio;separator=\"\\n\") AS ?pBiography) {
                            %s amart:PE_has_note_primaryartistbio ?pBio.
                    }
                }
            }
            
            OPTIONAL {
                {
                    SELECT  (GROUP_CONCAT(?bio;separator=\"\\n\") AS ?biography) {
                            %s amart:PE_has_note_artistbio ?bio.
                    }
                }
            }
        }

        """ % (prefixes, uris['smithsonian'], uris['smithsonian'], uris['smithsonian'], uris['smithsonian'], uris['smithsonian'])
        print(query)
        
        sparql = SPARQLWrapper(endpoints['smithsonian'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artist_result = ret["results"]["bindings"][0]
        
        if 'artist' not in locals():
            artist = Artist(artist_result['name']['value'])
            
            if 'birthDate' in artist_result:
                artist.add_birth_date(artist_result['birthDate']['value'])
            
            if 'deathDate' in artist_result:
                artist.add_death_date(artist_result['deathDate']['value'])
        
        artist.add_uri('smithsonian', original_uris['smithsonian'])
        
        if 'biography' in artist_result and 'pBiography' in artist_result:
            artist.add_biography('smithsonian', artist_result['pBiography']['value'] + '\n' + artist_result['biography']['value'])
        elif 'biography' in artist_result:    
            artist.add_biography('smithsonian', artist_result['biography']['value'])
        elif 'pBiography' in artist_result:
            artist.add_biography('smithsonian', artist_result['pBiography']['value'])
        
    return artist

def retrieve_artwork_info(uris: dict):
    print(type(uris))
    if 'dbpedia' in uris.keys():
        query = """
            %s
            
            SELECT (SAMPLE(?name) AS ?name) ?image ?year ?description ?authorName ?authorUri ?wikipediaLink ?museumName WHERE {
                <%s> rdfs:label ?name.
                FILTER langMatches(lang(?name),'en').

                OPTIONAL {
                    <%s> dbp:year ?year.
                }
                
                OPTIONAL {
                    <%s> dbo:thumbnail ?image.
                }

                OPTIONAL {
                    <%s> dbo:abstract ?description.
                    FILTER langMatches(lang(?description),'en').
                }

                OPTIONAL {
                    <%s> foaf:isPrimaryTopicOf ?wikipediaLink.
                }

               OPTIONAL {
                    <%s> dbo:author ?authorUri.
                    ?authorUri rdfs:label ?authorName.  
                    FILTER langMatches(lang(?authorName),'en').
               }

               OPTIONAL {
                    {
                        SELECT (GROUP_CONCAT(?mName;separator=",") AS ?museumName) {
                            <%s> dbo:museum ?museumUri.
                            ?museumUri dbp:name ?mName.
                            FILTER langMatches(lang(?mName),'en').
                        }
                    
                    }
                }
            }
        """ % (prefixes, uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'], uris['dbpedia'])
        
        sparql = SPARQLWrapper(endpoints['dbpedia'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        artwork_result = ret["results"]["bindings"][0]
        
        artwork = Artwork(artwork_result['name']['value'])
        artwork.add_uri('dbpedia', uris['dbpedia'])
        
        if 'year' in artwork_result:
            artwork.year = artwork_result['year']['value']
            
        if 'description' in artwork_result:
            artwork.description["dbpedia"] = artwork_result['description']['value']
            
        if 'authorName' in artwork_result:
            artwork.authorName = artwork_result['authorName']['value']
            
        if 'authorUri' in artwork_result:
            artwork.authorUri["dbpedia"] = artwork_result['authorUri']['value']
        
        if 'wikipediaLink' in artwork_result:
            artwork.wikipedia_link = artwork_result['wikipediaLink']['value']
        
        if 'image' in artwork_result:
            artwork.image = artwork_result['image']['value']
        
        museumsList = artwork_result['museumName']['value'].split(',')
        if len(museumsList) != 1 and museumsList[0] != '' :
            artwork.museumName = museumsList
            
            
    
    return artwork
    
def get_artworks_by_artist(uris: dict):
    artworks = []
    
    for key in uris.keys():
        uris[key] = '<%s>' % uris[key]
    
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
    
    if 'smithsonian' in uris.keys():
        query = """
            %s
            
            SELECT ?uri ?name WHERE {
                ?production cidoc:P14_carried_out_by %s;
                            cidoc:P108_has_produced ?uri.
                
                ?uri cidoc:P102_has_title ?title.
                ?title rdfs:label ?name.
            }
        """ % (prefixes, uris['smithsonian'])
        
        sparql = SPARQLWrapper(endpoints['smithsonian'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        
        for r in ret["results"]["bindings"]:
            artwork = Artwork(r['name']['value'])
            artwork.add_uri('smithsonian', r['uri']['value'])
            artworks.append(artwork)
    
    if 'dbpedia' in uris.keys():
        query = """
            %s
            
            SELECT ?uri ?name ?image WHERE {
                ?uri dbo:author %s;
                     rdfs:label ?name.
            FILTER (lang(?name) = "en").
   
            OPTIONAL {
                ?uri dbo:thumbnail ?image.
            }
        }
        """ % (prefixes, uris['dbpedia'])
        
        sparql = SPARQLWrapper(endpoints['dbpedia'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
        
        bef_artworks = copy.deepcopy(artworks)
        for r in ret["results"]["bindings"]:
            found = False
            for artwork in bef_artworks:
                if artwork.name == r['name']['value'] or artwork.name == r['name']['value'].split('(')[0].strip():
                    artwork.add_uri('dbpedia', r['uri']['value'])
                    
                    if 'image' in r and artwork.image == None:
                        artwork.add_image(r['image']['value'])
                    
                    found = True
                    break
            
            if found:
                continue
                
            artwork = Artwork(r['name']['value'])
            artwork.add_uri('dbpedia', r['uri']['value'])
            
            if 'image' in r:
                artwork.add_image(r['image']['value'])
            
            artworks.append(artwork)
    
    return artworks

def get_similar_artists_by_movements(artist_uris, movements):
    artists = set()
    
    for movement in movements:
        sim_artists = get_similar_artists_by_movement(artist_uris, movement)
        
        artists.update(sim_artists)
                        
    return artists

def get_similar_artists_by_movement(artist_uris, movement):
    artists = []
    
    if 'dbpedia' in artist_uris.keys():
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
        
        sparql = SPARQLWrapper(endpoints['dbpedia'])
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        
        ret = sparql.query().convert()
                    
        for r in ret["results"]["bindings"]:
            if(r['uri']['value'] == artist_uris['dbpedia']):
                continue
            
            artist = Artist(r['name']['value'])
            artist.add_uri('dbpedia', r['uri']['value'])
            
            if 'image' in r:
                artist.add_image(r['image']['value'])
            
            artists.append(artist)
        
    return artists
    
def get_artworks_with_same_subject(artwork : Artwork) -> list[Artwork]:
    artworks = []

    if 'dbpedia' in artwork.uris:
        query = """
            %s

            SELECT DISTINCT ?uri ?name ?image ?wikidata WHERE {
                <%s> dcterms:subject ?subject.
                ?uri dcterms:subject ?subject; rdf:type dbo:Artwork;
                    rdfs:label ?name.
                OPTIONAL {
                    ?uri dbo:thumbnail ?image.
                }
                OPTIONAL {
                    ?uri owl:sameAs ?wikidata.
                    FILTER regex(?wikidata, "^http:\\\\/\\\\/www\\\\.wikidata\\\\.org\\\\/.*", "i")
                }
                FILTER (lang(?name) = "en")
            }
        """ % (prefixes, artwork.uris['dbpedia'])

        search_and_save(query, 'dbpedia', artworks, Artwork)

    for artwork in artworks:
        print(artwork.name)

    return artworks

def get_exhibited_with_getty(artwork : Artwork) -> list[Artwork]:
    artworks = []

    if 'getty' in artwork.uris:
        print(artwork.uris['getty'])
        query = """
            %s

            SELECT DISTINCT ?uri ?name ?image ?exact_match WHERE {
                <%s> la:member_of ?exhibition.
                ?uri la:member_of ?exhibition; rdf:type crm:E22_Human-Made_Object;
                    rdfs:label ?name.
                OPTIONAL {
                    ?uri skos:exactMatch ?exact_match.
                    FILTER regex(str(?exact_match), "^http:\\\\/\\\\/vocab\\\\.getty\\\\.edu\\\\/.*", "i")
                }
                OPTIONAL {
                    ?uri getty:thumbnailUrl ?image.
                }
            }
        """ % (prefixes, artwork.uris['getty'])

        search_and_save(query, 'getty', artworks, Artwork)

    for artwork in artworks:
        print(artwork.name)
        print(artwork.uris)
        print()

    results = []

    for artwork in artworks:
        results.append(get_dbpedia_info_for_getty(artwork))

    for result in results:
        print(result.name)
        print(result.uris)
        print()

    return results

def get_dbpedia_info_for_getty(artwork : Artwork) -> Artwork:
    results = [artwork]

    if 'getty' in artwork.uris:
        match_id = None

        if 'exact_match' in artwork.uris:
            query = """
                %s

                SELECT DISTINCT ?exact_match WHERE {
                    <%s> skos:exactMatch ?exact_match.
                    FILTER regex(str(?exact_match),"^https:\\\\/\\\\/wikidata\\\\.org\\\\/.*", "i")
                }
            """ % (prefixes, artwork.uris['exact_match'])

            sparql = SPARQLWrapper(endpoints['getty_vocab'])
            sparql.setReturnFormat(JSON)
            sparql.setQuery(query)

            ret = sparql.query().convert()

            if len(ret['results']['bindings']) > 0:
                match_id = ret['results']['bindings'][0]['exact_match']['value'].split('/')[-1]

        query = """
            %s

            SELECT DISTINCT ?uri ?name ?image WHERE {
                ?uri owl:sameAs ?wikidata.
                FILTER regex(?wikidata, "^http:\\\\/\\\\/www\\\\.wikidata\\\\.org\\\\/.*/%s", "i")
                ?uri rdf:type dbo:Artwork;
                    rdfs:label ?name.
                OPTIONAL {
                    ?uri dbo:thumbnail ?image.
                }
                FILTER (lang(?name) = "en")
            }
        """ % (prefixes, match_id)

        if match_id:
            search_and_save(query, 'dbpedia', results, Artwork)

    return results[0]

if __name__ == '__main__':
    artworks = artwork_search('girl')

    #print([(artwork.name, artwork.uris) for artwork in artworks])

    # get_artworks_with_same_subject(artworks[0])
    for artwork in artworks:
        if 'getty' in artwork.uris:
            get_exhibited_with_getty(artworks[0])

    # artists = artist_search('vincent van gogh')

    # for artist in artists:
    #     print(artist.name)
    #     print(artist.uris)
    #     print()

    # artists_by_name  = {}

    # for artist in artists:
    #     if artist.name not in artists_by_name:
    #         artists_by_name[artist.name] = []

    #     artists_by_name[artist.name].append(artist)

    # for name in artists_by_name:
    #     print(f"{name}: {artists_by_name[name]}")
        