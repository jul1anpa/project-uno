''' user_interface.py: a TLDR Developer Guide
This file handles the interfacing the user's actions in UNO through Pygame.
    
To use, first make a PygameWrapper object with a starting screen height and width within 640x360.
Only make one PygameWrapper! it handles all Pygame logic, which could overlap with over PygameWrappers.
The PygameWrapper is used mainly for passing to other objects to use for Pygame logic. 
However it also has it's own methods you can use! These methods are:
    .typingPrompt, which takes a string, and then asks the user to type an answer in ASCII. It then returns the typed answer.
    .textPopUp, which takes a list of strings to show the user. The user then clicks a button to exit.
With those methods, PygameWrapper is very flexible: you can prompt anything, and display anything (if you can make ASCII art, that is)

Of particular note: we do not have a method of showing a turn that the A.I has played!
I cannot make a method, since it requires knowing the order of what the A.I did (E.G. drawing, and then playing a card). 
Thus, to show what the A.I did, make append strings on a list passed to PygameWrapper.textPopUp so it can describe what happened


We then have two main objects that PygameWrapper is used for, and can handle everything UNO wants: Menu, and UserInterface.


The Menu object only requires the PygameWrapper, and can then be used to handle the main menu.
This is done via the .mainMenu method, which creates a main menu which in turn calls all of Menu's other methods.
This .mainMenu method is guaranteed to return a list of players, either A.I or Human, with names and with one as the dealer.

You can also use some of Menu's methods manually. Do note they expect to be able to return to another menu. These list:
    .newGameMenu, which prompts for a new game, returning a list of players. However, it can also return -1, leaving the menu.
    .settingsMenu, which prompts for screen changes either manual, or full screen. It only returns nothing, leaving the menu.


The UserInterface object requires a PygameWrapper, DiscardPile, and DrawPile, which handles what the interface a user has each turn.
This is done via the .interfaceUser method which returns either 0 for calling UNO, 1 for drawing a card, or a card they wish to play.
.interfaceUser expects to be properly handled, as the card wished to play could be invalid, and UNO does not end the turn.
Thus, you must call .interfaceUser if their turn is not over after .interfaceUser returns a value.

You will also need UserInterface's other methods for other turn handling, like color choices, and drawing card logic. 
These are:
    .promptPlayCard, which takes a card, and asks the player to play it or not, returning true or false. 
        .promptPlayCard should be used after a player draws a card and this card is valid to be played.

    .chooseColor, which prompts the user to choose one of four colors, returning a string representing them.
        .chooseColor should be used to chose a color after playing a wildCard, or to challenge a wildDraw4.


        
And thats about everything you need to know to use user_interface.py!
To TLDR even further:
    Make a PygameWrapper(screenHeight > 640, screenWidth > 360)
    Then do var = Menu(PygameWrapper), var.mainMenu() = players[], using players[] as a list of players for a game of UNO
    Then do var1 = UserInterface(PygameWrapper, DiscardPile, DrawPile), var1.interfaceUser(player) = returnCode

    With that returnCode, handle game logic,
    returnCode == 0: called uno so player.callUNO, and to continue turn var1.interfaceUser(player)
    returnCode == 1: drew card, player.drawCard(drawPile), 
        If newley drawn card playable, var1.promptPlayCard(newCard), and if true, player.playCard(discardPile, newCard)
    type(returnCode) == Card:
        if returnCode is playable, player.playCard(discardPile, returnCode)
        else, continue turn, var1.interfaceUser(player)
    
    Then, after any A.I turn, PygameWrapper.textPopUp(list of strings describing the A.I's turn)
'''



import pygame
import threading # This is just for cooldowns on clicking!
import sys # For force shutdown if the user clicks the windows close button.

from objects import ComputerPlayer, Player

CARD_WIDTH = 48 # Cards are 48 pixels wide
CARD_HEIGHT = 72 # Cards are 72 pixels high
BAR_WIDTH = 512 # Menu bars are 512 pixels wide, and 72 high.

# Minimum resolution is 360p! Needed since there's a lot of pixel logic, and any lower some screens could break.
MIN_SCREEN_WIDTH = 640
MIN_SCREEN_HEIGHT = 360



