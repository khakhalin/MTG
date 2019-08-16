from .bot import *

from csv import reader
import re
from numpy import argsort


# Classic Draftsim logic, based on manual ratings

class oops(Bot):

    '''Class Constants'''
    PACK_SIZE = 15
    RATING_THRESHOLD = 2.0
    COLOR_COMMIT_THRESHOLD = 3.5
    TIME_TO_COMMIT = 1*PACK_SIZE+3
    MAX_BONUS_SPEC = 0.9
    ON_COLOR_BONUS = 2.0
    OFF_COLOR_PENALTY = 1.0
    SINGLE_COLOR_BIAS_FACTOR = 2.0
    SECOND_COLOR_FRACTION = 0.8
    MULTICOLOR_PENALTY = 0.6
    COLORS = ['W', 'U', 'B', 'R', 'G']
    HYBRID = {'A' : 'WB', 'D' : 'UB', 'M' : 'UG', 'L' : 'RG', 'I' : 'BG',
              'V' : 'WB', 'S' : 'WR', 'Z' : 'UR', 'Y' : 'WG', 'K' : 'BR'}
              
    def __init__(self, card_csv="Draftsim Ratings - GRN.csv", other_csv='Draftsim Ratings - GRN_land.csv'):
        Bot.__init__(self)

        self.card_set = self.get_card_dict(card_csv, other_csv)

        self.color_commitment = [0,0,0,0,0]
        self.eval_pack = []

    def get_choice(self, draft_frame):
        collection = draft_frame[0]
        pack = draft_frame[1]
        pick = draft_frame[2]

        evaluated_pack = [self.get_color_bias(card, self.get_color_commitment(collection)) + float(self.card_set[card]['rating']) for card in pack]
        self.eval_pack = evaluated_pack
        return argsort(evaluated_pack)

    # Input: card string name, array of color commitment to each color
    # output: float color bias
    # Note: must be run after calculating color commitment from collection
    # In the original code there was a lot of self.COLOR_COMMIT_THRESH/denom but I think thats just self.MAX_SPEC_BONUS
    def get_color_bias(self, card, commitment):
        card_colors = self.get_card_colors(card)
        num_card_colors = sum([1 if symbol != 0 else 0 for symbol in card_colors])
        num_commit_colors = sum([1 if symbol >= self.COLOR_COMMIT_THRESHOLD else 0 for symbol in commitment])

        denom = self.COLOR_COMMIT_THRESHOLD / self.MAX_BONUS_SPEC

        card_cost = self.get_card_cost(card)

        # 4-5 color cards get no bonus
        if num_card_colors > 3:
            return 0

        # 0 color cards
        elif num_card_colors == 0:
            # no bonus when the player has cards of only one color
            if num_commit_colors <= 1:
                return 0
            # min of max bonus or largest commitment/denom
            # originally the first option was the threshold over the denom but that should just be the max bonus
            else:
                return min(self.MAX_BONUS_SPEC, max(commitment) / denom)

        # 2-3 color cards
        elif num_card_colors in [2, 3]:
            bias = 0
            # loop through colors
            for i in range(len(commitment)):
                if self.COLORS[i] in card_cost:
                    bias += commitment[i]
                else:
                    bias -= commitment[i]
            return bias - self.MULTICOLOR_PENALTY

        # 1 color cards
        elif num_card_colors == 1:

            hybrid = self.is_hybrid(card)  # boolean does this card have hybrid mana symbols?

            # Note that the commit_argsorted is ASCENDING
            commit_argsorted = argsort(commitment)  # an list of the players color commitments

            # The hybrid case
            # Maybe this should actually be first?

            # TODO: Hybrid Mana Case

            # this one is kind of complicated. Might need to rework some of the variables from the other cases.
            # This needs to be reworked and moved to a different case.
            # The problem here is the way that we are tracking the number of colors in a card.
            # A hybrid card will get two colors in num_card_colors
            # drafting.js has only three cases for the hybrid cards: the player has only cards of one color
            # or the the player is committed to one color and neither of the card's colors are that color
            # the general case is just the highest bias among all colors that the card is in

            if hybrid:
                # this seems wrong. Can't tell what hybrid_color_index is
                bias = 0

                # set bias to highest bias among biases of colors in card
                for i in range(len(card_colors)):
                    if card_colors[i] != 0:
                        bias = max(bias, min(self.MAX_BONUS_SPEC, commitment[i] / denom))

                # the player is committed to only one color.
                if num_commit_colors == 1:
                    bias /= self.SINGLE_COLOR_BIAS_FACTOR
                # If the the player is committed to one color, and neither of the hybrid colors are that color
                if num_commit_colors == 1:
                    for i in range(len(card_colors)):
                        if card_colors[i] != 0 and i == commit_argsorted[-1]:
                            bias = max(self.SECOND_COLOR_FRACTION * self.MAX_BONUS_SPEC, bias)

                return bias

            # get the index of which color the card is
            # should be the max of the card colors if its the only non-zero entry
            color_index = card_colors.index(max(card_colors))  # index of the card's color

            # base bias
            bias = min(self.MAX_BONUS_SPEC, commitment[color_index] / denom)

            # the player is committed to no colors Case 2a in original code
            if num_commit_colors == 0:
                return bias

            # if player only has cards of one color
            if sum([1 if count != 0 else 0 for count in commitment]) == 1:
                bias /= self.SINGLE_COLOR_BIAS_FACTOR

            # if player is committed to only one color
            # and this card is of the second highest color in commitment
            # give it a slight bonus

            if num_commit_colors == 1 and color_index == commit_argsorted[-2]:
                bias = max(self.SECOND_COLOR_FRACTION * self.COLOR_COMMIT_THRESHOLD / denom, bias)

            return bias

    # Input: collection from dataset. Should be a list of card names
    # Output: array of number of mana symbols of each type shape 5,1
    def get_color_commitment(self, collection):
        temp_color_commitment = [0,0,0,0,0]

        for card in collection:
            new_card = self.get_card_colors(card)
            # pythonic vector addition
            temp_color_commitment = list(map(sum, zip(new_card, temp_color_commitment)))
        return temp_color_commitment

    def on_color(self, card):
        # TODO: write helper function
        # take in card string name
        # return boolean for on color or not
        pass

    # INPUT: Card name string
    # OUTPUT: Array with number of mana symbols of each type
    def get_card_colors(self, card):
        temp_colors = [0,0,0,0,0]
        cost = self.get_card_cost(card)

        # loop through characters in the manacost
        for char in cost:
            if char in self.COLORS:
                temp_colors[self.COLORS.index(char)] += 1

        return temp_colors

    # Helper function to get card costs
    # Input: card name string
    # Output: string of all costs with hybrid costs converted
    def get_card_cost(self, card):
        cost = self.card_set[card]['cost']
        if self.card_set[card]['cost2'] != 'none':
            cost += self.card_set[card]['cost2']

        for i in range(len(cost)):
            if cost[i] in self.HYBRID:
                cost += self.HYBRID[cost[i]]
                cost = cost[:i] + cost[i+1:]
        return cost

    # Input: card string name
    # Output: Boolean
    def is_hybrid(self, card):
        for char in self.card_set[card]['cost']:
            if char in self.HYBRID:
                return True
            else:
                continue
        if self.card_set[card]['cost2'] != 'none':
            for char in self.card_set[card]['cost2']:
                if char in self.HYBRID:
                    return True
                else:
                    continue
        return False

    @staticmethod
    def get_card_dict(file_name, other_file = 'none'):
        card_dict = {}
        with open(file_name, 'r') as f:
            r = reader(f)
            for row in r:
                card_dict[re.sub(',_', '_', row[0])] = {
                    'cost' : row[1],
                    'cost2' : row[2],
                    'rarity' : row[4],
                    'rating' : row[5]
                }
        if other_file != 'none':
            with open(other_file, 'r') as f:
                r = reader(f)
                for row in r:
                    card_dict[re.sub(',_', '_', row[0])] = {
                        'cost': row[1],
                        'cost2': row[2],
                        'rarity': row[4],
                        'rating': row[5]
                    }

        return card_dict


