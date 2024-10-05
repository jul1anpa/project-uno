import pygame
import threading # This is just for cooldowns on clicking!

CARD_WIDTH = 48
CARD_HEIGHT = 72

class PygameWrapper:
    def __init__(self, screenWidth, screenHeight):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        pygame.display.set_caption("UNO")

        self.zeroImage = pygame.image.load('graphics/Zero.png')
        self.wildCardImage = pygame.image.load('graphics/WildCard.png')

        self.purpleBorder = pygame.image.load('graphics/PurpleBorder.png')
        self.cardTopImage = pygame.image.load('graphics/CardTop.png')
        self.arrowImage = pygame.image.load('graphics/Arrow.png')
        self.unoButtonImage = pygame.image.load('graphics/unoButton.png')

    def getType(self, rank):
        match rank:
            case 0: 
                return self.zeroImage # ZERO = 0. So as we matching self, if self is zero, then viola, we give the image for zero.
            case _: 
                return self.zeroImage # If we somehow don't get any of the above cases, we default to zero.

    def getColor(self, color):
        match color:
            case _: 
                return self.wildCardImage


class Clickable:
    def __init__(self, width, height, clickedObject, hoverTexture, pygameWrapper):
        self.width = width
        self.height = height
        self.clickedObject = clickedObject
        self.hoverTexture = hoverTexture
        self.pygameWrapper = pygameWrapper
        self.clicked = False
        
        # This defines the base surface of the card which we then layer any graphics to
        # You will want to use Clickable.image.blit(graphics, (x, y)) to add a layer.
        # To refresh a clickable, you will want to reset it by running the below line again: self.image = pygame.Surface 
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.graphics = [] # This list is used for the graphics put onto the image in order: #2 is layered ontop of #1!
        
        # This is how we move the image around. You can set the position via card.rectangle.center(x, y) and a bunch of other functions like .move(x, y)
        # Then we can send it to be rendered via screen.blit(card.image, card.rectangle)
        self.rectangle = self.image.get_rect()

    def returnObject(self):
        return self.clickedObject

    def addGraphic(self, graphic):
        self.graphics.append(graphic)
        self.image.blit(graphic, (0, 0))

    def resetImage(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for graphic in self.graphics:
            self.image.blit(graphic, (0, 0))

    def display(self): 
        self.pygameWrapper.screen.blit(self.image, self.rectangle) # This just adds the card to the current screen. You will have to do screen.flip() to show it. 

    def displayAtCoords(self, x, y): # If you want to set coordinates as you blit
        if x is None:
            x = self.rectangle.centerx
        if y is None:
            y = self.rectangle.centery

        self.rectangle.center = (x, y)
        self.display()

    def isHovered(self, mouse_pos):
        if self.rectangle.collidepoint(mouse_pos): # Check if the mouse is over the rectangle
            if self.hoverTexture is not None: 
                self.image.blit(self.hoverTexture, (0,0))
            return True
        else:
            self.resetImage() # If it's not being hovered over, we reset it removing the hoverTexture
            return False
        
    def isClicked(self, mouse_buttons, mouse_pos):
        # Return if the clickable is hovered, and the mouse has clicked mouse1.
        return (self.isHovered(mouse_pos) and mouse_buttons[0])
    
# I don't now if we're using enums now, since Ryan's card used dictionaries, so I made this a dictionary!
# When you call UserInterface.interfaceUser, it'll either return one of these values or the card they want to play to the discardpile.
userReturnType = {-1: "window exited", 0:"uno clicked", 1: "draw card"}
        
class UserInterface:
    def __init__(self, pygameWrapper, discardPile, drawPile):
        self.pygameWrapper = pygameWrapper
        self.currentUser = None
        self.clickCooldown = False

        self.discardPile = discardPile
        self.discardClick = Clickable(CARD_WIDTH, CARD_HEIGHT, discardPile, None, self.pygameWrapper)
        self.discardClick.addGraphic(self.pygameWrapper.getColor(self.discardPile.cards[-1].color))
        self.discardClick.addGraphic(self.pygameWrapper.getType(self.discardPile.cards[-1].rank))
        
        self.drawPile = drawPile
        self.drawClick = Clickable(CARD_WIDTH, CARD_HEIGHT, drawPile, None, self.pygameWrapper)
        self.drawClick.addGraphic(self.pygameWrapper.cardTopImage)

        self.rightArrow = Clickable(CARD_HEIGHT, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.rightArrow.addGraphic(self.pygameWrapper.arrowImage)

        self.leftArrow = Clickable(CARD_HEIGHT, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.leftArrow.addGraphic(pygame.transform.flip(self.pygameWrapper.arrowImage, True, False))

        self.unoButton = Clickable(CARD_HEIGHT, CARD_WIDTH, None, None, self.pygameWrapper)
        self.unoButton.addGraphic(self.pygameWrapper.unoButtonImage)

        self.firstCard = 0
        self.lastCard = 0
        self.cards = []

    def turnOffClickCooldown(self):
        self.clickCooldown = False

    def turnOnClickCooldown(self):
        self.clickCooldown = True
        threading.Timer(1.0, self.turnOffClickCooldown).start()

    def updateCards(self, player):
        self.cards = []
        for card in player.hand.cards:
            newCard = Clickable(CARD_WIDTH, CARD_HEIGHT, card, self.pygameWrapper.purpleBorder, self.pygameWrapper)
            newCard.addGraphic(self.pygameWrapper.getColor(card.color))
            newCard.addGraphic(self.pygameWrapper.getType(card.rank))
            self.cards.append(newCard)
    
    def updateLastCard(self, player):
        cardsPerRender = int((self.pygameWrapper.screenWidth/64) - 2) # Cards are 48 pixels but we want parts in between. We also want 2 places for arrows
        self.lastCard = self.firstCard + (cardsPerRender - 1) # cardsPerDisplay - 1, because the firstCard counts, and we start at 0.
        if self.lastCard > len(player.hand.cards): 
            self.lastCard = len(player.hand.cards)

    def updateUserState(self, player):
        self.updateLastCard(player)
        self.updateCards(player)

    def render(self):
        # We display these first, so cards can then be displayed ontop of them.
        if len(self.cards) > self.lastCard: 
            self.rightArrow.displayAtCoords(self.pygameWrapper.screenWidth-CARD_HEIGHT/2, self.pygameWrapper.screenHeight-CARD_HEIGHT/2)
        if 1 < self.firstCard:
            self.leftArrow.displayAtCoords(CARD_HEIGHT/2, self.pygameWrapper.screenHeight-CARD_HEIGHT/2)
        self.discardClick.displayAtCoords(self.pygameWrapper.screenWidth/2 + CARD_WIDTH, self.pygameWrapper.screenHeight/4)
        self.drawClick.displayAtCoords(self.pygameWrapper.screenWidth/2 - CARD_WIDTH, self.pygameWrapper.screenHeight/4)
        self.unoButton.displayAtCoords(CARD_HEIGHT/2, CARD_WIDTH/2)

        currentCard = 1 # Though the list starts at 0, the "physical" cards start at 1. There is no "0th" card in our 2D space.
        for i in range(self.firstCard, self.lastCard):
            card = self.cards[i]
            if not card.clicked:
                card.displayAtCoords((currentCard+1) * 64,  self.pygameWrapper.screenHeight - CARD_HEIGHT/2) # We add one so we have room for the left arrow
            else:
                card.display()
            currentCard += 1

    def interfaceUser(self, player):
        self.currentUser = player
        self.updateUserState(player)
        while True:
            mousePos = pygame.mouse.get_pos()
            selected = None

            for event in pygame.event.get(): # This is for external interactions, like movement or keys.
                if event.type == pygame.QUIT: # Or for quitting out of the window!
                    return -1
                
            mouseButtons = pygame.mouse.get_pressed()

            # This sets a nice light blue background. We do this each frame to basically reset the screen.
            self.pygameWrapper.screen.fill((173, 216, 230))

            for i in range(self.firstCard, self.lastCard):
                card = self.cards[i]
                if card.isClicked(mouseButtons, mousePos) and selected is None: # This is drag and drop, and not selection.
                    selected = card
                    card.clicked = True
                    card.rectangle.center = mousePos
                # This elif is to give it another change to keep following if the mouse moves too fast.
                elif card.isClicked(mouseButtons, mousePos) and selected is None: 
                    card.rectangle.center = mousePos
                    selected = card
                else:
                    card.clicked = False # This is so it's drag and drop, and not selection. Otherwise, it'd be very awkward!

            self.render()
            pygame.display.flip() # This actually updates the display

            if not self.clickCooldown:
                if self.leftArrow.isClicked(mouseButtons, mousePos): 
                    self.firstCard -= int((self.pygameWrapper.screenWidth/64) - 2)
                    if self.firstCard < 0: 
                        self.firstCard = 0
                    self.updateLastCard(player)
                    self.turnOnClickCooldown()

                if self.rightArrow.isClicked(mouseButtons, mousePos):
                    self.firstCard += int((self.pygameWrapper.screenWidth/64) - 2)
                    if self.firstCard >= len(self.cards): 
                        self.firstCard = len(self.cards) - 1
                    self.updateLastCard(player)
                    self.turnOnClickCooldown()

                if self.unoButton.isClicked(mouseButtons, mousePos): 
                    return 0
                
                if self.drawClick.isClicked(mouseButtons, mousePos): 
                    return 1
                
                if self.discardClick.isClicked(mouseButtons, mousePos) and selected is not None:
                    return selected.clickedObject

""" Example Code. Uses Ryan's card from this branch: https://github.com/jul1anpa/project-uno/tree/CardClass
from objects import Player, DiscardPile, DrawPile

color = ('RED','GREEN','BLUE','YELLOW')
rank = ('0','1','2','3','4','5','6','7','8','9','Skip','Reverse','Draw2','Draw4','Wild')
ctype = {'0':'number','1':'number','2':'number','3':'number','4':'number','5':'number','6':'number',
            '7':'number','8':'number','9':'number','Skip':'action','Reverse':'action','Draw2':'action',
            'Draw4':'action_nocolor','Wild':'action_nocolor'}

class RyanCard:
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
''' I'm pretty sure this is broken; it infinitely loops.
        for clr in color:
            for ran in rank:
                if ctype[ran] != 'action_nocolor':
                    self.deck.append(RyanCard(clr, ran))
                    self.deck.append(RyanCard(clr, ran))
                else:
                    self.deck.append(RyanCard(clr, ran))
'''

player = Player("Test")
for _ in range(30):  # We're just adding 30 cards really quickly
    testCard = RyanCard("RED", '0')
    player.hand.addCard(testCard)

pygameWrapper = PygameWrapper(800, 600)
discardPile = DiscardPile()
discardPile.addCard(RyanCard("RED", '0'))
drawPile = DrawPile(None)
userInterface = UserInterface(pygameWrapper, discardPile, drawPile)

running = True
while running:
    userInput = userInterface.interfaceUser(player)
    if isinstance(userInput, RyanCard):
        print("We played a card!")
    else:
        match userInput:
            case -1:
                print("We closed out of the window!")
                running = False
            case 0:
                print("Uno pressed!")
            case 1:
                print("Draw pressed!")
        # You will probably want to add a wait before taking more userInput, or else you may get spammed with inputs.
        # Here, as we have no wait, when we click the draw button we draw a card every frame!
pygame.quit()
"""