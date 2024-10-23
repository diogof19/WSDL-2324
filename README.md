# Art Attack, Art, Artist, and Exhibitions Search Engine

A search engine for art built on linked-open data. Art Attack pools data from various public sources, namely the Smithsonian American Art Museum, DBPedia, and Wikidata.

## Features

Besides search Art Attack features:

### Artist Biographies

Art Attacks artist pages feature a vast amount of information about their subject, as well as the artworks they've created.

![artistpage](https://github.com/user-attachments/assets/b1e302a1-4f12-4b21-be1e-57078b1f1081)

### Artowrk Exhibithion Histories

Art Attack features the exhibition history of artworks, as well as related artworks, i.e. artworks that have been at the same exhibition, are from the same artist, or from the same artistic movement.

![artworkpage](https://github.com/user-attachments/assets/01b9cdc2-ed28-4aa9-859d-eb411e189872)


## Running

### Download and extract data for backup SAAM endpoint

- Download data [here](http://sirismm.si.edu/siris/linkeddata/n3.tar)
- Extract the ```.n3*``` files and ```n3-seeAlso``` directory from ```.tar``` to ```saam/n3``` (Don't delete the .empty that is there already)

### Running (Production)

- In the project root, run:

```shell
docker-compose up --build
```

### Running (DEV)

#### Frontend

- First time:

```shell
npm install
```

- After:

```shell
npm run dev
```

#### Backend

##### Server

- First time:

```shell
pip install -r requirements.txt
```

- After:

```shell
uvicorn main:app --reload
```

##### Backup SAAM

```shell
docker-compose up
```
