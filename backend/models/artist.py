from models.result import Result


class Artist(Result):
    def __init__(self, name) -> None:
        super().__init__('artist', name)
        self.birth_date = None
        self.birth_place = None
        self.death_date = None
        self.death_place = None
        self.bibliography = None
        self.getty_link = None
        self.artworks = []