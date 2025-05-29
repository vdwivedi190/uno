import random
import functools

from .exceptions import EmptyDeckError

NUMERIC = "num"
ACTION = "action"
WILD = "wild"

# List of valid card names and colors
ACTION_CARDS = {'skip':11, 'reverse':12, 'draw2':13}
WILD_CARDS = {'draw4':21, 'wild':22}
COLORS = {'red':1, 'green':2, 'blue':3, 'yellow':4}

# Dictionary to map card names to their respective colors
CARD_NAMES = {i: str(i) for i in range(10)} | {val: key for key,val in (ACTION_CARDS | WILD_CARDS).items()}
COLOR_NAMES = {ind:color for color, ind in COLORS.items()}



class Card:
    """A class representing a UNO card."""

    def __init__(self, ctype:str, name:str, color:str=''):
        """Construct a UNO card. The relevant parameters are:
        - ctype: The type of the card (numeric, action, or wild).
        - id: A integer ID of the card. Same as the number for numeric cards. 
        - color: The color of the card, which can be 'r', 'g', 'b', or 'y' for numeric and action cards."""

        if ctype not in {NUMERIC, ACTION, WILD}:
            raise ValueError(f"Invalid card type: {ctype}. Expected one of num, action, or wild.")
        
        self._ctype = ctype
        
        if self._ctype == WILD:  # Wild cards do not have a color
            if name not in WILD_CARDS:
                raise ValueError(f"Invalid wild card name: {name}. Expected one of {WILD_CARDS.keys()}.")

            self._id = WILD_CARDS[name]
            self._color = 0 

        else:  # Numeric and action cards require a name and color
            if color not in COLORS:
                raise ValueError(f"Invalid card color: {color}. Expected one of {COLORS.keys()}.")
        
            if ctype == ACTION:
                if name not in ACTION_CARDS:
                    raise ValueError(f"Invalid action card name: {name}. Expected one of {ACTION_CARDS.keys()}.")
                else:
                    self._id = ACTION_CARDS[name]
                    self._color = COLORS[color]
            elif ctype == NUMERIC:
                if len(name) != 1 or not name.isdecimal():
                    raise ValueError(f"Invalid card name: {name}. Expected a number between 01 and 9.")
                else:
                    self._id = int(name)
                    self._color = COLORS[color]
                
                
    def __str__(self):
        """Return a string representation of the card."""
        desc = f"{CARD_NAMES[self._id]}"
        if not self.is_wild():
            desc += f"({COLOR_NAMES[self._color]})"
        return desc

    def code(self):
        """Return a ID to sort the cards."""
        return 100*self._color + self._id

    def is_numeric(self) -> bool:
        """Check if a given card is a numeric card."""
        return self._ctype == NUMERIC
    
    def is_action(self) -> bool:
        """Check if a given card is a action card."""
        return self._ctype == ACTION
    
    def is_wild(self) -> bool:
        """Check if a given card is a wild card."""
        return self._ctype == WILD
    
    def is_stackable(self) -> bool:
        """Check if a given card is a wild card."""
        return self._id in {WILD_CARDS['draw4'], ACTION_CARDS['draw2']}

    @property
    def ctype(self) -> str:
        """Return the type of the card."""
        return self._ctype
    
    @property
    def id(self) -> str:
        """Return the ID of the card."""
        return CARD_NAMES[self._id]
    
    @property
    def color(self) -> str | None:
        """Return the color of the card."""
        return COLOR_NAMES[self._color] if self._color != 0 else None

    def __eq__(self, value) -> bool:
        return self.code() == value.code()

    @functools.total_ordering
    def __lt__(self, value) -> bool:
        return self.code() < value.code()
    

    def is_valid_play(self, played_cards, active_color:str|None) -> bool:
        """Check if the cards passed as played_cards can be played on top of the current active deck.
        Args:
            played_cards (list[Card]): A list of cards that the player wants to play.
        Returns:
            bool: True if the played cards.
        """
        if len(played_cards) == 0:
            return True         
        elif len(played_cards) > 1:
            raise NotImplementedError("Multi-card plays are not yet implemented.")        
        else:
            card = played_cards[0]
        
        if card.is_wild():
            # Wild cards can be played at any time
            return True
        elif self.is_wild():
            # If the top card is a wild card, the played card must match the active color
            if active_color is None:
                raise ValueError("Cannot play a card on top of a wildcard when the active color is not set.")
            if card.color == active_color:
                return True
        elif (card.color == self.color or card.id == self.id):
            return True
        else: 
            return False 

        # Check if all cards are of the same type 
        # if len(set(cards)) > 1: 
        #     raise ValueError("Cannot play multiple different cards at once.")
        


