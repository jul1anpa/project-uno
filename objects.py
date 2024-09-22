class GameState:
    '''
    Represents the state of the game.
    '''
    def __init__(self):
        '''
        Initializes a game state with the given attributes.
        '''
        self.players = []
        self.currentPlayer = None
        self.direction = None
        self.winner = None

    def addPlayer(self, player):
        '''
        Add a player object to the list of players.
        '''
        self.players.append(player)



class Player:
    '''
    Represents a player in the UNO game.
    '''
    def __init__(self, name, isDealer=False):
        '''
        Initializes a player with the given attributes.

        :param name: str - The name of the player.
        :param isDealer: bool - Indicates if the player is the dealer. Defaults to False.
        '''
        self.name = name
        self.points = 0
        self.hand = Hand()
        self.isDealer = isDealer
        self.isTurn = False
        self.hasUno = False
        self.hasDrawnCard = False

    def playCard(self):
        ...

    def drawCard(self, card):
        ...

    def checkUno(self):
        ...




class Hand:
    '''
    Represents a player's hand in the game.
    '''
    def __init__(self):
        ...



class Card:
    '''
    Represents a card in UNO.
    '''
    def __init__(self):
        ...



class DiscardPile:
    '''
    Represents the discard pile in UNO.
    '''
    def __init__(self):
        ...



class DrawPile:
    '''
    Represents the draw pile in UNO.
    '''
    def __init__(self):
        ...
