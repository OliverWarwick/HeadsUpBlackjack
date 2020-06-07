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
		self.sqliteConnection = None
		self.cursor = None



	''' 
	Checks if the database file exists, if not will create it and set up the tables needed.
	If so will connect to it and pass back an sqlite3 connector object.
	'''
	def setUpDatabaseFile(self):

		if not path.exists("heads_up_database.db"):

			# Create the new file and then build a connection.
			self.sqliteConnection = sqlite3.connect('heads_up_database.db')
			self.connector = self.sqliteConnection.cursor()

			# Add the tables we need.
			create_table_string = """CREATE TABLE card_history (
										hand_id INTEGER PRIMARY KEY,
										bet_amount INTEGER NOT NULL,
										dealer_face_up_card_value INT NOT NULL,
										player_card_one_value INT,	
										player_card_two_value INT,
										player_card_three_value INT,
										player_card_four_value INT,
										player_card_five_value INT,
										player_total INT,
										dealer_total INT,
										player_win INT		
										);"""					# This will be -1 for dealer
																# 1 for normal win, and 2 for backjack.
			self.connector.execute(create_table_string)	
			self.sqliteConnection.commit()
		try:
			self.sqliteConnection = sqlite3.connect('heads_up_database.db')
			self.connector = self.sqliteConnection.cursor()
			print("Database created and Successfully Connected to SQLite")

		except sqlite3.Error as error:
			print("Error while connecting to sqlite", error)
		
	''' 
	Shut down the link, needs to be called at the end of the program 
	'''
	def closeDatabaseConnection(self):
		try:
			self.connector.close()
			self.sqliteConnection.close()
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
	input:
		playerScore :: int
		dealerScore :: int
		playerBlackjack :: bool
		winner :: string
	return :: string
	'''
	
	def generateQueryForDB(self, playerScore, dealerScore, playerBlackjack, winner):
		

		query_builder_first_line = "INSERT INTO card_history (bet_amount, dealer_face_up_card_value,"
		
		print(len(self.player.currentHand))

		numberOfPlayerCardsDrawn = min(len(self.player.currentHand),5)
		col_names = ["player_card_one_value", "player_card_two_value","player_card_three_value", "player_card_four_value", "player_card_five_value"]
		for i in range(0,numberOfPlayerCardsDrawn):				# Add in all the cards
			query_builder_first_line += (col_names[i] + ",")
		query_builder_first_line += "player_total,dealer_total,player_win)"		# Add in the final columns

		query_builder_second_line = " VALUES (" + str(self.player.currentBet) + "," + \
								str(self.dealer.getFaceUpCard().getNumericValue()) + ","
		
		for j in range(0,numberOfPlayerCardsDrawn):		# Add in all the values
			query_builder_second_line += (str(self.player.currentHand[j].getNumericValue()) + ",")
		query_builder_second_line += (str(playerScore) + "," + str(dealerScore) + ",")

		if winner == "Player" and playerBlackjack == True:
			query_builder_second_line += str(2)
		elif winner == "Player":
			query_builder_second_line += str(1)
		else:
			query_builder_second_line += str(-1)

		full_query = query_builder_first_line + query_builder_second_line + ");"

		print(full_query)

		return full_query









	''' 
	This completes one hand of blackjack.
	'''

	def playOneHand(self):

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

		query = self.generateQueryForDB(self.player.getHandScore(), self.dealer.getHandScore(), self.player.isBlackjack(), winner)

		self.connector.execute(query)
		self.sqliteConnection.commit()

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

		ask = input("Would you like to play again? (Y/N) ")
		return ask.startswith("Y")
			



	def playGame(self):

		playAgain = True
		while playAgain and self.player.currentMoney > 0 and self.deck.numberOfCards > 10:
			playAgain = self.playOneHand()



game = Game()
game.setUpDatabaseFile()
game.playGame()
game.connector.execute("SELECT * FROM card_history")
record = game.connector.fetchall()
print(record)
print("Shut down complete: ", game.closeDatabaseConnection())


