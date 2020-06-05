# Card class with 2 attributes: Suit (String), Value (String)

class Card:

    def __init__(self, suit = "", value = ""):

        self.suit = suit
        self.value = value


    def getNumericValue(self):

        # Dictionary holding the values
        # Used to seperate out the 4 values of 10.

        valueLookUpDict = {"Ace": 14, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "Jack": 11, "Queen": 12, "King": 13}

        try:
            numValue = valueLookUpDict.get(self.value)
        except:
            numValue = 0

        return numValue