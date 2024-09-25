class Hand(object):
    '''A collection of Cards'''
    def __init__(self):
        """Initialize an empty hand of cards."""
        self.cards = []

    def add_card(self, card):
        """Add a card to the hand."""
        self.cards.append(card)

    def remove_card(self, card):
        """Remove a card from the hand, if it exists."""
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False

    def show_hand(self):
        """Display the cards in the hand."""
        return self.cards

    def count_cards(self):
        """Return the number of cards in the hand."""
        return len(self.cards)
