from .cards import Card, Deck, Hand, COLORS
from .io import IO

import random

# type cardcolor = str


class Player:
    """A class representing a player in the UNO game."""

    def __init__(self, name: str):
        self.name = name
        self._hand = Hand()

    def add_cards(self, cards:Card|list[Card]):
        """Add one or more cards to the hand."""
        self._hand.add_cards(cards)
        self._hand.sort()

    def is_done(self) -> bool:
        """Check if the player has finished (i.e., has no cards left in hand)."""
        return self._hand.is_empty()

    def choose_color(self) -> str:
        """Choose a color for a wild card."""
        return random.choice(list(COLORS))
    
    def move(self, top_card:Card, active_color:str, other_hands:list[int] = []) -> list[Card]:
        raise NotImplementedError("This method should be implemented by subclasses.")



class HumanPlayer(Player):
    """A class representing an AI player in the UNO game."""

    def __init__(self, name: str, IO:IO):
        super().__init__(name)
        self.IO = IO 
    
    def move(self, top_card:Card, active_color:str, other_hands:list[int] = []) -> list[Card]:
        """Make a move by playing a card from the hand.
        
        Args:
            top_card (Card): The top card of the active deck.
            other_hands (list[int]): A list of other players' hands (not used in this implementation).
        Returns:
            list[Card]: A list of cards to play, or an empty list if no card can be played.
        """
        if self._hand.is_empty():
            raise ValueError("Cannot play, hand is empty.")
        
        self._hand.sort()
        
        self.IO.write(f"{self.name}'s current hand:".upper())
        self.IO.show_hand(self._hand.cards)
        card_index = self.IO.read_card(self._hand.cards)

        if card_index == -1:
            return [] 
        elif card_index < 0 or card_index >= len(self._hand.cards):
            raise ValueError(f"Invalid card index {card_index} for the hand of {self.name}.")
        else:
            card = self._hand.cards[card_index]
            self._hand.remove_cards(card)
            return [card] 
        

class RandomAIPlayer(Player):
    """A class representing an AI player in the UNO game."""

    def move(self, top_card:Card, active_color:str, other_hands:list[int] = []) -> list[Card]:
        if self._hand.is_empty():
            raise ValueError("Cannot play, hand is empty.")
        
        
        playable_cards = self.get_playable_cards(top_card, active_color)
        if len(playable_cards) == 0:
            return []
        else:
            card = random.choice(playable_cards)  # Play the first playable card
            self._hand.remove_cards(card)
            return [card]

        # # Play the first card that matches the color or id of the top card in the active deck            
        # if top_card.is_numeric() or top_card.is_action():
        #     for card in self._hand.cards:
        #         if card.color == top_card._color or card.id == top_card._id:
        #             self._hand.remove_cards(card)
        #             return [card] 
                
        # # If no matching color or id found, play a wild card if available
        # for card in self._hand.cards:
        #     if card.is_wild() :
        #         self._hand.remove_cards(card)
        #         return [card] 
            
        # # If no playable card found, return an empty list
        # return []


    def get_playable_cards(self, top_card:Card, active_color:str) -> list[Card]:
        """Get a list of playable cards based on the top card."""
        playable_cards = []
        for card in self._hand.cards:
            if top_card.is_valid_play([card], active_color):
                playable_cards.append(card)
        return playable_cards

