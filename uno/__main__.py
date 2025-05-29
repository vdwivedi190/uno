from .game import Game
from .exceptions import EndGame


game = Game(num_players=2, specs=['ai'])
try:
    game.play()
except KeyboardInterrupt:
    print("\nGame interrupted. Exiting...")
except EndGame as e:
    raise SystemExit("Game ended.")
# except Exception as e:
#     print(f"An error occurred: {e}")
finally:
    print("Thank you for playing UNO!")