class Deck:
    """A class representing a deck of UNO cards."""

    def __init__(self, empty:bool = False):
        """Initialize the deck. 
        If empty is set to True, the deck will be empty initially; otherwise creates a full deck of cards."""

        self._cards = []

        if not empty:
            self.create_full_deck()
            self.shuffle()


    def create_full_deck(self):
        """Create a full deck of 108 UNO cards."""
        # Two copies of cards 1-9 in each color (9 x 4 x 2 = 72 cards)
        self._cards.extend([Card(NUMERIC, str(i), color) 
                      for i in range(1,10) 
                      for color in list(COLORS) 
                      for _ in range(2)])
        
        # Add 0 cards in each color (4 cards)
        self._cards.extend([Card("num", '0', color) for color in list(COLORS)])

        # Two copies of action cards in each color (3 x 4 x 2 = 24 cards)
        self._cards.extend([Card(ACTION, name, color) 
                      for name in list(ACTION_CARDS)
                      for color in list(COLORS) 
                      for _ in range(2)])

        # Two copies of wild cards (2 x 4 = 8 cards)
        self._cards.extend([Card(WILD, name) 
                      for name in list(WILD_CARDS)
                      for _ in range(4)])
                      

                
    def __str__(self):
        """Return a string representation of the deck."""
        return f"Deck with {len(self._cards)} cards: \n " + "\n ".join(str(card) for card in self._cards)

    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self._cards)


    def add_cards(self, cards:Card|list[Card]) -> None:
        if isinstance(cards, list):
            for card in cards:
                self.add_cards(card)
        elif isinstance(cards, Card):
            self._cards.append(cards)
        else:
            raise TypeError(f"Expected a Card or a list of Cards instead of {type(cards)}.")

    def remove_cards(self, card: Card, num:int = 0) -> list[Card]:
        """Removes up to 'num' copies of the card from the deck. num=0 means remove all copies."""
        if num < 0:
            raise ValueError("Must remove at least 1 card!")
        
        removed_cards:list[Card] = []
        if num == 0:
            num = len(self._cards)
        for _ in range(num):
            if card not in self._cards:
                break
            self._cards.remove(card)
            removed_cards.append(card)                
        return removed_cards
    
    def remove_all(self) -> list[Card]:
        """Removes all cards from the deck and returns them."""
        print(f"Removing all cards from the deck with {len(self._cards)} cards.")
        removed_cards = self._cards.copy()
        print(f"{len(self._cards)=}, {len(removed_cards)=}.")
        self._cards.clear()
        print(f"{len(self._cards)=}, {len(removed_cards)=}.")
        return removed_cards

    def draw_card(self) -> Card:
        """Draws a card from the top of the deck and returns it."""
        if self.is_empty():
            raise EmptyDeckError()
        else:
            return self._cards.pop(-1)

    def view_top_card(self) -> Card:
        """Draws a card from the top of the deck and returns it."""
        if self.is_empty():
            raise EmptyDeckError()
        else:
            return self._cards[-1]
        
    
    def is_empty(self) -> bool:
        """Check if the deck is empty."""
        return len(self._cards) == 0
    
    def sort(self) -> None:
        """Sort the deck by card type and color."""
        self._cards.sort()
    
    @property
    def cards(self) -> list[Card]:
        """Return a list of all cards in the deck."""
        return self._cards.copy()
    
    @property
    def size(self) -> int:
        """Return the number of cards in the hand."""
        return len(self._cards) 
    



class Hand(Deck):
    """A class representing a player's hand in the UNO game."""

    def __init__(self, deck: Deck | None = None, num: int = 0):
        if deck is None:
            self._cards = []
        else:
            self._cards = [deck.draw_card() for _ in range(num)]

    
    def play_cards(self, card:Card, num:int=1) -> list[Card]:
        """Play one or more cards from the hand."""
        if num < 1:
            raise ValueError("Must play at least 1 card.")
        
        try:
            played_cards = self.remove_cards(card, num)
        except ValueError:
            raise ValueError(f"Card {card} not found in hand.")
        
        return played_cards
    

    # @property
    # def cards(self) -> list[Card]:
    #     """Return a list of all cards in the deck."""
    #     raise Exception("Cannot access cards directly from Hand. Use the 'play_cards' method instead.")
    