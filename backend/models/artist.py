
class Artist:
    def __init__(self, name) -> None:
        self.name = name
        self.uris = {}
        self.type = 'artist'
        self.thumbnail = None
        self.birth_date = None
        self.birth_place = None
        self.death_date = None
        self.death_place = None
        self.bibliography = None
        self.getty_link = None
        self.artworks = []
        
    def add_uri(self, endpoint, uri):
        self.uris[endpoint] = uri
        
    def add_thumbnail(self, thumbnail):
        self.thumbnail = thumbnail
        
    def has_thumbnail(self):
        return self.thumbnail is not None