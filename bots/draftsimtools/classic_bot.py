from .bot import *
from .load import *
import numpy as np


# --- Draftsim classic bot (except for the hybrid cost logic)

class ClassicBot(Bot):    
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
    
    def __init__(self, card_set):
        self.num_correct = 0
        self.num_total = 0
        self.card_set = card_set # a list with 'Name' column, containing card names and attributes
        
        self.color_commitment = [0,0,0,0,0]
        self.eval_pack = []
        
        # self.card_set = create_set(setRatingPath, landRatingPath)
        # self.card_set['Name'] = self.card_set.Name.str.replace(',','')
        self.card_set = self.card_set.set_index('Name')
        #print(self.card_set.to_string())
        '''Structure:  
        Name: Death_Baron
        Casting Cost 1: 1BB
        Casting Cost 2: either 'none', or something like 'B'
        Card Type: 'Creature', 'spell' etc
        Rarity: M,R,U,C
        Rating: draftsim rating from -1 for lands, and up to 5 or something
        Color Vector: something like [0, 0, 1, 1, 1]  or [0, 0, 2, 0, 0]'''
        
    def rank_pack(self, draft_frame):
        pack_rank = self.__get_ranking(draft_frame)
        top_pick = self.get_top_pick(pack_rank)
        self.num_total += 1
        if top_pick == draft_frame[0][0]:
            self.num_correct += 1
        return pack_rank
        
    def __get_ranking(self, draft_frame):
        pack = draft_frame[0]
        collection = draft_frame[1] 
        color_commit = self.get_color_commitment(collection)
        evaluated_pack = [self.get_color_bias(card, color_commit) + 
                          float(self.card_set.loc[card]['Rating']) for card in pack]
        self.eval_pack = evaluated_pack              
        return {draft_frame[0][i]:evaluated_pack[i] for i in range(len(pack))}
    
    def get_color_commitment(self, collection):
        temp_color_commitment = [0,0,0,0,0]
        for card in collection:
            new_card = self.get_card_colors(card)
            # pythonic vector addition
            temp_color_commitment = list(map(sum, zip(new_card, temp_color_commitment)))
        return temp_color_commitment
    
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
                #if self.COLORS[i] in card_cost:
                if card_colors[i]>0:
                    bias += commitment[i]
                else:
                    bias -= commitment[i]
            return bias - self.MULTICOLOR_PENALTY

        # 1 color cards
        elif num_card_colors == 1:
            # --- AKh: I'm just commenting all hybrid stuff for now, as I cannot troubleshoot it on this set
            '''hybrid = self.is_hybrid(card)  # boolean does this card have hybrid mana symbols?'''
            # Note that the commit_argsorted is ASCENDING
            commit_argsorted = np.argsort(commitment)  # an list of the players color commitments

            # The hybrid case
            '''if hybrid:
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

                return bias'''

            # get the index of which color the card is
            # should be the max of the card colors if its the only non-zero entry
            #color_index = card_colors.index(max(card_colors))  # index of the card's color
            color_index = np.argmax(card_colors)

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
        
    def get_card_colors(self, card):
        try:
            temp = self.card_set.loc[card]['Color Vector']
        except:
            print("Unexpected card:",card," Assuming no color identity")
            temp = [0,0,0,0,0]
        return temp
    
    def get_card_cost(self, card):
        return np.sum(self.card_set.loc[card]['Color Vector'])