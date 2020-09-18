from Game import *
import random
import pandas as pd


def load_data(file):

    try:
        return pd.read_csv(file, index_col=0)
    except FileNotFoundError:
        print("No such dataframe file.")

'''
This is to provide a fair testing ground for the RLbot to be evalulated in, rather than just a random trial
This should return 
'''

def test_model():

    # Load in the dataframe.
    load_data('trial_run')


    # Create a new game for this dataframe.
    game = Game(dataframe, shuffle=False)

    eval_history = []

    for j in range(1,101):
        # Shuffle this using a random seed which will be consistent.
        random.Random(j).shuffle(game.deck.cards)
        game.playOneHand(verbose=True, update=False)
        game.deck.createNewFullDeck(shuffle=False)
        eval_history.append(game.player.currentMoney)

    return eval_history

    print(game.player.currentMoney)


