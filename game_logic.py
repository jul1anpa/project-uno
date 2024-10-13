import objects as obj
import pygame

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
    cooldownTime = 2000
    currentTime = pygame.time.get_ticks()

    playableCards = [card for card in player.hand.cards if gameState.isCardPlayable(card)]

    if type(player) is obj.Player:
        while True:
            userInput = gameState.userInterface.interfaceUser(player)
            if (userInput, obj.Card) and userInput in playableCards:
                gameState.playCard(player, userInput)
                print(f"{player.name} played a card!")
                print(f"{player.name}'s hand size is now {len(player.hand.cards)}\n")

                if userInput.action is not None and userInput.action != "Wild" and len(gameState.players) == 2:
                    pass
                
                gameState.nextPlayer()
                return
            else:
                match userInput:
                    case 0:
                        player.callUno()
                        print("Uno pressed!")
                    case 1:
                        if currentTime > cooldownTime:
                            player.drawCard(gameState.drawPile)
                            # userInterface.promptPlayCard
                            print("Draw pressed!")
                            print(f"{player.name}'s hand size is now {len(player.hand.cards)}\n")
                            gameState.nextPlayer()
                            return

    elif type(player) is obj.ComputerPlayer:
        if len(playableCards) > 0:
            card = gameState.playCard(player, None, playableCards)
            print(f"{player.name} played a card!")
            print(f"{player.name}'s hand size is now {len(player.hand.cards)}\n")

            if card.action is not None and card.action != "Wild" and len(gameState.players) == 2:
                pass

            gameState.nextPlayer()
            return
        else:
            player.drawCard(gameState.drawPile)
            print(f"{player.name} has drawn a card!")
            print(f"{player.name} hand size is now {len(player.hand.cards)}\n")
            gameState.nextPlayer()

    else:
        "Error: Turn not taken"