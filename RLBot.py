from Player import Player
import pandas as pd
import random

class RLBot(Player):

	def __init__(self, totalToBegin = 10000000):

		self.currentMoney = totalToBegin
		self.currentHand = []
		self.currentBet = 0
		self.finishedHand = False

	def getBetAmountTerminal(self):

		if self.currentMoney <= 0:
			raise ValueError("Insufficent funds to continue playing")
		else:
			if self.currentMoney >= 100:
				self.currentBet = 100
			else:
				self.currentBet = self.currentMoney

	def getResponse(self, dealerFaceUpCard, dataframe, verbose = False):

		# Find the row we are dealing with.
		playerScore = self.getHandScore()
		# print("PlayerScore ", playerScore)
		# print("Dealer Face Up Value: ", dealerFaceUpCard.getNumericValue())
		row = dataframe[(dataframe.PlayerTotal == playerScore) & (dataframe.DealerFaceUp == dealerFaceUpCard.getNumericValue())]

		# print(row)

		# Then we can query the row for which is greater out of the two.
		rewardHit = row['RewardHit'].values[0]
		rewardStand = row['RewardStand'].values[0]

		# print("Reward Hit: ", str(rewardHit), "       Reward Stand: ", str(rewardStand))

		# TODO - Add a small randomness for an e-greedy stratergy.

		if rewardHit > rewardStand:
			return "HIT"
		elif rewardHit < rewardStand:
			self.finishedHand = True
			return "STAND"
		else:
			choice = random.choice(["HIT", "STAND"])		# Don't want to bias either side so use this.
			if choice == "STAND":
				self.finishedHand = True
			# print(choice)
			return choice









