# Player class to interact with the game, hold the cards and the current money of 
# the player.

class Player():

	def __init__(self, totalToBegin = 1000):

		self.currentMoney = 0
		self.currentHand = []
		self.currentBet = 0
		self.finishedHand = False


	''' 
	BetAmountTerminal method.
	Asks the user for an input for a bet via terminal input, checks that this is not
	larger than the current balance, and if so throws exception of empty account. 
	Will loop until the bet is possible.
	'''
	def getBetAmountTerminal(self):

		if self.currentMoney <= 0:
			raise ValueError("Insufficent funds to continue playing")
		else:
			betPossible = False
			while not betPossible:
				print("Current balance: {0}".format(self.currentMoney))
				betAmount = int(input("Please enter the bet amount: "))
				if betAmount <= self.currentMoney: 
					self.currentBet = betAmount
					betPossible = True

		return betAmount

	'''
	ResponseTerminal method. 
	This should be called given the dealers face up card. Must either 'HIT' or 'STAND'
	Should only be allowed to HIT if the current total is smaller than 21.
	dealerFaceUpCard :: Card
	'''
	def getResponseTerminal(self, dealerFaceUpCard):

		if self.getHandScore() >= 21:
			self.finishedHand = True
			return "STAND"
		else:
			decision = input("Would you like to STAND or HIT? ")
			if decision.startswith("H"):
				return "HIT"
			else:
				self.finishedHand = True
				return "STAND"


	def printHand(self):
		print("Player's current hand: ")
		for card in self.currentHand:
			print(card)
		print()



	"""
	Function to return the score of the hand using the numeric values of the cards.
	This will add up all the cards first. If this is larger than 21 and there is an ace present
	then it will take away 10 (swapping "Ace -> 1"), until total under 21, or
	:return: Int. Can be more than 21.
	"""
	def getHandScore(self):

		totalScore = 0
		aceCount = 0

		for c in self.currentHand:
			totalScore += c.getNumericValue()
			if c.value == "Ace":
				aceCount += 1

		if (totalScore <= 21) or (totalScore > 21 and aceCount == 0):
			self.score = totalScore
			return totalScore
		else:
			# Check the aces now.
			while aceCount > 0:

				aceCount -= 1
				totalScore -= 10

				if totalScore <= 21:
					self.score = totalScore
					return totalScore
			return totalScore


	"""
	Function to check if a hand is blackjack. I.e: Score will be 21, and there will only be two cards in it.
	:return: Boolean.
	"""
	def isBlackjack(self):
		return (self.getHandScore() == 21) and (len(self.currentHand) == 2)