''' PygameWrapper
    This class is used to initialize, and then handle all pygame stuff. You should only have one PygameWrapper class!
    The screen that pygame window renders is thus PygameWrapper.screen, and so is just about every pygame variable.
    
    It also has some general pygame methods:
        .getType and .getColor to retrieve the proper textures for a cards type and color
        .typingPrompt to allow a simple console like prompt, and user input via typing
        .textPopUp to display a list of strings on the screen.
'''
class PygameWrapper:

    ''' __init__
        PygameWrappers init takes a width and height to make the pygame window. 
        It then loads every single texture we ever use; definitely questionable logic, but good enough!
    '''
    def __init__(self, screenWidth, screenHeight):
        # We cannot allow width or height to be above the minimum 360p
        if screenWidth < MIN_SCREEN_WIDTH:
            self.screenWidth = MIN_SCREEN_WIDTH
        else:
            self.screenWidth = screenWidth
            self.lastWidth = screenWidth # lastWidth and lastHeight are embarresingly only used for fullscreen logic. Oh well!
        
        if screenHeight < MIN_SCREEN_HEIGHT:
            self.screenHeight = MIN_SCREEN_HEIGHT
            self.lastHeight = screenHeight
        else:
            self.screenHeight = screenHeight

        # Initialize general pygame stuff
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        pygame.display.set_caption("UNO")
        self.fullscreen = False

        pygame.font.init()
        # This is the font we use to render graphics. 
        # It's this old one just because I like ASCII games, and grabbing from a users system files sounds scary.
        self.font = pygame.font.Font('graphics/Perfect DOS VGA 437.ttf', 12)


        # All the graphics!!!

        # General Menu graphics
        self.logoImage = pygame.image.load('graphics/Logo.png')
        self.newGameImage = pygame.image.load('graphics/NewGame.png')
        self.settingsImage = pygame.image.load('graphics/Settings.png')
        self.exitImage = pygame.image.load('graphics/Exit.png')
        self.resolutionImage = pygame.image.load('graphics/Resolution.png')
        self.fullscreenImage = pygame.image.load('graphics/Fullscreen.png')
        self.yesImage = pygame.image.load('graphics/YES.png')
        self.noImage = pygame.image.load('graphics/NO.png')
        self.playCardImage = pygame.image.load('graphics/PlayCardPrompt.png')

        # New Game menu dragables
        self.playerChoiceImage = pygame.image.load('graphics/PlayerChoice.png')
        self.robotChoiceImage = pygame.image.load('graphics/RobotChoice.png')
        self.resetChoiceImage = pygame.image.load('graphics/ResetChoice.png')

        # New Game menu types
        self.playerImage = pygame.image.load('graphics/Player.png')
        self.robotImage = pygame.image.load('graphics/Robot.png')

        # UNO card numbers
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

        # UNO action cards 
        self.skipImage = pygame.image.load('graphics/Skip.png')
        self.reverseImage = pygame.image.load('graphics/Reverse.png')
        self.drawTwoImage = pygame.image.load('graphics/DrawTwo.png')
        self.drawFourImage = pygame.image.load('graphics/DrawFour.png')
        self.wildCardActionImage = pygame.image.load('graphics/WildAction.png')

        # UNO card colors
        self.wildCardImage = pygame.image.load('graphics/WildCard.png')
        self.redCardImage = pygame.image.load('graphics/RedCard.png')
        self.greenCardImage = pygame.image.load('graphics/GreenCard.png')
        self.blueCardImage = pygame.image.load('graphics/BlueCard.png')
        self.yellowCardImage = pygame.image.load('graphics/YellowCard.png')

        # Miscellanious UNO stuff
        self.purpleBorder = pygame.image.load('graphics/PurpleBorder.png') # Border for a card
        self.cardTopImage = pygame.image.load('graphics/CardTop.png') # Top of a card (used for face down cards, E.G. a deck)
        self.unoButtonImage = pygame.image.load('graphics/UnoButton.png') # Used to call UNO

        # Arrows
        self.rightArrowImage = pygame.image.load('graphics/Arrow.png') 
        self.leftArrowImage = pygame.transform.flip(self.rightArrowImage, True, False) # This flips the arrow.
        self.rightArrowBorder = pygame.image.load('graphics/ArrowPurpleBorder.png') # Purple border for an arrow.
        self.leftArrowBorder = pygame.transform.flip(self.rightArrowBorder, True, False)


    ''' getType
        All this does it take a card's rank value, and returns the equivalent texture.
    '''
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
                return # I think in the corner case, we technically can have no rank? In any case, this intuitively feels useful.


    ''' getColor
        All this does it take a card's color value, and returns the equivalent texture.
    '''
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
                # If we don't get any of the above cases, we default to wild card black.
                # Unlike getType, this corner case does return a value, since a card needs a background to be properly rendered.
                return self.wildCardImage


    ''' typingPrompt
        This takes a string, and then makes the user type a string. After typing, it returns the new string
    '''
    def typingPrompt(self, prompt):
        inputText = ""
        while True:
            
            # This is how we get keys from pygame! 
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collector!

                # After grabbing events, we must divide them, or else we get a huge stinkin' if chain.
                # Though, I don't think it matters in this program...
                if event.type == pygame.KEYDOWN: # This detects if its a key
                    
                    if event.key == pygame.K_BACKSPACE:
                        inputText = inputText[:-1] # If it's backspace, we remove the last part of the typed string

                    if event.key == pygame.K_RETURN:
                        return inputText # If it's enter / return, we are done here!
                    
                    else:
                        # Otherwise, we check if it's a valid letter in our font.
                        if len(event.unicode) > 0 and 32 <= ord(event.unicode) <= 126: # We're using ASCII!
                            inputText += event.unicode # If so, we add it.
            
            self.screen.fill((173, 216, 230)) # Reset the screen to a light blue

            promptSurface = self.font.render(prompt, self.font, (0,0,0)) # Render the prompt
            self.screen.blit(promptSurface, (0, self.screenHeight/2-18)) # We put this just a bit above the middle
                             
            textSurface = self.font.render(inputText, self.font, (0,0,0)) # Render the currently typed text
            self.screen.blit(textSurface, (0, self.screenHeight/2)) # We put this in the middle
            
            pygame.display.flip() # Shows the frame we've rendered.
    

    ''' textPopUp
        This takes a list of strings, and renders them all on screen. 
    '''
    def textPopUp(self, prompts):
        self.screen.fill((173, 216, 230)) # We first set the color to a light blue

        currentPrompt = 0 # Used for currentPrompt*12 to place each prompt below the last
        for prompt in prompts:
            newTextSurface = self.font.render(prompt, self.font, (0,0,0)) # Render the prompt
            self.screen.blit(newTextSurface, (0, currentPrompt*12)) # Place the prompt in it's place
            currentPrompt += 1

        # This is makes a manual bounding box for an exit button the user clicks to leave the prompt.
        exitButton = pygame.Surface((BAR_WIDTH, CARD_HEIGHT), pygame.SRCALPHA) # Creates the surface to render the texture on
        exitButton.blit(self.exitImage, (0,0)) # Renders the texture onto the surface
        exitRectangle = exitButton.get_rect() # Now we make a rectangle that the surface is actually on
        exitRectangle.center = (self.screenWidth/2, self.screenHeight - CARD_HEIGHT/2) # We put this rectangle at the bottom of the screen

        self.screen.blit(exitButton, exitRectangle) # This finally renders the exit button in its place.

        pygame.display.flip() # We now finally render everything to the screen. This doesn't need to update each frame, so it doesn't.

        while True:
            mousePos = pygame.mouse.get_pos() # Gets the mouse's coordinates
            mouseButtons = pygame.mouse.get_pressed() # Checks the mouse's buttons

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collector!

            # This checks if the mouse is currently over the exit button, and if mouse 1 button has been clicked.
            if exitRectangle.collidepoint(mousePos) and mouseButtons[0]:
                return # If so, we're done here!



