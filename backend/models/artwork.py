from models.result import Result

class Artwork(Result):
    def __init__(self, name) -> None:
        super().__init__('artwork', name)
        pass