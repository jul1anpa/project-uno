import random

class AIPlayer:
    def __init__(self, name):
        self.name = name
        self.hand = []  # List of UNOCard objects
        self.score = 0

    def draw_card(self, deck):
        """A.I. Draws a card from the deck and adds it to the player's hand."""
        
        if deck:
            card = deck.pop()
            self.hand.append(card)
            print(f"{self.name} draws a card: {card}")
        else:
            print("The deck is empty.")

    def play_card(self, top_card):
        """A.I. Plays a card from hand that matches the top card or a wild card."""
        
        playable_cards = [card for card in self.hand if card.color == top_card.color or card.value == top_card.value or card.value == "Wild"]
        
        if playable_cards:
            chosen_card = random.choice(playable_cards)
            self.hand.remove(chosen_card)
            print(f"{self.name} plays: {chosen_card}")
            return chosen_card
        else:
            print(f"{self.name} has no playable card and needs to draw.")
            return None

    def update_score(self):
        """A,I. Updates the score based on the remaining cards in hand."""
        
        self.score = sum(1 for card in self.hand)  
        # Simple scoring: 1 point per card
        
        print(f"{self.name}'s score is now: {self.score}")

    def reset_hand(self):
        """A.I. Resets the player's hand."""
        
        self.hand = []
        print(f"{self.name}'s hand has been reset.")

    def __str__(self):
        hand_str = ', '.join(str(card) for card in self.hand)
        return f"AI Player: {self.name}, Hand: [{hand_str}], Score: {self.score}"
