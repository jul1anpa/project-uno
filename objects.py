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
        self._direction = "clockwise"
        self.hasWinner = False
        self.roundWon = False
        self.gameWinner = None
        self.round = 1
        self.discardPile = DiscardPile()
        self.drawPile = DrawPile()

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
        if isinstance(player, Player) or isinstance(player, ComputerPlayer):
            self.players.append(player)
        else:
            raise ValueError("Players must have a Player or ComputerPlayer object type.")
        
    def setDealer(self):
        '''
        Determines which player is the dealer at the start of the game.
        '''
        ...

    def dealCards(self):
        '''
        Deals seven cards to each player at the start of the game.
        '''
        for player in self.players:
            while player.hand.countCards() < 7:
                player.drawCard(self.drawPile)

    def setTopCard(self):
        '''
        Places top card of draw pile on discard pile to begin play.
        '''
        # Need to add logic for if a card is a Wild or Wild Draw 4
        card = self.drawPile.draw()
        self.discardPile.addCard(card)

    def checkWinner(self):
        '''
        Checks each player's score to determine if there is a winner. To win a game, a player must have a score of at least 500.
        '''
        for player in self.players:
            if player.points >= 500:
                self.hasWinner = True
                self.winner = player
                return True
            else:
                return False

    def nextRound(self):
        '''
        Increments round number and empties player hand's and discard pile back into the draw pile.
        '''
        self.round += 1
        for player in self.players:
            player.resetHand(self.drawPile)
        discardPileCards = self.discardPile.removeAllCards()
        for card in discardPileCards:
            self.drawPile.addCard(card)



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

    def callUno(self):
        '''
        Checks if the player's hand size is equal to one and determines whether or not they have UNO.
        '''
        if len(self.hand.cards) == 1:
            self.hasUno = True
        else:
            self.hasUno = False

    def resetHand(self, drawPile):
        '''
        Removes cards from hand and adds them back into the draw pile.
        '''
        cards = self.hand.removeAllCards()
        for card in cards:
            drawPile.addCard(card)




class ComputerPlayer(Player):        
    def playCard(self, topCard):
        '''
        Computer player plays a card from hand that matches the top card or a wild card. If there are no playable cards, the computer
        player will draw a card instead.
        '''
        playable_cards = [card for card in self.hand if card.color == topCard.color or card.value == topCard.value or card.value == "Wild"]
        
        if playable_cards:
            chosen_card = random.choice(playable_cards)
            self.hand.removeCard(chosen_card)
            print(f"{self.name} plays: {chosen_card}")
            return chosen_card
        else:
            self.drawCard()



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

    def removeCard(self, card):
        '''
        Remove a card from the hand and return it.
        '''
        if card in self.cards:
            self.cards.remove(card)
            return card
    
    def removeAllCards(self):
        '''
        Removes all cards from the hand and returns them.
        '''
        cards = self.cards
        self.cards.clear()
        return cards

    def isEmpty(self):
        '''
        Returns a boolean depending on if a player's hand is empty or not.
        '''
        return len(self.cards) == 0



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

    def removeAllCards(self):
        '''
        Removes all of the cards in the discard pile and returns them.
        '''
        cards = self.cards
        self.cards.clear()
        return cards

    def removeAllButTopCard(self):
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
    
    def addCard(self, card):
        '''
        Appends a card to the draw pile.
        '''
        self.cards.append(card)

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