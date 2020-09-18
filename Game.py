# Game class which will action the play within the game. We create a game by creating a 
# dealer and player, then initallising a deck.

from Card import Card
from Deck import Deck
from Dealer import Dealer
from Player import Player
from AIPlayer import AIPlayer
from RLBot import RLBot
import sys
from os import path
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import os


class Game(): 

	def __init__(self, df, shuffle=True):

		self.deck = Deck()
		self.deck.createNewFullDeck(shuffle=shuffle)
		self.dealer = Dealer(totalToBegin = 1000)
		self.player = RLBot(totalToBegin = 1000000000)
		self.playerHistory = []
		self.dataframe = df

	''' 
	Function to evaluate the result of a bet after the player and dealer have completed
	their hands. Correctly puts the money where it should be during the execution.
	'''

	def settleBet(self):

		winner = ""

		playerScore = self.player.getHandScore()
		playerBlackjack = self.player.isBlackjack()
		dealerScore = self.dealer.getHandScore()

		# If player score is greater than 21 they are bust and lose the bet.
		if playerScore > 21:
			self.player.currentMoney -= self.player.currentBet
			self.dealer.currentMoney += self.player.currentBet
			winner = "Dealer"
		else:
			# This is a win for a dealer, so played out at 1:1
			if dealerScore > 21 or (dealerScore <= 21 and playerScore > dealerScore and not playerBlackjack):
				self.player.currentMoney += self.player.currentBet
				self.dealer.currentMoney -= self.player.currentBet
				winner = "Player"
			else:
				# This would mean the dealer than won.
				if dealerScore > playerScore:
					self.player.currentMoney -= self.player.currentBet
					self.dealer.currentMoney += self.player.currentBet
					winner = "Dealer"
				elif dealerScore == playerScore:
					if dealerScore == 21 and len(self.dealer.currentHand) == 2:
						winner = "Draw"
					else:
						winner = "Dealer"		# This is to account for that when dealer and player have blackjack.
				else:
					# If the player has blackjack, and beats the dealer then played out at 2:1.
					if playerScore > dealerScore and playerBlackjack:
						self.player.currentMoney += 2 * self.player.currentBet
						self.dealer.currentMoney -= 2 * self.player.currentBet
						winner = "Player"
					else:
						raise Exception("Error, unseen pattern in betting - weird.")

		return winner


	def getReward(self, winner):

		# Convert the winner text to a concrete reward. -1 for loss, 0 for draw, 1 for win, 2 for blackjack.
		if winner == "Dealer":
			return -1
		elif winner == "Draw":
			return 0
		else:
			if self.player.isBlackjack():
				return 2
			else:
				return 1


	def updateDataFrame(self, dataframe, winner, stepSize = 0.1, discount = 1):

		# Get the reward from the function above.
		reward = self.getReward(winner)
		# print("Reward: ", reward)

		# Here we want to first use the dealers card and players total to identify the row.
		playerScore = self.player.getHandScore()
		# print("Players Score ", playerScore)

		newValue = None

		# First want to find the row which is the players current score (providing not over 21, if so we can just skip)
		# The player must have now stood. So we can allow
		if playerScore <= 21:

			# Find the row in question
			rowIndex = dataframe[(dataframe.PlayerTotal == playerScore) &
								 (dataframe.DealerFaceUp == self.dealer.getFaceUpCard().getNumericValue())].index.values[0]

			# Update the row.
			prevValue = dataframe.iloc[rowIndex]["RewardStand"]
			prevStandsNum = dataframe.iloc[rowIndex]["NumberOfStands"]
			newValue = prevValue + stepSize * reward
			dataframe.at[rowIndex, "RewardStand"] = newValue
			dataframe.at[rowIndex, "NumberOfStands"] = prevStandsNum + 1

			# print(dataframe.iloc[rowIndex])

		# This works backwards for each of the hits.
		# TODO - This should really be updating to the value of the new state that it gets put in
		# TODO - rather than the end result, but will change.

		numberOfHits = len(self.player.currentHand) - 2

		for i in range(numberOfHits):
			# Artifically remove a card the 'hit' card from the hand.
			self.player.currentHand.pop()
			runningScore = self.player.getHandScore()

			# This running score must be <= 21. We query for it, and update the row using the same discount value.
			rowIndex = dataframe[(dataframe.PlayerTotal == runningScore) & (
						dataframe.DealerFaceUp == self.dealer.getFaceUpCard().getNumericValue())].index.values[0]

			# This time looking for the hit value, and update this using the hit value.
			prevValue = dataframe.iloc[rowIndex]["RewardHit"]
			prevHitsNum = dataframe.iloc[rowIndex]["NumberOfHits"]
			if newValue != None:
				newValue = prevValue + discount * newValue		# So this uses the new value generated from the previous
																# iteration, which has already been sized down using step size
				dataframe.at[rowIndex, "RewardHit"] = prevValue + stepSize * reward * discount
				dataframe.at[rowIndex, "NumberOfHits"] = prevHitsNum + 1
			else:
				newValue = prevValue + stepSize * reward		# This will only get executed in the first version of the loop.
																# So this will be the reward for hitting and ending up with a
																# number greater than 21.
				dataframe.at[rowIndex, "RewardHit"] = newValue
				dataframe.at[rowIndex, "NumberOfHits"] = prevHitsNum + 1



			# print(dataframe.iloc[rowIndex])





	''' 
	This completes one hand of blackjack.
	'''

	def playOneHand(self, verbose = False, update=True):

		# Print out the amount of money the player have, and then ask for a bet amount.
		self.player.getBetAmountTerminal()

		# Deal out the cards to the dealer and player.
		self.deck.dealInitalCards(self.dealer.currentHand)
		self.deck.dealInitalCards(self.player.currentHand)

		# Display the cards the player has as well as the face up dealer card.
		if verbose:
			print()
			self.player.printHand()
			self.dealer.printFaceUpCard()

		# Query if the player would like another card.
		while (not self.player.finishedHand) and (self.player.getHandScore() <= 21):

			playerResponse = self.player.getResponse(dealerFaceUpCard=self.dealer.getFaceUpCard(), dataframe=self.dataframe)

			if playerResponse == "HIT":
				self.deck.dealAdditionalCard(self.player.currentHand)
				
				if verbose: 
					self.player.printHand()

		# Then allow the dealer to play out their hand.
		while not self.dealer.finishedHand:
			dealerResponse = self.dealer.getDealerResponse(self.player.getHandScore())
			if dealerResponse == "HIT":
				self.deck.dealAdditionalCard(self.dealer.currentHand)

		# Print out both of the hands.
		if verbose:
			self.player.printHand()
			self.dealer.printFullHand()

		# Settle up the bets now
		winner = self.settleBet()

		if verbose:
			print("Updating the dataframe")

		# Update the dataframe to include the new results.
		# This is where the RL happens.
		if update:
			self.updateDataFrame(self.dataframe, winner=winner, stepSize=0.1)


		# Finally set the betting totals back to zero to ensure no spill over, and the hands back to empty.
		self.player.currentBet = 0
		self.player.finishedHand = False
		self.player.currentHand = []
		self.dealer.currentHand = []
		self.dealer.finishedHand = False

		# Print out the new game state.
		if verbose:
			print("Winner of the hand: {0}".format(winner))
			print("Player's current total {0}".format(self.player.currentMoney))
			print("End of hand\n")

		# ask = input("Would you like to play again? (Y/N) ")
		return True
			

	# TODO - Fix verbose issue with the new routines.
	# Normal method for game play.
	def playGame(self, verbose=False, update = True, printHistory = False, numberOfIters = 1000):

		self.player = RLBot()		# Create fresh for the history.
		self.playerHistory = []

		# Explore Stage
		for i in range(0,numberOfIters):
			count = 0
			while count < 5 and self.player.currentMoney > 0 and self.deck.numberOfCards > 10:
				playAgain = self.playOneHand(verbose=verbose, update=update)
				if not update:
					self.playerHistory.append(self.player.currentMoney - 10000000)
				count += 1
			# Create new deck.
			self.deck = Deck()
			self.deck.createNewFullDeck()
			# print("Completed cycle: ", str(i))

		if printHistory:
			print(self.playerHistory)










