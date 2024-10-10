import objects as obj

def game_loop():
    '''
    Main game loop that runs until a player is determined to be the winner. 

    Initializes the game state, sets up rounds, handles play, and scores rounds.
    Continues looping through rounds until a player wins the game.
    '''
    deck = create_deck() # Initialize a deck

    gameState = obj.GameState(deck) # Initialize the game state

    while not gameState.hasWinner: # Create game loop that runs until there is a winner
        setup_round(gameState)
        play_round(gameState)
        score_round(gameState)
        gameState.checkWinner() # Checks for winner and sets hasWinner to True if one is found
        gameState.nextRound() # Proceeds to next round if there is no winner



def create_deck():
    '''
    Creates an UNO deck by initializing each Card with a color, rank, and/ or action.
    '''
    colors = ["Blue", "Green", "Red", "Yellow"]
    ranks = list(range(10))
    actions = ["Skip", "Reverse", "Draw Two"]
    wilds = ["Wild", "Wild Draw Four"]

    deck = []

    for color in colors:
        deck.append(obj.Card(color, 0)) # Creates a single 0 card for each color
        for rank in ranks[1:]:
            deck.append(obj.Card(color, rank)) # Creates two copies of each rank for each color
            deck.append(obj.Card(color, rank))
    
    for color in colors:
        for action in actions:
            deck.append(obj.Card(color, None, action)) # Creates two copies of each action for each color
            deck.append(obj.Card(color, None, action))
    
    for wild in wilds:
        for _ in range(4):
            deck.append(obj.Card(None, None, wild)) # Creates four copies of each wild action
    
    return deck



def setup_round(gameState):
    '''
    Sets up a new round in the game.

    Shuffles the draw pile, assigns the dealer, deals cards to players, and sets the top card on the discard pile.

    Parameters:
        gameState (GameState): The current game state object.
    '''
    gameState.drawPile.shuffleInitial()
    gameState.setDealer()
    gameState.drawPile.shuffleInitial()
    gameState.dealCards()
    gameState.setTopCard()



def play_round(gameState):
    '''
    Executes a round loop that runs until a player has played all of their cards.

    Loops through each player in the game, sets the current player, allows a player to take a turn, and checks if their hand is empty.

    Parameters:
        gameState (GameState): The current game state object.
    '''
    while not gameState.roundWon:
        currentPlayer = gameState.players[gameState.currentPlayerIndex]
        take_turn(currentPlayer, gameState)
        if currentPlayer.hand.isEmpty():
            gameState.roundWinner = currentPlayer
            gameState.roundWon = True



def score_round(gameState):
    '''
    Handles scoring logic at the end of the round and resets the round winner.

    Parameters:
        gameState (GameState): The current game state object.
    '''
    scoredPoints = 0
    for player in gameState.players:
        for card in player.hand.cards:
            scoredPoints += card.points
    
    gameState.roundWinner.points(scoredPoints)
    gameState.roundWinner = None



def take_turn(player, gameState):
    '''
    Executes a player's turn in the game.

    Parameters:
        player (Player): The player whose turn it is.
        gameState (GameState): The current game state object.
    '''
    player.drawCard() # Each player begins by drawing a card
    
    playableCards = [card for card in player.hand.cards if gameState.isCardPlayable(card)]
    
