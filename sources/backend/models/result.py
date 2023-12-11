class Result:
    def __init__(self, type, name) -> None:
        self.name = name
        self.type = type
        self.uris = {}
        self.image = None

    def add_uri(self, source, uri):
        self.uris[source] = uri

    def add_image(self, image):
        self.image = image

    def has_image(self):
        return self.image is not None
