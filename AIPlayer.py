# To act randomly to begin with to populate the dataset.
import random 
from Player import Player
from Card import Card
import pandas as pd
import numpy as np

class AIPlayer(Player):

	def __init__(self, totalToBegin = 10000):

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



	# TODO - figure out how to make it so that it checks for a permuation of the 
	# card numbers and not an exact match.

	# Also then need to calculate how many of those wins came from hit and 
	# how many came from stand.

	def getResponseExploitation(self, dealerFaceUpCard, connection, verbose = False):

		# TODO - Need to fix for more then 2 cards.

		# Using the current cards, query the database to see how many values and successes.

		if self.getHandScore() >= 21: 
			self.finishedHand = True
			return "STAND"
		if self.getHandScore() <= 11: 
			return "HIT"

		hitting_ev = 0
		standing_ev = 0 		# Incase the dataframe is empty.
		number_of_cards = len(self.currentHand)
		current_card_total = str(self.getHandScore())

		if verbose:
			print("Current card total: ", current_card_total)
			print()
			print("\nHitting query")

		# This is to create the card part of the query string.
		list_of_cards = ["player_card_one_value", "player_card_two_value","player_card_three_value","player_card_four_value","player_card_five_value"]
		string_for_number_of_cards = ""
		for k in range(0,min(number_of_cards,5)):
			string_for_number_of_cards += (list_of_cards[k] + ", ")
		string_for_sum_of_cards = ""
		for k in range(0,min(number_of_cards,5)):
			 string_for_sum_of_cards += (list_of_cards[k] + " + ")

		# Bit of butchering but works well, just had to trim off the end + simple for the number of cards string.
		query_to_send = "SELECT setting, dealer_face_up_card_value, " + string_for_number_of_cards + " player_win, SUM(" + string_for_sum_of_cards[:-2] +  ") AS running_total FROM card_history WHERE " + list_of_cards[min(number_of_cards,4)]  + " IS NOT NULL GROUP BY hand_id HAVING running_total = " + current_card_total + " AND " + "dealer_face_up_card_value = " + str(dealerFaceUpCard.getNumericValue()) 
		hitting_frame = pd.read_sql_query(query_to_send, connection)
		
		if verbose: 
			print(hitting_frame)

		# Count the number of wins and loses and put this into a small dataframe
		hitting_win_loss_data = hitting_frame['player_win'].value_counts()

		 		# Incase the dataframe is empty.
		if not hitting_win_loss_data.empty:
			# Dot product these to give a final EV score of this option.
			# This gets the frequency and scores and evaluates the EV.
			hitting_ev = np.dot(hitting_win_loss_data.values, hitting_win_loss_data.index.values) / len(hitting_frame)
		
		if verbose:
			print("Hitting EV: ", hitting_ev)
			

		query_to_send = "SELECT setting, dealer_face_up_card_value, " + string_for_number_of_cards + " player_win, SUM(" + string_for_sum_of_cards[:-2] + ") AS running_total FROM card_history WHERE " + list_of_cards[min(number_of_cards,4)] + " IS NULL GROUP BY hand_id HAVING running_total = " + current_card_total + " AND " + "dealer_face_up_card_value = " + str(dealerFaceUpCard.getNumericValue()) 
		standing_frame = pd.read_sql_query(query_to_send, connection)

		if verbose:
			print("\nStanding query")
			print(standing_frame)

		# Count the number of wins and loses and put this into a small dataframe
		standing_win_loss_data = standing_frame['player_win'].value_counts()

		
		if not standing_win_loss_data.empty:
			# Dot product these to give a final EV score of this option.
			# This gets the frequency and scores and evaluates the EV.
			standing_ev = np.dot(standing_win_loss_data.values, standing_win_loss_data.index.values) / len(standing_frame)
		
			query_to_send = "SELECT dealer_face_up_card_value, player_card_one_value, player_card_two_value, player_win, SUM(player_card_one_value + player_card_two_value) AS running_total FROM card_history GROUP BY hand_id HAVING running_total = " + current_card_total + " AND " + "dealer_face_up_card_value = " + str(dealerFaceUpCard.getNumericValue()) 
			if verbose:
				print("Standing EV: ", standing_ev)
				print("\nFull query")
				print(pd.read_sql_query(query_to_send, connection))

			# query_to_send = "SELECT player_win, COUNT(player_win) AS total FROM card_history WHERE dealer_face_up_card_value = " + str(dealerFaceUpCard.getNumericValue()) + " AND player_card_one_value = " + str(self.currentHand[0].getNumericValue()) + " AND player_card_two_value = " + str(self.currentHand[1].getNumericValue()) + " GROUP BY player_win"
			# print(pd.read_sql_query(query_to_send, connection))

		###
		# TODO
		###
		# Should be able to tidy this up at some point, no need to have the score.
		if standing_ev >= hitting_ev or (self.getHandScore() >= 20 and standing_ev == 0):
			self.finishedHand = True 
			return "STAND"
		else:
			return "HIT"


	def getResponseExploration(self, dealerFaceUpCard, verbose = False):


		# TODO - not right when has a score of 19 or 20, wants to hit for some reason? 
		# Check tomrorow whether this fraction is causing issues

		if self.getHandScore() >= 20:
			self.finishedHand = True
			return "STAND"
		elif self.getHandScore() <= 10:		# Safe to hit.
			return "HIT"
		else:

			# Find the upper bound on card in order to make it not bust.
			# This acts as a semi-optimal strat to start with.

			# upperBound = 21 - self.getHandScore()
			# frac = upperBound / 10
			if random.random() < 0.66:
			# if random.random() < 0.5:
				return "HIT"
			else:
				self.finishedHand = True
				return "STAND"