''' Clickable
    This is the backbone of my pygame logic, which handles the horrible logic I did manually in textPopUp for buttons and the like.
    It allows us to just make a rectangle, the textures the rectangle has, and easily check if we're hovering or clicking over it.
    Another feature, though not used as much, is clickedObject, allowing our clickable to directly represent an actual object.
'''
class Clickable:
    ''' __init__
        Clickable's init takes a width, height, clickedObject, hoverTexture, and pygameWrapper.
        They do self explanitory things: defining the clickables size, an object the clickable wraps around, a texture shown when hovered and pygame stuff.
        After setting up those things, it then sets up the needed pygame stuff for a rectangle you could click.
    '''
    def __init__(self, width, height, clickedObject, hoverTexture, pygameWrapper):
        self.width = width
        self.height = height
        self.clickedObject = clickedObject
        self.pygameWrapper = pygameWrapper

        # This detects if it is currently being clicked.
        # It's only used externally, to follow if the object is the one we're clicking. Mainly, for drag and drop logic.
        self.clicked = False

        self.hoverTexture = hoverTexture # A texture used when we're hovering over the object
        self.canHover = True # 
        
        # This defines the base surface of the card which we then layer any graphics to
        # You will want to use Clickable.image.blit(graphics, (x, y)) to add a layer.
        # To refresh a clickable, you will want to reset it by running the below line again: self.image = pygame.Surface 
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.graphics = [] # This list is used for the graphics put onto the image in order: #2 is layered ontop of #1!
        
        # This is how we move the image around. You can set the position via card.rectangle.center(x, y) and a bunch of other functions like .move(x, y)
        # Then we can send it to be rendered via screen.blit(card.image, card.rectangle)
        self.rectangle = self.image.get_rect()


    ''' addGraphic
        This adds a graphic to the clickable, and is used when defining a clickables graphics.
        It simply appends it to our graphics list, and then renders it onto the clickable's current image.
    '''
    def addGraphic(self, graphic):
        self.graphics.append(graphic)
        self.image.blit(graphic, (0, 0)) # Renders the new graphic to the clickable's current image


    ''' resetImage
        This removes any graphics that we did not define inherently to the clickables graphics.
        This is mainly for the clickable's own hover texture, 
        But it was also once used when playing around with it for menu stuff!!! Though, that didn't come to fruition
    '''
    def resetImage(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # Reset the clickable's current image / surface
        for graphic in self.graphics:
            self.image.blit(graphic, (0, 0)) # Render all the textures to the surface


    ''' display:
        Kind of a silly function, but this logic was waaay too clickable centric to do manually over and over.
    '''
    def display(self): 
        self.pygameWrapper.screen.blit(self.image, self.rectangle) # This just adds the card to the current screen. You will have to do screen.flip() to show it. 

    ''' displayAtCoords:
        Takes an x and y value to then display the clickable at.
        Since the logic is encapsulated in clickables, this gets to be the center of the clickable instead of pygames SDL2 top left!
    '''
    def displayAtCoords(self, x, y): # If you want to easily set coordinates as you blit
        if x is None:
            x = self.rectangle.centerx
        if y is None:
            y = self.rectangle.centery

        self.rectangle.center = (x, y) # The rectangle is used as the render point in self.display()
        self.display()


    ''' isHovered
        Takes a mouse position (an X and Y tuple), and checks if it's inside of the clickable.
    '''
    def isHovered(self, mousePos):
        if self.rectangle.collidepoint(mousePos) and self.canHover is True: # Check if the mousePos is over the rectangle
            if self.hoverTexture is not None: 
                self.image.blit(self.hoverTexture, (0,0)) # If it is, then it's hovered, and we show that with a hoverTexture
            return True
        else:
            # If it's not being hovered over, we remove a hoverTexture removing the hoverTexture
            # Very inefficient, but you may be suprised how much that does not matter at all.
            self.resetImage()
            return False
    

    ''' isClicked
        Takes mouseButtons from pygame, and a mouse position (an X and Y tuple), 
        With this, it checks if the clickable is hovered over, and the mouseButton's mouse 1 is down.
    '''
    def isClicked(self, mouseButtons, mousePos):
        # Return if the clickable is hovered, and the mouse has clicked mouse1.
        return (mouseButtons[0] and self.isHovered(mousePos))
    


''' Menu
    This class takes a pygameWrapper, and then handles all of the main menu stuff.
    It's main use is it's .mainMenu method for a main menu, which then returns a valid list of players for a new game.
    Other than that... Not much. 
'''
class Menu:
    ''' __init__
        Menu's init takes a pygamewrapper. Then, it sets up most of the clickables Menu uses. 
        Some clickables of particular note is a list of "player" clickables we turn into real players later.
    '''
    def __init__(self, pygameWrapper):
        self.pygameWrapper = pygameWrapper

        # This is used so that you don't click some buttons multiple times a frame.
        # Of particular note, is the escape / back buttons, and the full screen button.
        self.clickCooldown = False 

        # literally just the logo we show at the top of the main menu. It's a clickable, but you can never actually click it!
        self.logo = Clickable(CARD_HEIGHT * 3, CARD_HEIGHT * 2, None, None, self.pygameWrapper)
        self.logo.addGraphic(self.pygameWrapper.logoImage)

        # General buttons
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


        self.players = []
        for i in range(10): # These players are essentially cards that you can later see in the UserInterface object
            playerClickable = Clickable(CARD_WIDTH, CARD_HEIGHT, None, self.pygameWrapper.purpleBorder, self.pygameWrapper)
            playerClickable.addGraphic(self.pygameWrapper.wildCardImage)
            self.players.append(playerClickable)

        # "Decks" / "Dragables" we use in .newGameMenu
        # Not necessarily for clicking, but rather, dragging players to.
        self.playerChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.playerChoice.addGraphic(self.pygameWrapper.playerChoiceImage)

        self.robotChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.robotChoice.addGraphic(self.pygameWrapper.robotChoiceImage)

        self.resetChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        self.resetChoice.addGraphic(self.pygameWrapper.resetChoiceImage)


    ''' turnOffClickCooldown
        This handles the turning off of clickCooldown! It's called as a thread after turning the cooldown on, so it'll turn off.
    '''
    def turnOffClickCooldown(self):
        self.clickCooldown = False


    ''' turnOnClickCooldown
        This is how we handle the turning on of clickCooldown! Oh, and the logic of making sure it turns off eventually.
    '''
    def turnOnClickCooldown(self):
        self.clickCooldown = True
        
        # We just make a thread that waits 0.5 seconds to turnOffClickCooldown
        threading.Timer(0.5, self.turnOffClickCooldown).start()

    
    ''' newGamePrompts
        This handles the specifics of a new game, asking for the name of each player, and who the dealer is.
    '''
    def newGamePrompts(self):
        returnValue = [] # The list of players we will return

        currentPlayer = 1
        for player in self.players:
            prompt = f"Type player {currentPlayer}'s name. Press enter to continue"
            if player.clickedObject == "AI":
                # If the player is an AI, we prompt and use the name for a computer player
                name = self.pygameWrapper.typingPrompt(prompt)
                newComputerPlayer = ComputerPlayer(name)
                returnValue.append(newComputerPlayer)

            elif player.clickedObject == "Player":
                # If the player is a Player... Well, y'know, like a user, then we prompt and use the name for a player object... Get it?
                name = self.pygameWrapper.typingPrompt(prompt)
                newPlayer = Player(name)
                returnValue.append(newPlayer)
            
            if player.clickedObject is not None:
                currentPlayer += 1 # If the player was something we actually prompted for, then we add one and go to the next player.

        playerNum = len(returnValue)
        prompt = f"You have {playerNum} players. Please enter the player who should be the dealer: "
        chosenPlayer = self.pygameWrapper.typingPrompt(prompt) # Choose a player to be a dealer!

        # If that's not a valid player, keep going until you chose a valid player!
        while not chosenPlayer.isdigit() or int(chosenPlayer) > playerNum or int(chosenPlayer) < 1:
            prompt = f"That was not a correct value! Please choose a dealer between 1 and {playerNum}: "
            chosenPlayer = self.pygameWrapper.typingPrompt(prompt)
        
        # Make the selected player the dealer.
        returnValue[int(chosenPlayer) - 1].isDealer = True

        return returnValue
    

    ''' newGameMenu
        This handles the selection of players: are they A.I, or a hotseat user?
    '''
    def newGameMenu(self):
        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()
            selected = None

            self.pygameWrapper.screen.fill((173, 216, 230)) # Reset the screen to blue

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collect

            # We show the start new game button at the top, but not directly at the top
            self.startNewGame.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/10)

            # The three choices in the middle: player, robot, or none.
            self.resetChoice.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 2)
            self.playerChoice.displayAtCoords(self.pygameWrapper.screenWidth/2 * 1.5, self.pygameWrapper.screenHeight/5 * 2)
            self.robotChoice.displayAtCoords(self.pygameWrapper.screenWidth/2 * 0.5, self.pygameWrapper.screenHeight/5 * 2)

            # And a back button at the bottom left.
            self.backButton.displayAtCoords(CARD_HEIGHT/2, self.pygameWrapper.screenHeight - CARD_HEIGHT/2)

            currentPlayer = 0
            for player in self.players: # We go through all of our clickable players
                if not player.clicked: # If they aren't currently being clicked, we display them where they should be
                    player.displayAtCoords((currentPlayer) * 64 + 32, self.pygameWrapper.screenHeight - (CARD_HEIGHT * 1.5))
                else: # But if they are clicked, as in, being drag and dropped, then we display them where they currently are.
                    player.display()
                currentPlayer += 1

            pygame.display.flip() # Update the displays render!


            if self.backButton.isClicked(mouseButtons, mousePos): # If we click the bottom left back button, leave
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

            # If we have something selected (a player) and then we also hover over / click playerChoice, then we make the player a player
            if self.playerChoice.isClicked(mouseButtons, mousePos) and selected is not None:
                selected.graphics = []
                selected.addGraphic(self.pygameWrapper.wildCardImage)
                selected.addGraphic(self.pygameWrapper.playerImage)
                selected.clickedObject = "Player"
            
            # If we have something selected (a player) and then we also hover over / click playerChoice, then we make the player a !ROBOT!            
            if self.robotChoice.isClicked(mouseButtons, mousePos) and selected is not None:
                selected.graphics = []
                selected.addGraphic(self.pygameWrapper.wildCardImage)
                selected.addGraphic(self.pygameWrapper.robotImage)
                selected.clickedObject = "AI"
            
            # If we have something selected (a player) and then we also hover over / click playerChoice, then we make the player... Nothin'
            if self.resetChoice.isClicked(mouseButtons, mousePos) and selected is not None:
                selected.graphics = []
                selected.addGraphic(self.pygameWrapper.wildCardImage)
                selected.clickedObject = None

            # This starts a new game, by prompting for player info, and returning the now complete list of players.
            if self.startNewGame.isClicked(mouseButtons, mousePos):
                returnValue = self.newGamePrompts()
                return returnValue
    

    ''' settingsMenu
        This handles the changing of settings! Mainly, just resolution.
        You can change the resolution manually, or you can toggle fullscreen.
    '''
    def settingsMenu(self):
        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()

            self.pygameWrapper.screen.fill((173, 216, 230))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collect

            # Display all the buttons
            self.resolutionButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/10)
            self.fullscreenButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/3)
            self.backButton.displayAtCoords(CARD_HEIGHT/2, self.pygameWrapper.screenHeight - CARD_HEIGHT/2)

            pygame.display.flip() # Render all the buttons

            # If the resolution button is clicked, we prompt for the new resolution
            if self.resolutionButton.isClicked(mouseButtons, mousePos): 
                
                # Enter a width
                newWidth = self.pygameWrapper.typingPrompt("Please choose your new screen width: ")
                while not newWidth.isdigit() or int(newWidth) < MIN_SCREEN_WIDTH: # Oh come on, not like that!
                    prompt = f"The minimum screen width is {MIN_SCREEN_WIDTH}! Please enter a valid screen width: "
                    newWidth = self.pygameWrapper.typingPrompt(prompt)

                # Enter a new height
                newHeight = self.pygameWrapper.typingPrompt("Please choose your new screen height: ")
                while not newHeight.isdigit() or int(newHeight) < MIN_SCREEN_HEIGHT: # Play nice!!!
                    prompt = f"The minimum screen height is {MIN_SCREEN_HEIGHT}! Please enter a valid screen height: "
                    newHeight = self.pygameWrapper.typingPrompt(prompt)
                
                # And now, we update for the resolution!
                self.pygameWrapper.screenWidth = int(newWidth)
                self.pygameWrapper.screenHeight = int(newHeight)
                self.pygameWrapper.screen = pygame.display.set_mode((self.pygameWrapper.screenWidth, self.pygameWrapper.screenHeight))
            
            # If the fullscreen Button is clicked, we make it fullscreen, or make it not fullscreen
            if self.fullscreenButton.isClicked(mouseButtons, mousePos) and self.clickCooldown is False: 
                if self.pygameWrapper.fullscreen is not True:
                    self.pygameWrapper.fullscreen = True # If it's not fullscreen, make it full screen!               
                    self.pygameWrapper.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

                    # Sve the old non-fullscreen size.
                    self.pygameWrapper.lastWidth = self.pygameWrapper.screenWidth
                    self.pygameWrapper.lastHeight = self.pygameWrapper.screenHeight
                    
                    # And add the new fullscreen size as the "official" size, since we often use it for formatting clickables.
                    screenInfo = pygame.display.Info()
                    self.pygameWrapper.screenWidth = screenInfo.current_w
                    self.pygameWrapper.screenHeight = screenInfo.current_h

                else: # If it's not-not fullscreen, then it must be fullscreen!
                    self.pygameWrapper.fullscreen = False # That means we should make it not fullscreen anymore.
                    self.pygameWrapper.screenWidth = self.pygameWrapper.lastWidth
                    self.pygameWrapper.screenHeight = self.pygameWrapper.lastHeight

                    self.pygameWrapper.screen = pygame.display.set_mode((self.pygameWrapper.screenWidth, self.pygameWrapper.screenHeight))
                
                # We turn on the cooldown since otherwise we spam fullscreen stuff, and an operating systems API really does not like that!!!
                # Trust me; personal experience.
                self.turnOnClickCooldown()
            
            if self.backButton.isClicked(mouseButtons, mousePos):
                self.turnOnClickCooldown() # If exit buttons been clicked, we exit.
                return
    

    ''' mainMenu
        The menu your supposed to call! 
        This gives the options to start a new game, change settings, or exit the program.
        Oh, and it also returns a list of players when a new game is made. Very important!
    '''
    def mainMenu(self):
        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()

            self.pygameWrapper.screen.fill((173, 216, 230)) # Classic good ole blue! 

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collect

            # Display all the buttons... And the logo.
            self.logo.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5)
            self.startNewGame.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 2.5)
            self.settingsButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 3.5)
            self.exitButton.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/5 * 4.5)

            pygame.display.flip() # This updates the display

            if self.startNewGame.isClicked(mouseButtons, mousePos): 
                returnValue = self.newGameMenu() # If the newGame is clicked, we go and do the stuff to make a new game!
                if returnValue != -1:
                    return returnValue # If that turns out not to be an exit value, we return the expected list of players.
            
            if self.settingsButton.isClicked(mouseButtons, mousePos): 
                self.settingsMenu() # If the settings button is clicked, we go to the settings menu!
            
            if self.exitButton.isClicked(mouseButtons, mousePos) and self.clickCooldown is False:
                pygame.quit() # If the exit button is clicked, we're out of here!!!
                sys.exit()



