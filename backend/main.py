from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

import json
import sparql_queries

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {'message' : 'Hello, world!'}

@app.get('/artist_search')
async def search(q: Optional[str] = ''):
    results = sparql_queries.artist_search(q)

    return results

@app.get('/artwork_search')
async def search(q: Optional[str] = ''):
    results = sparql_queries.artwork_search(q)

    return results

@app.get('/artist')
async def search(q: Optional[str] = ''):
    result = sparql_queries.retrieve_artist_info(json.loads(q))

    return result

@app.get('/artwork')
async def search(q: Optional[str] = ''):
    result = sparql_queries.retrieve_artwork_info(json.loads(q))

    return result

@app.get('/artworks_by_artist')
async def search(q: Optional[str] = ''):
    result = sparql_queries.get_artworks_by_artist(json.loads(q))

    return result

@app.get('/similar_artists_movement')
async def search(uris: Optional[str] = '', movements: Optional[str] = ''):
    result = sparql_queries.get_similar_artists_by_movements(json.loads(uris), json.loads(movements))

    return result