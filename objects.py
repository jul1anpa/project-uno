import random

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


# Pygame set up
import pygame

pygame.init()

screenWidth, screenHeight = 800, 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("UNO")


from enum import Enum

zeroImage = pygame.image.load('graphics/Zero.png')

class CardType(Enum):
    ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
    # Then we have the other types, making this ENUM actually matter.
    SKIP = 10
    REVERSE = 11
    DRAW2 = 12
    WILD = 13
    WILD_DRAW_4 = 14

    # Since this is the first time some of you have ever seen ENUMs, and this is a teaching experience... This is not how I usually do ENUMS!
    # In C++ and Rust, they are usually just simple value types kind of like: 'enum CardType {ONE, TWO, THREE}', and we use them just as a normal variable
    # But with more object oriented languages, like Java, C#, and I guess Python, enums are classes which can have class functions.
    # So, to not let an opportunity go to waste, I'm using that class functionality here! We like to use this enums to get images, so I've added functionality here.
    def getImage(self):
        match self:
            case 0: return zeroImage # ZERO = 0. So as we matching self, if self is zero, then viola, we give the image for zero.
            case _: return zeroImage # If we somehow don't get any of the above cases, we default to zero.


wildCardImage = pygame.image.load('graphics/WildCard.png')

class CardColor(Enum):
    WILDCARD = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4

    def getImage(self):
        match self:
            case 0: return wildCardImage
            case _: return wildCardImage


purpleBorder = pygame.image.load('graphics/PurpleBorder.png')
'''
Represents a card in UNO.
'''
class Card:
    # These are defined outside of init as part of the class itself, due to init wanting to use a function that uses them 'combineSurface'
    type = CardType
    color = CardColor

    def combineSurface(self):
        # This defines the base surface of the card which we then layer color and type onto. We get the size of a card, and then make sure it has alpha (transparency)
        self.image = pygame.Surface(wildCardImage.get_size(), pygame.SRCALPHA)
        self.image.blit(self.color.getImage(), (0,0)) # Put the card color on the surface
        self.image.blit(self.type.getImage(), (0,0))  # Put the type onto the card color.

    def __init__(self, type : CardType, color : CardColor):
        self.type = type
        self.color = color
        self.selected = False

        self.combineSurface()
        
        # This is how we move the card image around. You can set the position via card.rectangle.center(x, y) and a bunch of other functions like .move(x, y)
        # Then we can send it to be rendered via screen.blit(card.image, card.rectangle)
        self.rectangle = self.image.get_rect()

    def display(self): 
        screen.blit(self.image, self.rectangle) # This just adds the card to the current screen. You will have to do screen.flip() to show it. 

    def displayAtCoords(self, x, y): # If you want to set coordinates as you display
        if x is None:
            x = self.rectangle.centerx
        if y is None:
            y = self.rectangle.centery

        self.rectangle.center = (x, y)
        self.display()

    def isHovered(self, mouse_pos):
        if self.rectangle.collidepoint(mouse_pos): # Check if the mouse is over the rectangle
            self.image.blit(purpleBorder, (0,0)) # We give the card a purple border to show it's being hovered over!
            return True
        else:
            self.combineSurface() # If it's not being hovered over, we reset it, so it no has a purple border.
            return False

