import pygame
import threading # This is just for cooldowns on clicking!
import sys

from objects import ComputerPlayer, Player

CARD_WIDTH = 48
CARD_HEIGHT = 72
BAR_WIDTH = 512

# Minimum resolution is 360p! Needed since there's a lot of pixel logic, and any lower some screens could break.
MIN_SCREEN_WIDTH = 640
MIN_SCREEN_HEIGHT = 360


class PygameWrapper:
    def __init__(self, screenWidth, screenHeight):
        if screenWidth < MIN_SCREEN_WIDTH:
            self.screenWidth = MIN_SCREEN_WIDTH
        else:
            self.screenWidth = screenWidth
            self.lastWidth = screenWidth
        
        if screenHeight < MIN_SCREEN_HEIGHT:
            self.screenHeight = MIN_SCREEN_HEIGHT
            self.lastHeight = screenHeight
        else:
            self.screenHeight = screenHeight

        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        pygame.display.set_caption("UNO")
        self.fullscreen = False


        pygame.font.init()
        # This is the font we use to render graphics. 
        # It's this old one just because I like ASCII games, and grabbing from a users system files sounds scary.
        self.font = pygame.font.Font('graphics/Perfect DOS VGA 437.ttf', 12)

        self.logoImage = pygame.image.load('graphics/Logo.png')
        self.newGameImage = pygame.image.load('graphics/NewGame.png')
        self.settingsImage = pygame.image.load('graphics/Settings.png')
        self.exitImage = pygame.image.load('graphics/Exit.png')
        self.resolutionImage = pygame.image.load('graphics/Resolution.png')
        self.fullscreenImage = pygame.image.load('graphics/Fullscreen.png')

        self.playerChoiceImage = pygame.image.load('graphics/PlayerChoice.png')
        self.robotChoiceImage = pygame.image.load('graphics/RobotChoice.png')
        self.resetChoiceImage = pygame.image.load('graphics/ResetChoice.png')

        self.playerImage = pygame.image.load('graphics/Player.png')
        self.robotImage = pygame.image.load('graphics/Robot.png')

        self.zeroImage = pygame.image.load('graphics/Zero.png')
        self.oneImage = pygame.image.load('graphics/One.png')
        self.twoImage = pygame.image.load('graphics/Two.png')
        self.threeImage = pygame.image.load('graphics/Three.png')
        self.fourImage = pygame.image.load('graphics/Four.png')
        self.fiveImage = pygame.image.load('graphics/Five.png')
        self.sixImage = pygame.image.load('graphics/Six.png')
        self.sevenImage = pygame.image.load('graphics/Seven.png')
        self.eightImage = pygame.image.load('graphics/Eight.png')
        self.nineImage = pygame.image.load('graphics/Nine.png')

        self.skipImage = pygame.image.load('graphics/Skip.png')
        self.reverseImage = pygame.image.load('graphics/Reverse.png')
        self.drawTwoImage = pygame.image.load('graphics/DrawTwo.png')
        self.drawFourImage = pygame.image.load('graphics/DrawFour.png')
        self.wildCardActionImage = pygame.image.load('graphics/WildAction.png')

        self.wildCardImage = pygame.image.load('graphics/WildCard.png')
        self.redCardImage = pygame.image.load('graphics/RedCard.png')
        self.greenCardImage = pygame.image.load('graphics/GreenCard.png')
        self.blueCardImage = pygame.image.load('graphics/BlueCard.png')
        self.yellowCardImage = pygame.image.load('graphics/YellowCard.png')

        self.purpleBorder = pygame.image.load('graphics/PurpleBorder.png')
        self.cardTopImage = pygame.image.load('graphics/CardTop.png')
        self.unoButtonImage = pygame.image.load('graphics/UnoButton.png')

        self.rightArrowImage = pygame.image.load('graphics/Arrow.png')
        self.leftArrowImage = pygame.transform.flip(self.rightArrowImage, True, False)
        self.rightArrowBorder = pygame.image.load('graphics/ArrowPurpleBorder.png')
        self.leftArrowBorder = pygame.transform.flip(self.rightArrowBorder, True, False)


    def getType(self, rank):
        match rank:
            case '0': 
                return self.zeroImage # ZERO = 0. So as we matching self, if self is zero, then viola, we give the image for zero.
            case '1':
                return self.oneImage # I apologize for this syntax, but it's how our ruff checker wants it.
            case '2':
                return self.twoImage
            case '3':
                return self.threeImage
            case '4':
                return self.fourImage
            case '5':
                return self.fiveImage
            case '6':
                return self.sixImage
            case '7':
                return self.sevenImage
            case '8':
                return self.eightImage
            case '9':
                return self.nineImage
            case 'Skip':
                return self.skipImage
            case 'Reverse':
                return self.reverseImage
            case 'Draw2':
                return self.drawTwoImage
            case 'Draw4':
                return self.drawFourImage
            case 'Wild':
                return self.wildCardActionImage
            case _: 
                return

    def getColor(self, color):
        match color:
            case 'RED': 
                return self.redCardImage
            case 'GREEN': 
                return self.greenCardImage
            case 'BLUE':
                return self.blueCardImage
            case 'YELLOW':
                return self.yellowCardImage
            case _: 
                return self.wildCardImage # If we don't get any of the above cases, we default to wild card black.
            
    def typingPrompt(self, prompt):
        inputText = ""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        inputText = inputText[:-1]
                    if event.key == pygame.K_RETURN:
                        return inputText
                    else:
                        if len(event.unicode) > 0 and 32 <= ord(event.unicode) <= 126: # This checks if the user input a letter we have in our font
                            inputText += event.unicode
            
            self.screen.fill((173, 216, 230))

            promptSurface = self.font.render(prompt, self.font, (0,0,0))
            self.screen.blit(promptSurface, (0, self.screenHeight/2-18))
                             
            textSurface = self.font.render(inputText, self.font, (0,0,0))
            self.screen.blit(textSurface, (0, self.screenHeight/2))
            
            pygame.display.flip()

    def textPopUp(self, prompts):
        self.screen.fill((173, 216, 230))

        currentPrompt = 0
        for prompt in prompts:
            newTextSurface = self.font.render(prompt, self.font, (0,0,0))
            self.screen.blit(newTextSurface, (0, currentPrompt*12))
            currentPrompt += 1
        exitButton = pygame.Surface((BAR_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        exitButton.blit(self.exitImage, (0,0))

        exitRectangle = exitButton.get_rect()
        exitRectangle.center = (self.screenWidth/2, self.screenHeight - CARD_HEIGHT/2)

        self.screen.blit(exitButton, exitRectangle)

        pygame.display.flip()

        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()

            for event in pygame.event.get(): # This is for external interactions, like movement or keys.
                if event.type == pygame.QUIT: # Or for quitting out of the window!
                    pygame.quit()
                    sys.exit()

            if exitRectangle.collidepoint(mousePos) and mouseButtons[0]:
                return




class Clickable:
    def __init__(self, width, height, clickedObject, hoverTexture, pygameWrapper):
        self.width = width
        self.height = height
        self.clickedObject = clickedObject
        self.pygameWrapper = pygameWrapper
        self.clicked = False

        self.hoverTexture = hoverTexture
        self.canHover = True
        
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

    def displayAtCoords(self, x, y): # If you want to easily set coordinates as you blit
        if x is None:
            x = self.rectangle.centerx
        if y is None:
            y = self.rectangle.centery

        self.rectangle.center = (x, y)
        self.display()

    def isHovered(self, mousePos):
        if self.rectangle.collidepoint(mousePos) and self.canHover is True: # Check if the mouse is over the rectangle
            if self.hoverTexture is not None: 
                self.image.blit(self.hoverTexture, (0,0))
            return True
        else:
            self.resetImage() # If it's not being hovered over, we reset it removing the hoverTexture
            return False
        
    def isClicked(self, mouseButtons, mousePos):
        # Return if the clickable is hovered, and the mouse has clicked mouse1.
        return (self.isHovered(mousePos) and mouseButtons[0])
    


# All you need to know from this menu object, is that you call Menu.mainMenu, and that eventually outputs a valid list of players.
# Thus, this is a blackbox that just handles user input for how many players they want.
class Menu:
    def __init__(self, pygameWrapper):
        self.pygameWrapper = pygameWrapper
        self.clickCooldown = False

        self.logo = Clickable(CARD_HEIGHT * 3, CARD_HEIGHT * 2, None, None, self.pygameWrapper)
        self.logo.addGraphic(self.pygameWrapper.logoImage)

        self.startNewGame = Clickable(BAR_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.startNewGame.addGraphic(self.pygameWrapper.newGameImage)

        self.settingsButton = Clickable(BAR_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.settingsButton.addGraphic(self.pygameWrapper.settingsImage)

        self.exitButton = Clickable(BAR_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.exitButton.addGraphic(self.pygameWrapper.exitImage)

        self.backButton = Clickable(CARD_HEIGHT, CARD_HEIGHT, None, self.pygameWrapper.leftArrowBorder, self.pygameWrapper)
        self.backButton.addGraphic(self.pygameWrapper.leftArrowImage)

        self.resolutionButton = Clickable(BAR_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.resolutionButton.addGraphic(self.pygameWrapper.resolutionImage)

        self.fullscreenButton = Clickable(BAR_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.fullscreenButton.addGraphic(self.pygameWrapper.fullscreenImage)


        self.playerChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.playerChoice.addGraphic(self.pygameWrapper.playerChoiceImage)

        self.robotChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.robotChoice.addGraphic(self.pygameWrapper.robotChoiceImage)

        self.resetChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.resetChoice.addGraphic(self.pygameWrapper.resetChoiceImage)

        self.players = []
        for i in range(10):
            playerClickable = Clickable(CARD_WIDTH, CARD_HEIGHT, None, self.pygameWrapper.purpleBorder, self.pygameWrapper)
            playerClickable.addGraphic(self.pygameWrapper.wildCardImage)
            self.players.append(playerClickable)


    def turnOffClickCooldown(self):
        self.clickCooldown = False

    def turnOnClickCooldown(self):
        self.clickCooldown = True
              
        threading.Timer(0.5, self.turnOffClickCooldown).start()


    def newGamePrompts(self):
        returnValue = []
        currentPlayer = 1
        for player in self.players:
            prompt = f"Type player {currentPlayer}'s name. Press enter to continue"
            if player.clickedObject == "AI":
                name = self.pygameWrapper.typingPrompt(prompt)
                newComputerPlayer = ComputerPlayer(name)
                returnValue.append(newComputerPlayer)
            elif player.clickedObject == "Player":
                name = self.pygameWrapper.typingPrompt(prompt)
                newPlayer = Player(name)
                returnValue.append(newPlayer)
            
            if player.clickedObject is not None:
                currentPlayer += 1

        playerNum = len(returnValue)
        prompt = f"You have {playerNum} players. Please enter the player who should be the dealer: "
        chosenPlayer = self.pygameWrapper.typingPrompt(prompt)
        while not chosenPlayer.isdigit() or int(chosenPlayer) > playerNum or int(chosenPlayer) < 1:
            prompt = f"That was not a correct value! Please choose a dealer between 1 and {playerNum}: "
            chosenPlayer = self.pygameWrapper.typingPrompt(prompt)
        
        returnValue[int(chosenPlayer) - 1].isDealer = True

        return returnValue
        
    def newGameMenu(self):
        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()
            selected = None

            self.pygameWrapper.screen.fill((173, 216, 230))

            for event in pygame.event.get(): # This is for external interactions, like movement or keys.
                if event.type == pygame.QUIT: # Or for quitting out of the window!
                    pygame.quit()
                    sys.exit()

            self.startNewGame.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/10)

            self.resetChoice.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 2)
            self.playerChoice.displayAtCoords(self.pygameWrapper.screenWidth/2 * 1.5, self.pygameWrapper.screenHeight/5 * 2)
            self.robotChoice.displayAtCoords(self.pygameWrapper.screenWidth/2 * 0.5, self.pygameWrapper.screenHeight/5 * 2)
            self.backButton.displayAtCoords(CARD_HEIGHT/2, self.pygameWrapper.screenHeight - CARD_HEIGHT/2)

            currentPlayer = 0
            for player in self.players:
                if not player.clicked:
                    player.displayAtCoords((currentPlayer) * 64 + 32, self.pygameWrapper.screenHeight - (CARD_HEIGHT * 1.5))
                else:
                    player.display()
                currentPlayer += 1

            pygame.display.flip()


            if self.backButton.isClicked(mouseButtons, mousePos):
                self.turnOnClickCooldown()
                return -1

            for player in self.players:
                if player.isClicked(mouseButtons, mousePos) and selected is None: # This is drag and drop, and not selection.
                    selected = player
                    player.clicked = True
                    player.rectangle.center = mousePos
                # This elif is to give it another change to keep following if the mouse moves too fast.
                elif player.isClicked(mouseButtons, mousePos) and selected is None: 
                    player.rectangle.center = mousePos
                    selected = player
                else:
                    player.clicked = False # This is so it's drag and drop, and not selection. Otherwise, it'd be very awkward!

            if self.playerChoice.isClicked(mouseButtons, mousePos) and selected is not None:
                selected.graphics = []
                selected.addGraphic(self.pygameWrapper.wildCardImage)
                selected.addGraphic(self.pygameWrapper.playerImage)
                selected.clickedObject = "Player"
            
            if self.robotChoice.isClicked(mouseButtons, mousePos) and selected is not None:
                selected.graphics = []
                selected.addGraphic(self.pygameWrapper.wildCardImage)
                selected.addGraphic(self.pygameWrapper.robotImage)
                selected.clickedObject = "AI"
                
            if self.resetChoice.isClicked(mouseButtons, mousePos) and selected is not None:
                selected.graphics = []
                selected.addGraphic(self.pygameWrapper.wildCardImage)
                selected.clickedObject = None

            if self.startNewGame.isClicked(mouseButtons, mousePos):
                returnValue = self.newGamePrompts()
                return returnValue
    

    def settingsMenu(self):
        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()

            self.pygameWrapper.screen.fill((173, 216, 230))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.resolutionButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/10)
            self.fullscreenButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/3)
            self.backButton.displayAtCoords(CARD_HEIGHT/2, self.pygameWrapper.screenHeight - CARD_HEIGHT/2)

            pygame.display.flip()

            if self.resolutionButton.isClicked(mouseButtons, mousePos): 
                newWidth = self.pygameWrapper.typingPrompt("Please choose your new screen width: ")
                while not newWidth.isdigit() or int(newWidth) < MIN_SCREEN_WIDTH:
                    prompt = f"The minimum screen width is {MIN_SCREEN_WIDTH}! Please enter a valid screen width: "
                    newWidth = self.pygameWrapper.typingPrompt(prompt)
                newHeight = self.pygameWrapper.typingPrompt("Please choose your new screen height: ")
                while not newHeight.isdigit() or int(newHeight) < MIN_SCREEN_HEIGHT:
                    prompt = f"The minimum screen height is {MIN_SCREEN_HEIGHT}! Please enter a valid screen height: "
                    newHeight = self.pygameWrapper.typingPrompt(prompt)
                
                self.pygameWrapper.screenWidth = int(newWidth)
                self.pygameWrapper.screenHeight = int(newHeight)
                self.pygameWrapper.screen = pygame.display.set_mode((self.pygameWrapper.screenWidth, self.pygameWrapper.screenHeight))
            

            if self.fullscreenButton.isClicked(mouseButtons, mousePos) and self.clickCooldown is False: 
                if self.pygameWrapper.fullscreen is not True:
                    self.pygameWrapper.fullscreen = True                   
                    self.pygameWrapper.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

                    self.pygameWrapper.lastWidth = self.pygameWrapper.screenWidth
                    self.pygameWrapper.lastHeight = self.pygameWrapper.screenHeight

                    screenInfo = pygame.display.Info()
                    self.pygameWrapper.screenWidth = screenInfo.current_w
                    self.pygameWrapper.screenHeight = screenInfo.current_h

                else:
                    self.pygameWrapper.fullscreen = False
                    self.pygameWrapper.screenWidth = self.pygameWrapper.lastWidth
                    self.pygameWrapper.screenHeight = self.pygameWrapper.lastHeight

                    self.pygameWrapper.screen = pygame.display.set_mode((self.pygameWrapper.screenWidth, self.pygameWrapper.screenHeight))
                
                self.turnOnClickCooldown()
            
            if self.backButton.isClicked(mouseButtons, mousePos):
                self.turnOnClickCooldown()
                return

    def mainMenu(self):
        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()

            self.pygameWrapper.screen.fill((173, 216, 230))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.logo.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5)
            self.startNewGame.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 2.5)
            self.settingsButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 3.5)
            self.exitButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 4.5)

            pygame.display.flip() # This actually updates the display

            if self.startNewGame.isClicked(mouseButtons, mousePos): 
                returnValue = self.newGameMenu()
                if returnValue != -1:
                    return returnValue
            
            if self.settingsButton.isClicked(mouseButtons, mousePos): 
                self.settingsMenu()
            
            if self.exitButton.isClicked(mouseButtons, mousePos) and self.clickCooldown is False:
                pygame.quit()
                sys.exit()