# df_results = pd.DataFrame(columns=['Trial Number','History','End','Mean','Min','Max', "Varience"])
#
#
#
# # For now just naively explore.
#
# explore_runs = [500000, 100000, 100000, 50000, 50000]
#
# game = Game()
# game.setUpDatabaseFile()
# for i in range(0,5):
# 	game.explore(trials = explore_runs[i])
# 	df_results = game.exploit(trial_number = 5, batch_size = 1000, dataFrame = df_results)
# # game.connector.execute("SELECT * FROM card_history")
# # record = game.connector.fetchall()
# # print(record)
# print("Shut down complete: ", game.closeDatabaseConnection())
#
#
#
#
# z = np.polyfit(x=df_results.index, y=df_results.loc[:, "Mean"], deg=1)
# p = np.poly1d(z)
# df_results['Trendline'] = p(df_results.index)
# print(df_results)
#
#
# df_results.to_csv("results")
#
# plt.plot(df_results["Min"], color='red', label='Min Value', alpha = 0.25)
# plt.plot(df_results["Max"], color='green', label='Min Value', alpha = 0.25)
# plt.plot(df_results['Mean'], color='blue', label='Mean Value')
# plt.plot(df_results['Trendline'], color='blue', label='Trend', alpha = 0.5)
#
# plt.title("Mean value over time")
# plt.show()


