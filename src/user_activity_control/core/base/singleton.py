class Singleton:
    """A Singleton class that ensures only one instance of the class is created."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