# When you call UserInterface.interfaceUser, it'll either return one of these values or the card they want to play to the discardpile.
userReturnType = {0:"uno clicked", 1: "draw card"}
        
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

        self.rightArrow = Clickable(CARD_HEIGHT, CARD_HEIGHT, None, self.pygameWrapper.rightArrowBorder, self.pygameWrapper)
        self.rightArrow.addGraphic(self.pygameWrapper.rightArrowImage)

        self.leftArrow = Clickable(CARD_HEIGHT, CARD_HEIGHT, None, self.pygameWrapper.leftArrowBorder, self.pygameWrapper)
        self.leftArrow.addGraphic(self.pygameWrapper.leftArrowImage)

        self.unoButton = Clickable(CARD_HEIGHT, CARD_WIDTH, None, None, self.pygameWrapper)
        self.unoButton.addGraphic(self.pygameWrapper.unoButtonImage)
        
        # This card stuff is neded to render the players cards
        self.firstCard = 0
        self.lastCard = 0
        self.cards = []

    def turnOffClickCooldown(self):
        self.clickCooldown = False

        # This canHover logic might not be pretty, but it allows us to give feedback to the user that they cannot use the Clickable.
        self.rightArrow.canHover = True
        self.leftArrow.canHover = True

    def turnOnClickCooldown(self):
        self.clickCooldown = True
        
        self.rightArrow.canHover = False
        self.leftArrow.canHover = False
              
        threading.Timer(0.5, self.turnOffClickCooldown).start()

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

    def renderTurn(self):
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
                    pygame.quit()
                    sys.exit()

            mouseButtons = pygame.mouse.get_pressed()

            # This sets a nice light blue background. We do this each frame to basically reset the screen.
            self.pygameWrapper.screen.fill((173, 216, 230))
            self.renderTurn()
            pygame.display.flip() # This actually updates the display

            # Yes, we do just go over all clickables and check O(n) for if they're selected. 
            # This is fine! We don't have enough to care. More sophisticated mouse tracking would be a lot of unnecessary work. 
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

            # This 'and not self.clickCooldown' logic isn't pretty, but we need it due to isClicked logic.
            if self.leftArrow.isClicked(mouseButtons, mousePos) and not self.clickCooldown: 
                self.firstCard -= int((self.pygameWrapper.screenWidth/64) - 2)
                if self.firstCard < 0: 
                    self.firstCard = 0
                self.updateLastCard(player)
                self.turnOnClickCooldown()

            if self.rightArrow.isClicked(mouseButtons, mousePos) and not self.clickCooldown:
                self.firstCard += int((self.pygameWrapper.screenWidth/64) - 2)
                if self.firstCard >= len(self.cards): 
                    self.firstCard = len(self.cards) - 1
                self.updateLastCard(player)
                self.turnOnClickCooldown()

            if self.unoButton.isClicked(mouseButtons, mousePos) and not self.clickCooldown: 
                return 0
            
            if self.drawClick.isClicked(mouseButtons, mousePos) and not self.clickCooldown: 
                return 1
            
            if self.discardClick.isClicked(mouseButtons, mousePos) and selected is not None:
                return selected.clickedObject
            
    def showOtherTurn(self, player, card = None):
        prompts = []
        if card is not None:
            if card.rank != "Draw4" and card.rank != "Wild":
                prompts.append(f"{player.name} played a {card.color} {card.rank} card")
            else:
                prompts.append(f"{player.name} played a {card.rank} card")
        else:
            prompts.append(f"{player.name} drew a card")
        prompts.append(f"{player.name} now has {len(player.hand.cards)} cards")


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
    testCard = RyanCard("GREEN", '3')
    player.hand.addCard(testCard)
blueCard = RyanCard("Wild", 'Wild')
yellowCard = RyanCard("Draw4", 'Draw4')
redCard = RyanCard("RED", 'Draw2')
player.hand.addCard(yellowCard)
player.hand.addCard(redCard)
player.hand.addCard(blueCard)

pygameWrapper = PygameWrapper(800, 600)
discardPile = DiscardPile()
discardPile.addCard(RyanCard("RED", '7'))
drawPile = DrawPile(None)
userInterface = UserInterface(pygameWrapper, discardPile, drawPile)

menu = Menu(pygameWrapper)
players = menu.mainMenu()

for player in players:
    print(player.name)

running = True
while running:
    userInput = userInterface.interfaceUser(player)
    if isinstance(userInput, RyanCard):
        print("We played a card!")
    else:
        match userInput:
            case 0:
                print("Uno pressed!")
            case 1:
                print("Draw pressed!")
pygame.quit()
"""