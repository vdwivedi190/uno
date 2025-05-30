# A terminal-based implementation of the card game UNO

This repository contains a Python implementation of the card game [UNO](https://en.wikipedia.org/wiki/Uno_(card_game)) with a command line interface. The game can be invoked from the terminal as 

```
vatsal@qrcode>python -m uno
``` 
The module can alternatively be imported and used to test algorithms by defining a class inheriting from `Player` which must provide a function `move(...)` that takes in information about the current board state and returns a list of card(s) to play, or an empty list if no valid move remain, in which case the player must draw a card from the main deck. Explicitly, one needs to define 
```
from uno import Card, Player, PlayerList, Game

class AIPlayer(Player):
    """A class representing an AI Player for UNO."""

    def move(self, top_card:Card, active_color:str, other_hands:list[int] = []) -> list[Card]:
        """"Make a move by playing a card from the hand.
        
        Args:
            top_card (Card): The top card of the active deck.
            active_color (str): The current color. This is relevant only when the top_card is a wild card,
                                where the active_color is chosen by the player who played the wild card. 
            other_hands (list[int]): A list of number of cards in other player's hands, in the order of their
                                     turn starting from the player after AIPlayer in the current turn order.
        Returns:
            list[Card]: A list of cards to play, or an empty list if no card can be played.
        """
        # function body
```
The player can be added to a `PlayerList` object, which is then passed as an argument to the constructor of `Game`. An example, `RandomAIPlayer`, is defined in `player.py`, which plays one of the allowed cards at random. 
