# WSDL-2324

## Running

# Download and extract data for backup SAAM endpoint

- Download data [here](http://sirismm.si.edu/siris/linkeddata/n3.tar)
- Extract the ```.n3*``` files and ```n3-seeAlso``` directory from ```.tar``` to ```saam/n3``` (Don't delete the .empty that is there already)

# Running (Production)

- In the project root, run:

```shell
docker-compose up --build
```

## Running (DEV)

### Frontend

- First time:

```shell
npm install
```

- After:

```shell
npm run dev
```

### Backend

#### Server

- First time:

```shell
pip install -r requirements.txt
```

- After:

```shell
uvicorn main:app --reload
```

#### Backup SAAM

```shell
docker-compose up
```