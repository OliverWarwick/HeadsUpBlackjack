# Deck class which contains an array of Card objects.

from Card import Card
import random

class Deck:

    def __init__(self):

        # Should have a counter for the number of cards

        self.numberOfCards = 0
        self.cards = []

    def createNewFullDeck(self):

        Suits = ["Diamonds", "Spades", "Hearts", "Clubs"]
        Values = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

        for s in Suits:
            for v in Values:
                self.cards.append(Card(s,v))

        self.numberOfCards = 52
        self.shuffle()


    #Shuffle the array of current cards.
    def shuffle(self):

        random.shuffle(self.cards)


    def printDeck(self):

        print("Start of deck")
        for card in self.cards:
            print(card.value)
        print("End of deck")