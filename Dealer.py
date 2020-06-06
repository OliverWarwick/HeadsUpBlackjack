# Dealer class to act as the decision maker from the dealer side. 

# Fields:
# currentMoney :: int
# currentHand  :: Hand

from Player import Player
from Deck import Deck
from Card import Card

class Dealer(Player):

	def __init__(self, totalToBegin = 1000):

		self.currentMoney = totalToBegin
		self.currentHand = []
		self.finishedHand = False

	''' Dealer should hit on another up to and including 16. Will also STAND if the player is bust'''
	def getDealerResponse(self, playerScore):
		if self.getHandScore() > 16 or playerScore > 21:
			self.finishedHand = True
			return "STAND"
		else:
			return "HIT"






	def getFaceUpCard(self):
		return self.currentHand[0]

	def printFaceUpCard(self):
		print("Dealer's face up card: ")
		print(self.getFaceUpCard())
		print()

	def printFullHand(self):
		print("Dealer's current hand: ")
		for card in self.currentHand:
			print(card)
		print()

