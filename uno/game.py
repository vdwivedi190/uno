from unittest import skip
from .cards import Card, Deck, Hand, NUMERIC, ACTION, WILD, COLORS
from .player import Player, RandomAIPlayer, HumanPlayer
from .io import IO
from .exceptions import EmptyDeckError, EndGame



class PlayerList: 
    """A class representing a list of players in the UNO game."""
    
    def __init__(self, num_players:int=2, names:list[str]=[], specs:list[str]=[]):
        
        if len(specs) == 0:
            specs = [''] * num_players
        elif len(specs) == 1:
            # If only one spec is provided, assume all players are of that type
            specs = [specs[0]] * num_players
        elif len(specs) != num_players:
            print("Warning: The number of player specifications does not match the number of players. Initializing AI players...")
            specs = [''] * num_players 
        
        if len(names) != num_players:
            print("Warning: The number of player names does not match the number of players. Using default names...")
            names = [f"Player {i+1}" for i in range(num_players)]
        
        self._players = [self.create_player(name, spec) for name, spec in zip(names, specs)]
        self._num_players = len(self._players)

        self._index = 0     # Index of the current player
        self._dir = 1       # Direction of play (1 for clockwise, -1 for counter-clockwise)
        self._skip = 0      # Number of players to skip


    def create_player(self, name: str, spec: str) -> Player:
        """Create a player based on the specification."""
        match spec.lower():
            case 'ai':
                return RandomAIPlayer(name)
            case 'human':
                return HumanPlayer(name, IO())
            case '':
                return RandomAIPlayer(name)  # Default to AI if no spec is provided
            case _:
                print(f"Warning: Unknown player specification '{spec}'. Defaulting to AI player.")
                return RandomAIPlayer(name)  # Default to AI if no spec is provided



    def __len__(self) -> int:
        """Return the number of players in the list."""
        return self._num_players
    
    def _next_index(self, cur_index:int, skip:bool=False) -> int:
        """Get the current player."""
        return (cur_index + self._dir*(int(skip) + 1)) % self._num_players

    @property
    def cur_player(self) -> Player:
        """Get the current player."""
        return self._players[self._index]

    @property
    def next_player(self) -> Player:
        """Get the next player."""
        return self._players[self._next_index(self._index)]
    
    def update(self, skip:bool=False) -> None:
        """Update the current player index to the next player."""
        self._index = self._next_index(self._index, skip)

    def flip_direction(self) -> None:
        """Skip the next player."""
        self._dir *= 1


    def __iter__(self):
        """Return an iterator over the players, starting from the current player."""
        return iter([self._players[(self._index + i) % self._num_players] for i in range(self._num_players)])
    


