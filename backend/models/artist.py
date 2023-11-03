class Artist:
    def __init__(self, name) -> None:
        self.name = name
        self.uris = {}
        self.thumbnail = None
        
    def add_uri(self, endpoint, uri):
        self.uris[endpoint] = uri
        
    def add_thumbnail(self, thumbnail):
        self.thumbnail = thumbnail