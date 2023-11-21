from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

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


