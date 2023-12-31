from models.result import Result


class Artist(Result):
    def __init__(self, name) -> None:
        super().__init__('artist', name)
        self.birth_date = None
        self.birth_place = None
        self.death_date = None
        self.death_place = None
        self.death_manner = None
        self.biography = {}
        self.getty_link = None
        self.movements = []
        self.wikipedia_link = None
        self.artworks = []
        
        
    def add_uri(self, endpoint, uri):
        self.uris[endpoint] = uri
        
    def add_image(self, image):
        self.image = image
        
    def has_image(self):
        return self.image is not None
    
    def add_birth_date(self, birth_date):
        self.birth_date = birth_date
        
    def add_birth_place(self, birth_place):
        self.birth_place = birth_place
        
    def add_death_date(self, death_date):
        self.death_date = death_date
        
    def add_death_place(self, death_place):
        self.death_place = death_place
    
    def add_death_manner(self, death_manner):
        self.death_manner = death_manner
        
    def add_biography(self, endpoint, biography):
        self.biography[endpoint] = biography
    
    def add_getty_link(self, getty_link):
        self.getty_link = getty_link
        
    def add_artwork(self, artwork):
        self.artworks.append(artwork)
        
    def add_movement(self, movement):
        if movement not in self.movements:
            self.movements.append(movement)
        
    def add_wikipedia_link(self, wikipedia_link):
        self.wikipedia_link = wikipedia_link