if __name__ == '__main__':

	# Need to pass in a dataframe.

	# Create the dataframe here.
	columns = ['PlayerTotal', 'DealerFaceUp', "RewardHit", "NumberOfHits", "RewardStand", "NumberOfStands"]
	data = []

	# Populate the dataframe for every example possible, setting all values to zero thus far.
	possibleTotals = list(range(2,22))
	possibleFaceUp = list(range(2,12))

	for pt in possibleTotals:
		for pfc in possibleFaceUp:
			data.append([pt,pfc,0,0,0,0])		# Settling all initally to zero.


	# Create the dataframe and set this up
	# ToDO - move this inside the class of the game, or give it to the player class.
	# They are the only class that uses the data.

	# TODO - add in 6 deck to the game.

	# TODO - streamline

	if os.path.isfile('trial_run.csv'):
		print("Loading existing dataframe")
		dataframe = pd.read_csv('trial_run.csv', index_col=0)
	else:
		print("Creating new dataframe")
		dataframe = pd.DataFrame(data, columns=columns)
		new_dtypes = {"RewardHit": np.float64, "RewardStand": np.float64}
		dataframe = dataframe.astype(new_dtypes)
		pd.set_option('max_columns',7)
		# print(dataframe.head())



	game = Game(dataframe)

	for p in range(0,5):

		playerRecords = []
		playerEndScore = []

		for j in range(1,5):
			print("Round {0} of learning".format(str(j)))
			game.playGame(verbose=False, update=True, printHistory=False, numberOfIters=100)
			print("Round {0} of evaluating".format(str(j)))
			game.playGame(verbose=False, update=False, printHistory=False, numberOfIters=50)
			playerRecords.append(game.playerHistory)

			playerEndScore.append(playerRecords[-1])

		print("Mean of scores: ",  np.mean(playerEndScore))

	# Save dataframe to a csv.
	game.dataframe.to_csv("trial_run.csv")

	# # Some queries for the df.
	# print("\n\nHitting Data\n\n")
	# print(game.dataframe[game.dataframe.RewardHit != 0])
	# print("\n\nSitting Data\n\n")
	# print(game.dataframe[game.dataframe.RewardStand != 0])

	colormap = plt.cm.gist_ncar
	plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.jet(np.linspace(0, 1, len(playerRecords)))))


	for j in range(0,len(playerRecords)):
		plt.plot(list(range(0,len(playerRecords[j]))), playerRecords[j], label="Run {0}".format(str(j+1)))
	plt.legend()
	plt.xlabel('Number of Hands')
	plt.ylabel('P & L')
	plt.show()



	# ToDo - Create a standard 50 hand long set of deals for this to deal with, for testing procedure to see if it is getting better.

	# This will be much quicker through using a dictionary to hold the information to begin with, and then from there at the end fo the run write this to a dataframe
	# Rather than having to do this inhouse and spend O(200) operations to find the right row each time.

