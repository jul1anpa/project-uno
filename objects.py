import random

color = ('RED','GREEN','BLUE','YELLOW')
rank = ('0','1','2','3','4','5','6','7','8','9','Skip','Reverse','Draw2','Draw4','Wild')
ctype = {'0':'number','1':'number','2':'number','3':'number','4':'number','5':'number','6':'number',
            '7':'number','8':'number','9':'number','Skip':'action','Reverse':'action','Draw2':'action',
            'Draw4':'action_nocolor','Wild':'action_nocolor'}

class GameState:
    '''
    Represents the state of the game.
    '''
    def __init__(self):
        '''
        Initializes a game state with the given attributes.
        '''
        self.players = []
        self._currentPlayer = None
        self._direction = None
        self.winner = None

    @property
    def currentPlayer(self):
        '''
        Returns the current Player.
        '''
        return self._currentPlayer

    @currentPlayer.setter
    def currentPlayer(self, player):
        '''
        Sets the initial player for turn order.
        '''
        if isinstance(player, Player):
            self._currentPlayer = player
        else:
            raise ValueError("Initial player must be a Player object.")
        
    @property
    def direction(self):
        '''
        Returns the current direction.
        '''
        return self._direction
    
    @direction.setter
    def direction(self, direction):
        '''
        Sets the direction of play.
        '''
        self._direction = direction

    def addPlayer(self, player):
        '''
        Add a player object to the list of players.
        '''
        if isinstance(player, Player):
            self.players.append(player)
        else:
            raise ValueError("Players must have a Player object type.")
        
    def setDealer(self):
        '''
        Determines which player is the dealer at the start of the game.
        '''
        ...
        
    def dealCards(self, drawPile):
        '''
        Deals seven cards to each player.
        '''
        for player in self.players:
            for i in range(7):
                card = drawPile.draw()
                player.hand.addCard(card)



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
        self._name = name
        self._points = 0
        self.hand = Hand()
        self.isDealer = isDealer
        self.isTurn = False
        self.hasUno = False
        self.hasDrawnCard = False

    @property
    def name(self):
        '''
        Returns the player's name.
        '''
        return self._name
    
    @name.setter
    def name(self, name):
        '''
        Sets the players name.
        '''
        if isinstance(name, str) and name.strip():
            self._name = name
        else:
            raise ValueError("Name must be a non-empty string value.")

    @property
    def points(self):
        '''
        Returns the point total a player has.
        '''
        return self._points
    
    @points.setter
    def points(self, points):
        '''
        Sets a player's point total.
        '''
        if isinstance(points, int):
            self._points += points
        else:
            raise ValueError("Points must be an integer value.")

    def playCard(self, discardPile, card):
        '''
        Plays a card from the player's hand and stores it in the discard pile.
        '''
        ...

    def drawCard(self, drawPile):
        '''
        Draws a card from the draw pile and stores it in the player's hand.
        '''
        if not drawPile.isEmpty():
            card = drawPile.draw()
            self.hand.addCard(card)

    def checkUno(self):
        '''
        Checks if the player's hand size is equal to one and determines whether or not they have UNO.
        '''
        if len(self.hand.cards) == 1:
            self.hasUno = True
        else:
            self.hasUno = False



class Hand:
    '''
    Represents a player's hand in the game.
    '''
    def __init__(self):
        self.cards = []

    def addCard(self, card):
        '''
        Adds a card to the player's hand.
        '''
        self.cards.append(card)


class Card:
    '''
    Represents a card in UNO.
    '''
    def __init__(self, color, rank):
        self.rank = rank
        self.deck = []

        if ctype[rank] == 'number':
            self.color = color
        elif ctype[rank] == 'action':
            self.color = color
        else:
            self.color = None

        for clr in color:
            for ran in rank:
                if ctype[ran] != 'action_nocolor':
                    self.deck.append(Card(clr, ran))
                    self.deck.append(Card(clr, ran))
                else:
                    self.deck.append(Card(clr, ran))



class DiscardPile:
    '''
    Represents the discard pile in UNO.
    '''
    def __init__(self):
        self.cards = []

    def addCard(self, card):
        '''
        Appends a card being played to the discard pile.
        '''
        self.cards.append(card)

    def takeAllButTopCard(self):
        '''
        Returns all cards except the top most one.
        '''
        topCard = self.cards[-1]
        restOfCards = self.card[:-1]
        self.cards.append(topCard)
        return restOfCards

class DrawPile:
    '''
    Represents the draw pile in UNO.
    '''
    def __init__(self, cards):
        self.cards = cards

    def isEmpty(self):
        '''
        Returns a boolean depending on whether the draw pile is empty or not. 
        '''
        return len(self.cards) == 0

    def draw(self):
        '''
        Returns the last card stored in the draw pile or reshuffles the draw pile if there are none left.
        '''
        if self.cards:
            return self.cards.pop()
        else:
            self.reshuffle()
    
    def shuffleInitial(self):
        '''
        Shuffle the draw pile at the beginning of the game.
        '''
        random.shuffle(self.cards)

    def reshuffle(self, discardPile):
        '''
        Shuffles the draw pile once all cards have been drawn.
        '''
        self.cards = discardPile.takeAllButTopCard()
        random.shuffle(self.cards)