arrow = pygame.image.load('graphics/Arrow.png')
class Hand:
    '''
    Represents a player's hand in the game.
    '''
    def __init__(self):
        self.cards = []
        self.firstCard = 0 # This is the left most card, as to be used for rendering. Refers to cards index.

    def addCard(self, card):
        '''
        Adds a card to the player's hand.
        '''
        self.cards.append(card)

    def lastCard(self): # This is a function since whenever we want the lastCard we should recalculate.
        cardsPerDisplay = int((screenWidth/64) - 2) # Cards are 48 pixels in width, but we want parts in between. We also want 2 places for the sides. 
        lastCard = self.firstCard + (cardsPerDisplay - 1) # cardsPerDisplay - 1, because the firstCard counts, and we start at 0.
        if lastCard > len(self.cards): lastCard = len(self.cards)
        return (lastCard)

    def isOverflowRight(self):
        cardNum = len(self.cards)
        if cardNum > self.lastCard(): # If there are more cards then the most right card, we are 'overflowing' to the right
            return True
        else:
            return False

    def isOverflowLeft(self):
        if 1 < self.firstCard: # If there is any card left of the current cards further left, we are 'overflowing' to the left
            return True
        else:
            return False


    def display(self):
        cardNum = len(self.cards)

        if self.isOverflowRight():
            screen.blit(arrow, ((screenWidth-72), (screenHeight - 72))) # Without a defined rectangle, blit renders from the top left down.

        if self.isOverflowLeft():
            screen.blit(pygame.transform.flip(arrow, True, False), (0, screenHeight - 72)) # We flip the arrow and have it now point left.

        currentCard = 1
        for i in range(self.firstCard, self.lastCard()):
            card = self.cards[i]
            if card.selected != True:
                card.displayAtCoords((currentCard+1) * 64, screenHeight - 36) # We add one so we have room for the left arrow
            else:
                card.display()
            currentCard += 1

    def shiftLeft(self):
        self.firstCard -= int((screenWidth/64) - 2)
        if self.firstCard < 0: self.firstCard = 0
    
    def shiftRight(self):
        self.firstCard += int((screenWidth/64) - 2)
        if self.firstCard >= len(self.cards): self.firstCard = len(self.cards) - 1

''' Current lycommented out, since I decided not to use them just yet. Just hit the left and right arrows to move between cards
    def rightArrowHovered(self, mouse_pos):
        if self.isOverflowRight():
            rightArrow = pygame.Rect((screenWidth-72), 72, 72, 72)
            if rightArrow.collidepoint(mouse_pos): return True
            else: return False
        else: return False
    
    def leftArrowHovered(self, mouse_pos):
        if self.isOverflowRight():
            leftArrow = pygame.Rect(0, 72, 72, 72)
            if leftArrow.collidepoint(mouse_pos): return True
            else: return False
        else: return False
'''
            
        
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


''' Uncomment this for an example on how the pygame elements work! Remember, you will need pygame, so run pip install pygame in your environment!
    Also, you will need to have your environment be in the project folder. That's where the images are accessed!

testHand = Hand()
for _ in range(30):  # We're just adding 30 cards really quickly
    testCard = Card(CardType.ZERO, CardColor.WILDCARD)
    testHand.addCard(testCard)

running = True
while running:
    mousePos = pygame.mouse.get_pos()
    clicked = False
    selected = False

    for event in pygame.event.get(): # This is for external interactions, like movement or keys.
        if event.type == pygame.QUIT:
            running = False

        # Just an example of how this would work, for something not like the big X quit button:
        if event.type == pygame.KEYDOWN: # We check if a key is down overall, to avoid the big elif below.
            match event.key: # A match statement is just nicer than a bunch of elifs here
                case pygame.K_LEFT: 
                    testHand.shiftLeft()
                case pygame.K_RIGHT:
                    testHand.shiftRight() 
        
    mouse_buttons = pygame.mouse.get_pressed()

    # Set a nice light blue background
    screen.fill((173, 216, 230))

    for i in range(testHand.firstCard, testHand.lastCard()):
        card = testHand.cards[i]
        isHovered = card.isHovered(mousePos)
        print(selected)
        print(card.selected)
        if isHovered == True and mouse_buttons[0] and selected == False: # This is drag and drop, and not selection.
            card.selected = True
            selected = True
            card.rectangle.center = mousePos
        elif card.selected == True and mouse_buttons[0] and selected == False: # Here, we give it another tick to update, if the mouse moves too fast.
            card.rectangle.center = mousePos
            card.selected == False
            selected = True
        else:
            card.selected = False # This is so it's drag and drop, and not selection. Otherwise, it'd be very awkward.

    testHand.display()

    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()

import sys
sys.exit()

'''