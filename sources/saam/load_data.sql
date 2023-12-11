SPARQL create GRAPH <http://www.museums.com/saam/graph>;

ld_dir('/import', '%.n3%', 'http://www.museums.com/saam/graph');
ld_dir('/import', '%.rdf', 'http://www.museums.com/saam/graph');
ld_dir('/import/n3-seeAlso', '%.n3%', 'http://www.museums.com/saam/graph');
ld_dir('/import/n3-seeAlso', '%.rdf', 'http://www.museums.com/saam/graph');

rdf_loader_run();
