# Deck class which contains an array of Card objects.

from Card import Card
import random

class Deck:

    def __init__(self):

        # Should have a counter for the number of cards

        self.numberOfCards = 0
        self.cards = []

    '''
    Set up the deck
    '''

    def createNewFullDeck(self, shuffle=True):

        Suits = ["Diamonds", "Spades", "Hearts", "Clubs"]
        Values = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

        for s in Suits:
            for v in Values:
                self.cards.append(Card(s,v))

        self.numberOfCards = 52
        if shuffle:
            self.shuffle()

    def shuffle(self):

        random.shuffle(self.cards)

    def dealAdditionalCard(self, hand):

        if self.numberOfCards >= 1:
            self.numberOfCards -= 1
            hand.append(self.cards.pop())
        else:
            raise EmptyDeckException("1")

    def dealInitalCards(self, hand):

        if self.numberOfCards >= 2:
            self.numberOfCards -= 2
            hand.append(self.cards.pop())
            hand.append(self.cards.pop())
        else:
            raise EmptyDeckException("2")



    def __str__(self):

        s = "Start of deck\n"
        for card in self.cards:
            s += str(card)
            s += "\n"
        s += "End of deck"
        return s


class EmptyDeckException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else: 
            self.message = None

    def __str__(self):
        if self.message:
            return "EmptyDeckException - attempted to remove {0} card(s) from an empty deck".format(self.message)
        else: 
            return "EmptyDeckException"
