import objects as obj

def game_loop(gameState):
    '''
    Main game loop that runs until a player is determined to be the winner. 

    Initializes the game state, sets up rounds, handles play, and scores rounds.
    Continues looping through rounds until a player wins the game.
    '''
    while not gameState.hasWinner: # Create game loop that runs until there is a winner
        setup_round(gameState)
        play_round(gameState)
        score_round(gameState)
        gameState.checkWinner() # Checks for winner and sets hasWinner to True if one is found
        gameState.nextRound() # Proceeds to next round if there is no winner
    
    gameState.userInterface.pygameWrapper.textPopUp([f"{gameState.gameWinner.name} has won the game in {gameState.round} rounds!"])



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
            deck.append(obj.Card(color, action, action)) # Creates two copies of each action for each color
            deck.append(obj.Card(color, action, action))
    
    for wild in wilds:
        for _ in range(4):
            deck.append(obj.Card(None, wild, wild)) # Creates four copies of each wild action
    
    return deck



def setup_round(gameState):
    '''
    Sets up a new round in the game.

    Shuffles the draw pile, assigns the dealer, deals cards to players, and sets the top card on the discard pile.

    Parameters:
        gameState (GameState): The current game state object.
    '''
    gameState.drawPile.shuffleInitial()
    # gameState.setDealer() Excluding this function since we choose the dealer manually in the application
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
        print(f"The current player is {currentPlayer.name}.\nPlayer Index: {gameState.currentPlayerIndex}")
        take_turn(currentPlayer, gameState)
        if currentPlayer.hand.isEmpty():
            gameState.roundWinner = currentPlayer
            gameState.roundWon = True
    
    gameState.userInterface.pygameWrapper.textPopUp([f"{gameState.roundWinner.name} has won the round!"])



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
    
    gameState.roundWinner.points = scoredPoints

    gameState.userInterface.pygameWrapper.textPopUp([f"{gameState.roundWinner.name} scored {gameState.roundWinner.points} points!"])

    gameState.roundWinner = None



def take_turn(player, gameState):
    '''
    Executes a player's turn in the game.

    Parameters:
        player (Player): The player whose turn it is.
        gameState (GameState): The current game state object.
    '''

    playableCards = [card for card in player.hand.cards if gameState.isCardPlayable(card)]

    if type(player) is obj.Player: # Checks if the player is a Player object

        while True:
            userInput = gameState.userInterface.interfaceUser(player)

            if isinstance(userInput, obj.Card) and userInput in playableCards:
                gameState.playCard(player, userInput)
                return
            
            else:
                match userInput:

                    case 0:
                        player.callUno()
                        print("Uno pressed!")

                    case 1:
                        player.drawCard(gameState.drawPile, gameState.discardPile)
                        print(f"{player.name} has drawn a card!")
                        print(f"{player.name} hand size is now {len(player.hand.cards)}\n")

                        drawnCard = player.hand.cards[-1]

                        willPlayCard = gameState.userInterface.promptPlayCard(drawnCard)

                        if willPlayCard and gameState.isCardPlayable(drawnCard):
                            gameState.playCard(player, drawnCard)
                            return

                        gameState.nextPlayer()
                        return

    elif type(player) is obj.ComputerPlayer: # Checks if the player is a ComputerPlayer object

        if len(playableCards) > 0:
            gameState.playCard(player, None, playableCards)
            return
        
        else:
            player.drawCard(gameState.drawPile, gameState.discardPile)
            print(f"{player.name} has drawn a card!")
            print(f"{player.name} hand size is now {len(player.hand.cards)}\n")

            drawnCard = player.hand.cards[-1]

            if gameState.isCardPlayable(drawnCard):
                gameState.playCard(player, drawnCard, playableCards)
                return

            gameState.nextPlayer()

    else:
        "Error: Turn not taken"