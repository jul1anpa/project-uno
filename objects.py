import random

class GameState:
    '''
    Represents the state of the game.
    '''
    def __init__(self, deck, userInterface=None):
        '''
        Initializes a game state with the given attributes.

        :param deck: list - A list containing 108 Card objects.
        '''
        self.discardPile = DiscardPile()
        self.drawPile = DrawPile(deck)
        self.players = []
        self.currentPlayerIndex = 0
        self.dealer = None
        self.direction = 1 # Represented by +1 for clockwise direction or -1 for counter-clockwise direction
        self.round = 1
        self.roundWon = False
        self.roundWinner = None
        self.hasWinner = False
        self.gameWinner = None
        self.userInterface = userInterface

    def addPlayer(self, player):
        '''
        Add a player object to the list of players.

        :param player: Player object - Represents a player.
        '''
        if isinstance(player, Player) or isinstance(player, ComputerPlayer):
            self.players.append(player)
        else:
            raise ValueError("Players must have a Player or ComputerPlayer object type.")
        
    def setDealer(self):
        '''
        Determines which player is the dealer at the start of the game and sets the current player to the left of the dealer to begin play.
        '''
        highestValue = -1
        newDealer = None

        for player in self.players:
            card = self.drawPile.draw()
            if card.action is None and card.rank > highestValue: # Ensures that only number cards are considered and the card's value is higher than the current highest value
                highestValue = card.rank # Sets new highest value
                newDealer = player # Assigns dealer to the player who drew the highest value card
            self.drawPile.addCardToBottom(card) # Adds the drawn card back to the bottom of the draw pile

        if newDealer is None: # Handles edge case if no player draws a number card
            newDealer = self.players[0] # Sets new dealer to the first player in the players list

        self.dealer = newDealer

    def dealCards(self):
        '''
        Deals seven cards to each player at the start of the game.
        '''
        for player in self.players:
            while len(player.hand.cards) < 7:
                player.drawCard(self.drawPile)

    def setTopCard(self):
        '''
        Places top card of draw pile on discard pile to begin play and handles logic depending on what is drawn.
        '''
        card = self.drawPile.draw()

        while card.action == "Wild" or card.action == "Wild Draw Four":
            self.drawPile.addCardToBottom(card) 
            card = self.drawPile.draw()
        
        if card.action == "Draw Two":
            self.drawTwo()
        elif card.action == "Reverse":
            self.reverseDirection()
            self.nextPlayer()
        elif card.action == "Skip":
            self.skip()
        elif card.action is None:
            self.nextPlayer()

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
        self.roundWon = False
        for player in self.players:
            player.resetHand(self.drawPile)
        discardPileCards = self.discardPile.removeAllCards()
        self.drawPile += discardPileCards

    def isCardPlayable(self, card):
        '''
        Checks whether a card is able to be played or not.

        :param card: Card object - Represents a card.
        '''
        topCard = self.discardPile.topCard

        if card.color == topCard.color or card.rank == topCard.rank or card.action == "Wild" or card.action == "Wild Draw Four":
            return True
        
        return False
    
    def playCard(self, player, card=None, playableCards=None):
        '''
        Placeholder for a player playing a card from their hand.
        '''
        if isinstance(playableCards, list):
            card = random.choice(playableCards)

        if card.action is not None:

            if card.action == "Wild":
                # Need logic
                print("A Wild card was played.")
            elif card.action == "Skip":
                self.skip()
                print("A Skip card was played.")
            elif card.action == "Reverse":
                self.reverseDirection()
                print("A Reverse card was played.")
            elif card.action == "Draw Two":
                self.drawTwo()
                print("A Draw Two card was played.")
            elif card.action == "Wild Draw Four":
                self.drawFour()
                print("A Wild Draw Four card was played.")

        else:
            print(f"A {card.rank} was played.")

        cardToPlay = player.hand.removeCard(card)
        self.discardPile.addCard(cardToPlay)

        if type(player) is ComputerPlayer:
            return card

    def reverseDirection(self):
        '''
        Reverses the direction of play.
        '''
        self.direction *= -1

    def drawTwo(self):
        '''
        The player ahead of the current player draws two cards and is skipped.
        '''
        playerAffected = self.players[(self.currentPlayerIndex + self.direction) % len(self.players)]
        playerAffected.drawCard(self.drawPile)
        playerAffected.drawCard(self.drawPile)
        self.skip()

    def drawFour(self):
        '''
        The player ahead of the current player draws four cards and is skipped.
        '''
        playerAffected = self.players[(self.currentPlayerIndex + self.direction) % len(self.players)]
        for _ in range(4):
            playerAffected.drawCard(self.drawPile)
        self.skip()

    def skip(self):
        '''
        Skips the next player in turn order.
        '''
        self.currentPlayerIndex = (self.currentPlayerIndex + (self.direction * 2)) % len(self.players)

    def nextPlayer(self):
        '''
        Determines the next player's turn depending on direction of play.
        '''
        # The modulo operator is key here in order to wrap around the player list when incrementing past the end of the player list or decrementing past the beginning of the player list

        # A direction of 1 will increment the current player index by 1 (or clockwise direction of play)
        # When incrementing past the end of the list, the modulo operation will return 0

        # A direction of -1 will decrement the current player index by 1 (or counter-clockwise direction of play)
        # When decrementing past the beginning of the list, the modulo operation will return the value of the last index (If there are four players, it will return 3)

        # For example, if there are four players in the game and the current player is at index 0 and the direction is -1 (or counter-clockwise)
        # self.currentPlayerIndex = (0 + -1) % 4
        #                         = -1 % 4 = 3
        # The new currentPlayerIndex would now be set to 3 or the player at the end of the list

        # The modulus formula is helpful when trying to understand the logic behind the return value of the modulo operator
        # The formula is below:
        #                           a % b    =     a - b * floor(a/b)

        self.currentPlayerIndex = (self.currentPlayerIndex + self.direction) % len(self.players) 



