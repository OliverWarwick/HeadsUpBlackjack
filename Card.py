# Card class with 2 attributes: Suit (String), Value (String)

class Card:

    def __init__(self, suit = "", value = ""):

        self.suit = suit
        self.value = value

    '''
    Method to convert the string of the card into the underlying numeric value
    '''
    def getNumericValue(self):

        # Dictionary holding the values
        # Used to seperate out the 4 values of 10.

        valueLookUpDict = {"Ace": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "Jack": 10, "Queen": 10, "King": 10}

        try:
            numValue = valueLookUpDict.get(self.value)
        except Exception:
            numValue = 0

        return numValue

    '''
    Override method for printing a card
    '''
    def __str__(self):
        return "(" + str(self.value) + ", " + str(self.suit) + ")"