# When you call UserInterface.interfaceUser, it'll either return one of these values or the card they want to play to the discardpile.
# We don't actually use this userReturnType. But it's nice to have it here, as proof that's what the return values mean!
userReturnType = {0:"uno clicked", 1: "draw card"}

''' UserInterface
    Handles all that is needed to interface the user.
'''
class UserInterface:
    ''' __init__
        UserInterface's init takes a pygameWrapper, discardPile, and drawPile
        It then sets up all the clickables we want, as well as the underlying card viewing logic.
    '''
    def __init__(self, pygameWrapper, discardPile, drawPile):
        self.pygameWrapper = pygameWrapper
        
        self.currentUser = None # Later to be used for a player class.

        # This is used so that you don't click some buttons multiple times a frame.
        # Of particular note is the arrow keys.
        self.clickCooldown = False

        # Clickables!
        self.discardPile = discardPile # Discard pile clickable. Used for dragging and dropping cards onto it
        self.discardClick = Clickable(CARD_WIDTH, CARD_HEIGHT, discardPile, None, self.pygameWrapper)
        self.discardClick.addGraphic(self.pygameWrapper.getColor(self.discardPile.cards[-1].color)) # Uses its top cards graphics
        self.discardClick.addGraphic(self.pygameWrapper.getType(self.discardPile.cards[-1].rank))
        
        self.drawPile = drawPile # drawPile clickable! Honestly, there's no real reason for it having a drawPile object haha.
        self.drawClick = Clickable(CARD_WIDTH, CARD_HEIGHT, drawPile, None, self.pygameWrapper)
        self.drawClick.addGraphic(self.pygameWrapper.cardTopImage)

        # Uno button for calling uno!
        self.unoButton = Clickable(CARD_HEIGHT, CARD_WIDTH, None, None, self.pygameWrapper)
        self.unoButton.addGraphic(self.pygameWrapper.unoButtonImage)


        # The two arrows to go back and forth through your potentially incredibly large hand.
        # Both have borders, since it makes going through them nicer with the click cooldown
        self.rightArrow = Clickable(CARD_HEIGHT, CARD_HEIGHT, None, self.pygameWrapper.rightArrowBorder, self.pygameWrapper)
        self.rightArrow.addGraphic(self.pygameWrapper.rightArrowImage) 

        self.leftArrow = Clickable(CARD_HEIGHT, CARD_HEIGHT, None, self.pygameWrapper.leftArrowBorder, self.pygameWrapper)
        self.leftArrow.addGraphic(self.pygameWrapper.leftArrowImage)


        # This card stuff is neded to render the players cards
        self.firstCard = 0 # First card is the card the furthest to the left we will render
        self.lastCard = 0 # Last card is the card the furthest to the right we will render
        self.cards = [] # And this is the list of card clickables we will make.


    ''' turnOffClickCooldown
        This handles the turning off of clickCooldown! It's called as a thread after turning the cooldown on, so it'll turn off.
    '''
    def turnOffClickCooldown(self):
        self.clickCooldown = False

        # This canHover logic might not be pretty, but it allows us to give feedback to the user that they cannot use the Clickable.
        # Basically, we tell that when the clickcooldown is on, then the arrow cannot show a hover image.
        self.rightArrow.canHover = True
        self.leftArrow.canHover = True

    ''' turnOnClickCooldown
        This is how we handle the turning on of clickCooldown! Oh, and the logic of making sure it turns off eventually.
    '''
    def turnOnClickCooldown(self):
        self.clickCooldown = True
        
        self.rightArrow.canHover = False
        self.leftArrow.canHover = False
        
        # We just make a thread that waits 0.5 seconds to turnOffClickCooldown
        threading.Timer(0.5, self.turnOffClickCooldown).start()


    ''' updateCards
        This function updates self.cards by taking a player, looking through their cards, and making clickables of them all.
    '''
    def updateCards(self, player):
        self.cards = [] # Reset the current cards
        for card in player.hand.cards:
            # For each card make a clickable of it, add its respective color and rank, and then add it to our list of card clickables.
            newCard = Clickable(CARD_WIDTH, CARD_HEIGHT, card, self.pygameWrapper.purpleBorder, self.pygameWrapper)
            newCard.addGraphic(self.pygameWrapper.getColor(card.color))
            newCard.addGraphic(self.pygameWrapper.getType(card.rank))
            self.cards.append(newCard)
    

    ''' updateLastCard
        This function finds the last card in our current list of card clickables. 
        That's done by just calculating the amount of them, and then size of each one.
    '''
    def updateLastCard(self, player):
        cardsPerRender = int((self.pygameWrapper.screenWidth/64) - 2) # Cards are 48 pixels but we want parts in between. We also want 2 places for arrows
        self.lastCard = self.firstCard + (cardsPerRender - 1) # cardsPerDisplay - 1, because the firstCard counts, and we start at 0.
        if self.lastCard > len(player.hand.cards): 
            self.lastCard = len(player.hand.cards)


    ''' updateUserState
        This function just calls .updateLastCard and .updateCards, as well as making sure the discardClick texture matches the discardPile
    '''
    def updateUserState(self, player):
        self.updateLastCard(player)
        self.updateCards(player)

        self.discardClick.graphics = [] # Reset what graphics the discard currently is graphics
        self.discardClick.addGraphic(self.pygameWrapper.getColor(self.discardPile.cards[-1].color)) # Make the texture match its top card
        self.discardClick.addGraphic(self.pygameWrapper.getType(self.discardPile.cards[-1].rank))


    ''' renderTurn
        This function renders the turn we have in interfaceUser.
        Unlike other objects rendering, this deserves it's own function due to semi-tricky hand rendering logic.
    '''
    def renderTurn(self):
        # We display our buttons first, so cards can then be displayed ontop of them.
        if len(self.cards) > self.lastCard: # If there are more cards then the last we are rendering,
            # Show the right arrow, so we can go right and make a new last card!
            self.rightArrow.displayAtCoords(self.pygameWrapper.screenWidth-CARD_HEIGHT/2, self.pygameWrapper.screenHeight-CARD_HEIGHT/2)
        if 1 < self.firstCard: # If there are more cards then the first we are rendering
            # Show the left arrow, so we can go left and make a new first card!
            self.leftArrow.displayAtCoords(CARD_HEIGHT/2, self.pygameWrapper.screenHeight-CARD_HEIGHT/2)

        self.discardClick.displayAtCoords(self.pygameWrapper.screenWidth/2 + CARD_WIDTH, self.pygameWrapper.screenHeight/4)
        self.drawClick.displayAtCoords(self.pygameWrapper.screenWidth/2 - CARD_WIDTH, self.pygameWrapper.screenHeight/4)
        self.unoButton.displayAtCoords(CARD_HEIGHT/2, CARD_WIDTH/2)

        currentCard = 1 # Though the list starts at 0, the "physical" cards start at 1. There is no "0th" card in our 2D space.
        for i in range(self.firstCard, self.lastCard):
            card = self.cards[i]
            if not card.clicked: # If the card is not clicked / dragged, then we just display at its proper coordinates
                card.displayAtCoords((currentCard+1) * 64,  self.pygameWrapper.screenHeight - CARD_HEIGHT/2) # We add one so we have room for the left arrow
            else: # But if it is being dragged, then display it where it currently is.
                card.display()
            currentCard += 1


    ''' interfaceUser
        This function handles the interfacing of the user
        It updates the state of the current interface to match the users current player, and then outputs the users actions.
    '''
    def interfaceUser(self, player):
        self.currentUser = player
        self.updateUserState(player)

        while True:
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()
            selected = None

            for event in pygame.event.get(): # This is for external interactions, like movement or keys.
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collect

            # This sets a nice light blue background. We do this each frame to basically reset the screen.
            self.pygameWrapper.screen.fill((173, 216, 230))
            self.renderTurn() # This renders the display
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
            
            # If the discard pile is clicked, whilst a card is dragged on it, return the dragged card.
            if self.discardClick.isClicked(mouseButtons, mousePos) and selected is not None:
                return selected.clickedObject
    

    ''' promptPlayCard
        This function prompts the user if they want to play the inputted card.
    '''
    def promptPlayCard(self, card):
        self.pygameWrapper.screen.fill((173, 216, 230)) # Baby blue :-)

        # The Card
        playableCard = Clickable(CARD_WIDTH, CARD_HEIGHT, card, self.pygameWrapper.purpleBorder, self.pygameWrapper)
        playableCard.addGraphic(self.pygameWrapper.getColor(card.color))
        playableCard.addGraphic(self.pygameWrapper.getType(card.rank))
        playableCard.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/2)

        # The yes option
        yes = Clickable(CARD_HEIGHT, CARD_WIDTH, None, None, self.pygameWrapper)
        yes.addGraphic(self.pygameWrapper.yesImage)
        yes.displayAtCoords(self.pygameWrapper.screenWidth/4, self.pygameWrapper.screenHeight/5 * 4)

        # The no option
        no = Clickable(CARD_HEIGHT, CARD_WIDTH, None, None, self.pygameWrapper)
        no.addGraphic(self.pygameWrapper.noImage)
        no.displayAtCoords(self.pygameWrapper.screenWidth/4*3, self.pygameWrapper.screenHeight/5 * 4)

        # The caption asking "WOULD YOU LIKE TO PLAY THIS CARD?"
        playCard = Clickable(BAR_WIDTH, CARD_HEIGHT, None, None, self.pygameWrapper)
        playCard.addGraphic(self.pygameWrapper.playCardImage)
        playCard.displayAtCoords(self.pygameWrapper.screenWidth/2, self.pygameWrapper.screenHeight/2 - CARD_HEIGHT)

        pygame.display.flip() # Render it all nce, since we don't need to update it.
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collect
        
            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()

            if yes.isClicked(mouseButtons, mousePos):
                return True # If yes is clicked, then we return yes (True)

            if no.isClicked(mouseButtons, mousePos):
                return False # If no is clicked, then we return no (False)


    ''' chooseColor
        This function shows the four colors of UNO, and asks the user to select one.
        It takes a prompt, as there are many reasons we may want the user to select a color.
    '''
    def chooseColor(self, prompt):
        # The prompt
        promptSurface = self.pygameWrapper.font.render(prompt, self.pygameWrapper.font, (0,0,0))


        # The four colors with borders because I'm nice!
        redChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, self.pygameWrapper.purpleBorder, self.pygameWrapper)
        redChoice.addGraphic(self.pygameWrapper.redCardImage)
        
        greenChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, self.pygameWrapper.purpleBorder, self.pygameWrapper)
        greenChoice.addGraphic(self.pygameWrapper.greenCardImage)

        blueChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, self.pygameWrapper.purpleBorder, self.pygameWrapper)
        blueChoice.addGraphic(self.pygameWrapper.blueCardImage)

        yellowChoice = Clickable(CARD_WIDTH, CARD_HEIGHT, None, self.pygameWrapper.purpleBorder, self.pygameWrapper)
        yellowChoice.addGraphic(self.pygameWrapper.yellowCardImage)

        while True:
            self.pygameWrapper.screen.fill((173, 216, 230)) # Light blue, otherwise known as ral 6207, apparently.

            # Display the font
            self.pygameWrapper.screen.blit(promptSurface, (self.pygameWrapper.screenWidth/2 - len(prompt)*4, self.pygameWrapper.screenHeight/2-CARD_HEIGHT))
            
            # Display the four colors!
            redChoice.displayAtCoords(self.pygameWrapper.screenWidth/5, self.pygameWrapper.screenHeight/2)
            greenChoice.displayAtCoords(self.pygameWrapper.screenWidth/5 * 2, self.pygameWrapper.screenHeight/2)
            blueChoice.displayAtCoords(self.pygameWrapper.screenWidth/5 * 3, self.pygameWrapper.screenHeight/2)
            yellowChoice.displayAtCoords(self.pygameWrapper.screenWidth/5 * 4, self.pygameWrapper.screenHeight/2)

            mousePos = pygame.mouse.get_pos()
            mouseButtons = pygame.mouse.get_pressed()

            for event in pygame.event.get(): # This is for external interactions, like movement or keys.
                if event.type == pygame.QUIT: # pygame.QUIT is a windows exit / X button
                    pygame.quit() # Clicking it should instantly shut down the game.
                    sys.exit() # It's just much easier this way. Python shouldn't care; it has a garbage collect

            # If the user selects a color, return that color!
            if redChoice.isClicked(mouseButtons, mousePos):
                return 'RED'

            if greenChoice.isClicked(mouseButtons, mousePos):
                return 'GREEN'

            if blueChoice.isClicked(mouseButtons, mousePos):
                return 'BLUE'

            if yellowChoice.isClicked(mouseButtons, mousePos):
                return 'YELLOW' 

            pygame.display.flip()





""" Random, kind of bad example code. Uses Ryan's card from this branch: https://github.com/jul1anpa/project-uno/tree/CardClass
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

# Look, this works!!!! 
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