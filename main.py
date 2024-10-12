import objects as o
import game_logic as gl
import user_interface as ui
import pygame

def main():
    deck = gl.create_deck() # Initialize a deck
    gameState = o.GameState(deck) # Initialize the game state

    pygameWrapper = ui.PygameWrapper(800, 600)
    userInterface = ui.UserInterface(pygameWrapper, gameState.discardPile, gameState.drawPile)
    menu = ui.Menu(pygameWrapper)
    gameState.players = menu.mainMenu()

    gameState.userInterface = userInterface

    gl.game_loop(gameState)

    pygame.quit()



if __name__ == "__main__":
    main()