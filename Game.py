# Game class which will action the play within the game. We create a game by creating a 
# dealer and player, then initallising a deck.

from Card import Card
from Deck import Deck
from Dealer import Dealer
from Player import Player
import sys
from os import path
import sqlite3


class Game(): 

	def __init__(self): 

		self.deck = Deck()
		self.deck.createNewFullDeck()
		self.dealer = Dealer(totalToBegin = 1000)
		self.player = Player(totalToBegin = 1000)

	''' 
	Checks if the database file exists, if not will create it and set up the tables needed.
	If so will connect to it and pass back an sqlite3 connector object.
	'''
	def setUpDatabaseFile(self):

		if not path.exists("heads_up_database.db"):

			# Create the new file and then build a connection.
			sqliteConnection = sqlite3.connect('heads_up_database.db')
			connector = sqliteConnection.cursor()

			# Add the tables we need.
			create_table_string = """CREATE TABLE card_history (
										hand_id INTEGER PRIMARY KEY,
										bet_amount INTEGER NOT NULL,
										dealer_face_up_card_name TEXT NOT NULL,
										dealer_face_up_card_value INT NOT NULL,
										player_card_one_name TEXT,
										player_card_one_value INT,	
										player_card_two_name TEXT,
										player_card_two_value INT,
										player_card_three_name TEXT,
										player_card_three_value INT,
										player_card_four_name TEXT,
										player_card_four_value INT,
										player_card_five_name TEXT,
										player_card_five_value INT,
										player_total INT,
										dealer_total INT,
										player_win INT		
										);"""					# This will be -1 for dealer
																# 1 for normal win, and 2 for backjack.
			connector.execute(create_table_string)	

		try:
			sqliteConnection = sqlite3.connect('heads_up_database.db')
			connector = sqliteConnection.cursor()
			print("Database created and Successfully Connected to SQLite")

		except sqlite3.Error as error:
			print("Error while connecting to sqlite", error)
		
		return connector

	''' 
	Shut down the link, needs to be called at the end of the program 
	'''
	def closeDatabaseConnection(self,connector):
		try:
			connector.close()
			print("The SQLite connection is closed")
			return True
		except Exception:
			return False
			





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
				if dealerScore >= playerScore:
					self.player.currentMoney -= self.player.currentBet
					self.dealer.currentMoney += self.player.currentBet
					winner = "Dealer"
				else:
					# If the player has blackjack, and beats the dealer then played out at 2:1.
					if playerScore > dealerScore and playerBlackjack:
						self.player.currentMoney += 2 * self.player.currentBet
						self.dealer.currentMoney -= 2 * self.player.currentBet
						winner = "Player"
					else:
						raise Exception("Error, unseen pattern in betting - weird.")

		return winner

	'''
	Function generates the update query to send to the database. 
	return :: string
	'''
	#def generateQueryForDB(self, winner, playerScore, playerBlackjack, dealerScore)
	def generateQueryForDB(self):
		numberOfPlayerCardsDrawn = len(self.player.currentHand)

		query_builder_first = "INSERT INTO card_history (bet_amount, dealer_face_up_card_name, dealer_face_up_card_value)"
		query_builder_second = " VALUES (" + str(self.player.currentBet) + "," + self.dealer.getFaceUpCard().value + "," + str(self.dealer.getFaceUpCard().getNumericValue())

		full_query = query_builder_first + query_builder_second + ");"

		print(full_query)

		return full_query









	''' 
	This completes one hand of blackjack.
	'''

	def playOneHand(self, connector):

		# Print out the amount of money the player have, and then ask for a bet amount.
		self.player.getBetAmountTerminal()

		# Deal out the cards to the dealer and player.
		self.deck.dealInitalCards(self.dealer.currentHand)
		self.deck.dealInitalCards(self.player.currentHand)

		# Display the cards the player has as well as the face up dealer card.
		print()
		self.player.printHand()
		self.dealer.printFaceUpCard()

		# Query if the player would like another card.
		while not self.player.finishedHand:
			playerResponse = self.player.getResponseTerminal(self.dealer.getFaceUpCard())
			if playerResponse == "HIT":
				self.deck.dealAdditionalCard(self.player.currentHand)
				self.player.printHand()

		# Then allow the dealer to play out their hand.
		while not self.dealer.finishedHand:
			dealerResponse = self.dealer.getDealerResponse(self.player.getHandScore())
			if dealerResponse == "HIT":
				self.deck.dealAdditionalCard(self.dealer.currentHand)

		# Print out both of the hands.
		self.player.printHand()
		self.dealer.printFullHand()

		# Settle up the bets now
		winner = self.settleBet()

		print("Writing to database")

		query = self.generateQueryForDB()

		conn.execute(query)

		# Finally set the betting totals back to zero to ensure no spill over, and the hands back to empty.
		self.player.currentBet = 0
		self.player.finishedHand = False
		self.player.currentHand = []
		self.dealer.currentHand = []
		self.dealer.finishedHand = False

		# Print out the new game state.
		print("Winner of the hand: {0}".format(winner))
		print("Player's current total {0}".format(self.player.currentMoney))
		print("End of hand\n")

		playAgain = input("Would you like to play again? (Y/N) ")
		return playAgain



	def playGame(self):

		playAgain = True
		while playAgain and self.player.currentMoney > 0:
			playAgain = self.playOneHand()



game = Game()
conn = game.setUpDatabaseFile()
game.playOneHand(conn)
conn.execute("SELECT * FROM card_history")
record = conn.fetchall()
print(record)
print("Shut down complete: ", game.closeDatabaseConnection(conn))