class Player:
    '''
    Represents a player in the UNO game.
    '''
    def __init__(self, name):
        '''
        Initializes a player with the given attributes.

        :param name: str - The name of the player.
        :param isDealer: bool - Indicates if the player is the dealer. Defaults to False.
        '''
        self._name = name
        self._points = 0
        self.hand = Hand()
        self.hasUno = False

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
        drawPile.cards += cards



class ComputerPlayer(Player):     
    '''
    Represents a computer player in the UNO game.
    '''   



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
    def __init__(self, color=None, rank=None, action=None):
        '''
        Initializes a card with the given attributes.

        :param color: str - Indicates which color a card is or None.
        :param rank: int - Indicates what number value a card has or None.
        :param action: str - Indicates which action a card has or None.
        '''
        self.color = color
        self.rank = rank
        self.action = action
        self.points = self.assignPoints()

    def assignPoints(self):
        '''
        Assigns a card a point value depending on its face value and/ or special type. This point value is used for scoring at the end of each round.
        '''
        if self.rank is not None and isinstance(self.rank, int):
            return self.rank
        elif self.action == "Draw Two" or self.action == "Reverse" or self.action == "Skip":
            return 20
        elif self.action == "Wild" or self.action == "Wild Draw Four":
            return 50
        else:
            return 0
        
    def changeColor(self, color):
        '''
        For wild cards, changes the cards color to whatever the player has chosen.
        '''
        self.color = color



class DiscardPile:
    '''
    Represents a discard pile in UNO.
    '''
    def __init__(self):
        self.cards = [] # The top most card is represented by the last card in the list

    @property
    def topCard(self):
        '''
        Returns the top card of the discard pile.
        '''
        if len(self.cards) > 0:
            return self.cards[-1]
        return None

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
        restOfCards = self.cards[:-1]
        self.cards = topCard
        return restOfCards



class DrawPile:
    '''
    Represents a draw pile in UNO.
    '''
    def __init__(self, cards):
        '''
        Initializes a draw pile with the given attribute.

        :param cards: list - A list containing 108 Card objects.
        '''
        self.cards = cards # The top most card is represented by the last card in the list and vice versa

    def isEmpty(self):
        '''
        Returns a boolean depending on whether the draw pile is empty or not. 
        '''
        return len(self.cards) == 0
    
    def addCardToBottom(self, card):
        '''
        Adds a card to the bottom of the draw pile.
        '''
        self.cards.insert(0, card) # Inserts a card to the front of the cards list

    def addCardToTop(self, card):
        '''
        Adds a card to the top of the draw pile.
        '''
        self.cards.append(card) # Appends a card to the end of the cards list

    def draw(self):
        '''
        Returns the last card stored in the draw pile or reshuffles the draw pile if there are none left.
        '''
        if self.cards:
            return self.cards.pop() # Removes a card from the end of the cards list
        else:
            self.reshuffle()
            return self.cards.pop()
    
    def shuffleInitial(self):
        '''
        Shuffle the draw pile at the beginning of the game.
        '''
        random.shuffle(self.cards)

    def reshuffle(self, discardPile):
        '''
        Shuffles the draw pile once all cards have been drawn.
        '''
        self.cards = discardPile.removeAllButTopCard()
        random.shuffle(self.cards)