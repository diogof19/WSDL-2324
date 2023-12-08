from models.result import Result

class Artwork(Result):
    def __init__(self, name) -> None:
        super().__init__('artwork', name)
        self.year = None
        self.description = {}
        self.authorUri = {}
        self.authorName = None
        self.wikipedia_link = None
        self.museumName = []
        self.provenance = {}
        pass
    
    