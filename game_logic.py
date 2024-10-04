import objects as obj

def game_loop():
    gameState = obj.GameState() # Initialize the game state

    # How are players going to be added to the game state via Pygame?



    while not gameState.hasWinner: # Create game loop that runs until there is a winner
        setup_round(gameState)
        play_round(gameState)
        gameState.checkWinner() # Checks for winner and sets hasWinner to True if one is found
        gameState.nextRound() # Proceeds to next round if there is no winner

def setup_round(gameState):
    gameState.drawPile.shuffleInitial()
    gameState.setDealer()
    gameState.direction("Left")
    gameState.dealCards()
    gameState.setTopCard()

def play_round(gameState):
    while not gameState.roundWon: # Create round loop that runs until a round has been won
        for player in gameState.players: # Loop through each player's turn
            gameState.currentPlayer(player)
            take_turn(player, gameState) # Execute turn logic for each player


def take_turn(player, gameState):
    player.drawCard() # Each player begins by drawing a card
    
    # Need logic for playable cards