class Game:
    """A class representing a UNO game."""

    def __init__(self, num_players:int=2, names:list[str]=[], specs:list[str]=[]):
        if num_players < 2:
            raise ValueError("A game of UNO requires at least 2 players.")
        
        self.IO = IO()  # Initialize IO for input/output operations
        self.players = PlayerList(num_players, names, specs)       
        
        self.main_deck = Deck()
        self.discard_deck = Deck(empty=True)  # Discard deck starts empty
        self.active_cards = []  # Cards currently in play
        self.active_color = None  # The color of the active deck, initially None        


    @property
    def top_card(self) -> Card:
        """Get the top card of the active deck."""
        if len(self.active_cards) == 0:
            raise ValueError("No active cards in play.")
        return self.active_cards[-1]


    @property
    def num_players(self) -> int:
        """Get the number of players in the game."""
        return len(self.players)
    
    
    def deal_cards(self, num_cards: int = 7):
        """Deal cards to each player."""
        if num_cards < 1:
            raise ValueError("Must deal at least 1 card to each player.")
        
        for _ in range(num_cards):
            for player in self.players:
                player.add_cards(self.draw_new_card())


    def play(self) -> None:
        """The main game loop."""
        
        self.deal_cards()
        self.IO.write(f"Starting a {len(self.players)}-player game of UNO! Players have been dealt their cards.")
        self.IO.show_help()

        self.active_cards.append(self.draw_new_card())
        self.active_color = self.get_active_color()        

        ctr = 0
        while True:
            ctr += 1 
            total_cards = sum(player._hand.size for player in self.players) \
                + self.main_deck.size + self.discard_deck.size + len(self.active_cards)
            
            self.IO.write(f"\nROUND #{ctr}: The draw deck has {self.main_deck.size} cards and the discard deck has  {self.discard_deck.size} cards. Total cards in play: {total_cards}.") 

            self.IO.write(f"{self.players.cur_player.name}'s turn. The active color is {self.active_color.upper()} and top card is: ", self.active_cards[-1]) 
            self.IO.show_hand(self.players.cur_player._hand.cards)
            cards = self.players.cur_player.move(self.top_card, self.active_color)
            
            if not self.top_card.is_valid_play(cards, self.active_color):
                self.IO.write("Not a valid move! Please choose another card. ")
                self.players.cur_player.add_cards(cards)
                ctr -= 1 
                continue  

            if len(cards) > 0:
                self.IO.write(f"{self.players.cur_player.name} played: ", cards[0])
                self.execute_turn(cards)
            else:
                self.IO.write(f"{self.players.cur_player.name} has no playable cards. Drawing a card...")
                new_card = self.draw_new_card()
                if self.top_card.is_valid_play([new_card], self.active_color):
                    self.IO.write(f"{self.players.cur_player.name} played the drawn card, ", new_card)
                    self.execute_turn([new_card])
                else:
                    self.IO.write(f"{self.players.cur_player.name} drew a card and added to their deck.")
                    self.players.cur_player.add_cards(new_card)

            # Check if the game is over
            if self.players.cur_player.is_done():
                print(f"{self.players.cur_player.name} is done! ")
                break
            

    def draw_new_card(self) -> Card:
        """Draw a new card from the main deck."""
        try:
            return self.main_deck.draw_card()
        except EmptyDeckError:
            print("The main deck is empty! Shuffling the discard deck back into the main deck.")
            self.main_deck.add_cards(self.discard_deck.remove_all())
            return self.main_deck.draw_card()


    def execute_turn(self, cards: list[Card]) -> None:
        """Execute a turn for the current player."""

        # Update the active deck based on if the card is stackable
        if cards[0].is_stackable():
            self.active_cards.extend(cards)
        else:                
            self.discard_deck.add_cards(self.active_cards)
            self.active_cards.clear() 
            self.active_cards.extend(cards)
        self.active_color = self.get_active_color()

        # Implement the logic for playing a card
        # Multiple cards can be played in a single turn only if they are identical, 
        skip_flag = self.play_card(cards[0])        

        # Change the active player to the next player
        self.players.update(skip=skip_flag)


    def play_card(self, card: Card) -> bool:
        """Play a card and update the game state accordingly."""
        skip_flag = False

        if card.id == 'skip':
            # If a skip card is played, the next player will be skipped
            self.IO.skip(self.players.next_player.name)
            skip_flag = True
            
        elif card.id == 'reverse':
            # If a reverse card is played, the play direction is reversed
            self.IO.reverse(self.players.next_player.name)
            if self.num_players > 2:
                self.players.flip_direction()         
            else:
                skip_flag = True

        elif card.id == 'draw2':
            # If a draw2 card is played, the next player must draw 2 cards
            
            # TODO: IMPLEMENT STACKING HERE!!!
            self.IO.draw2(self.players.next_player.name)
            for _ in range(2):
                self.players.next_player.add_cards(self.draw_new_card())
            skip_flag = True

        elif card.id == 'draw4': 
            self.IO.draw4(self.players.next_player.name)
            for _ in range(4):
                self.players.next_player.add_cards(self.draw_new_card())
            skip_flag = True

        return skip_flag


    def get_active_color(self) -> str|None:
        """Get the current active color."""
        if self.top_card.is_wild():
            return self.players.cur_player.choose_color()
        else:
            return self.top_card.color
