# Game class which will action the play within the game. We create a game by creating a 
# dealer and player, then initallising a deck.

from Card import Card
from Deck import Deck
from Dealer import Dealer
from Player import Player


class Game(): 

	def __init__(self): 

		self.deck = Deck()
		self.deck.createNewFullDeck()
		self.dealer = Dealer(totalToBegin = 1000)
		self.player = Player(totalToBegin = 1000)


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
game.playGame()


