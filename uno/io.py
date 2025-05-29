from termcolor import colored, cprint

from .cards import Card
from .exceptions import EndGame

NUMBER_NAMES = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

class IO:
    """A class for handling input/output operations in the UNO game."""
    def read_card(self, cards: list[Card]) -> int:
        """Read a card from the user input.
        
        Return the index of the card in the hand, or -1 if no card is played."""
        while True:
            tmp = input("Please select a card to play from your hand. ")
            tmp = tmp.strip()

            if tmp == 'q':
                raise EndGame("Exiting the game.")            
            elif tmp == 'd':
                self.show_hand(cards)            
            elif tmp == 'h':
                self.show_help()            
            elif tmp.isdecimal() and tmp != '':
                card_num = int(tmp)
                if card_num == 0:
                    return -1
                elif 1 <= card_num <= len(cards):
                    return card_num - 1
                else:
                    print("Invalid card number. Please try again.")                    
            else:
                print("Invalid input!")


    def write(self, msg: str, card:Card|None=None) -> None:
        """Write a message to the user."""
        if card is None:
            print(msg)  
        else:
            print(msg, self.card_to_formatted_str(card))


    def skip(self, player_name:str) -> None:
        print(f"Skipping {player_name}!")

    def reverse(self, player_name:str) -> None:
        print(f"Reversing gameplay direction!")

    def draw2(self, player_name:str) -> None:
        print(f"{player_name} draws 2 cards from the main deck and skips their turn!")

    def draw4(self, player_name:str) -> None:
        print(f"{player_name} draws 4 cards from the main deck and skips their turn!")

    def show_help(self): 
        print("""At your turn, please select a card to play by entering the number next to it, when prompted. Alternatively, you can enter: 
   0   to skip playing a card (if you have no playable cards)
   d   to display your hand
   h   to display this help message
   q   to exit the game""")

    def show_hand(self, cards: list[Card], num:bool=True) -> None:
        """Display the player's hand."""
        print('   ', end='')
        for ind, card in enumerate(cards, start=1):
            if num:
                print(f'{ind}. ', end='')
            print(f'{self.card_to_formatted_str(card)}', end='   ')
        print('') 


    def card_to_formatted_str(self, card: Card) -> str:
        if card.is_wild():  
            return colored(f"{card}", 'white', attrs=['bold','underline'])
        elif card.is_action():  
            return colored(f"{card}", card.color, attrs=['bold'])
        else:
            return colored(f"{card}", card.color, attrs=['bold'])        
            # return colored(f"{NUMBER_NAMES[int(card.id)]} of {card.color}", card.color, attrs=['bold'])
