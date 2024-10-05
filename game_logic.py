import objects as obj

def game_loop():
    '''
    Main game loop that runs until a player is determined to be the winner. 

    Initializes the game state, sets up rounds, handles play, and scores rounds.
    Continues looping through rounds until a player wins the game.
    '''
    gameState = obj.GameState() # Initialize the game state

    # How are players going to be added to the game state? via Pygame?



    while not gameState.hasWinner: # Create game loop that runs until there is a winner
        setup_round(gameState)
        play_round(gameState)
        score_round(gameState)
        gameState.checkWinner() # Checks for winner and sets hasWinner to True if one is found
        gameState.nextRound() # Proceeds to next round if there is no winner



def setup_round(gameState):
    '''
    Sets up a new round in the game.

    Shuffles the draw pile, assigns the dealer, deals cards to players, and sets the top card on the discard pile.

    Parameters:
        gameState (GameState): The current game state object.
    '''
    gameState.drawPile.shuffleInitial()
    gameState.setDealer()
    gameState.dealCards()
    gameState.setTopCard()



def play_round(gameState):
    '''
    Executes a round loop that runs until a player has played all of their cards.

    Loops through each player in the game, sets the current player, allows a player to take a turn, and checks if their hand is empty.

    Parameters:
        gameState (GameState): The current game state object.
    '''
    while not gameState.roundWon: # Create round loop that runs until a round has been won
        for player in gameState.players: # Loop through each player's turn
            gameState.currentPlayer(player)
            take_turn(player, gameState) # Execute turn logic for each player
            if player.hand.isEmpty():
                gameState.roundWon = True



def score_round(gameState):
    '''
    Handles scoring logic at the end of the round.

    Parameters:
        gameState (GameState): The current game state object.
    '''
    ... # Handle scoring here 



def take_turn(player, gameState):
    '''
    Executes a player's turn in the game.

    Parameters:
        player (Player): The player whose turn it is.
        gameState (GameState): The current game state object.
    '''
    player.drawCard() # Each player begins by drawing a card
    
    # Need logic for playable cards
