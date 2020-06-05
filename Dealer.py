# Dealer class to act as the decision maker from the dealer side. 

# Fields:
# currentMoney :: int
# currentHand  :: Hand

class Dealer:

	def __init__(self, totalToBegin = 1000):

		self.currentMoney = totalToBegin
		self.currentHand = None


	def getFaceUpCard(self):
		return self.currentHand[0]

	



# getFaceUpCard() 