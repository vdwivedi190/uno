
class EndGame(Exception):
    """Custom exception for ending the game."""
    def __init__(self, msg: str = "Cannot draw from an empty deck."):
        super().__init__(msg)
        self.message = msg


class EmptyDeckError(Exception):
    """Custom exception for when trying to draw from an empty deck."""
    def __init__(self, msg: str = "Cannot draw from an empty deck."):
        super().__init__(msg)
        self.message = msg