"""
  draftsimtools.bots
  ~~~~~~~~~~~~~~~~~~

  Machine learning based bot logic.
"""

from random import shuffle
from copy import deepcopy

import pandas as pd

class Bot(object):
    """The bot object is used to simulate drafts. It has functions for creating new drafts, 
    making picks, and tracking it's color commit. 
    
    A draft can be simulated in the following manner:
        p = Bot()
        p.new_draft(drafts[0])
        for x in range(45):
            p.make_pick()
    """
    
    #Some constants from the website.    
    COLOR_COMMIT_THRESHOLD=3.5  #Determines how many good cards are needed to commit to a color
    RATING_THRESH=2.0  #Baseline playability rating for color_commit
    MAX_BONUS_SPEC=.9  #The maximum bonus during the speculation phase at the start of a draft
    ON_COLOR_BONUS=2.0 #Bonus cards receive after player locks into 2 colors
    OFF_COLOR_PENALTY=1.0 #Penalty for off color cards after the player locks into 2 colors
    SECOND_COLOR_FRAC=0.8 #When committed to one color, the second color bonus is this fraction of the on color bonus
    MULTICOLOR_PENALTY=0.6 #P1P1 penalty for multicolored cards 
    SING_COLOR_BIAS_FACTOR=2.0 #If the player only has cards of 1 color, reduce the bonus by this fraction
   
    def __init__(self, rating_dict, draft=None):
        """Create a new Bot instance. Bots should be restricted to a single set.
        
        :param rating_dict: Rating dictionary for the set being drafted.
        :param draft: (Optional) Attach a draft to the bot. 
        """
        self.rating_dict = rating_dict
        self.draft_count = 0
        self.loss_current = 0
        self.loss_history = []
        if draft is not None:
            self.new_draft(draft)
    
    def new_draft(self, draft):
        """Update the Bot object with a single new draft. New drafts can be created by
        draftsimtools.process_drafts. 
        
        Calling new_draft resets all information in the Bot object and allows numerous drafts
        to be simulated using a single Bot object. 
        
        Fields:
          self.draft - a single draft object (list of list of cardnames)
          self.collection - a list of cardnames currently picked
          self.color_commit - the color_commit vector of the current collection
          self.num_colors - number of colors bot is commited to
          self.ps - number of cards in a pack
          
        :param draft: Attach a draft to the bot. 
        """
        self.draft = deepcopy(draft)
        self.collection = []
        self.color_bonus = [0,0,0,0,0]
        self.color_commit = [0,0,0,0,0]
        self.num_colors = 0
        self.ps = int(len(self.draft)/3)
        
        self.draft_count += 1
    
    def make_pick(self):
        """Makes a pick and updates the bot's collection and color_commit. 
        
        This method picks the first card in each pack. Note that the draft lists are set up 
        such that the first element of each list is the card that was picked by a human. 
        """
        cur_pick = len(self.collection)
        if cur_pick < len(self.draft):
            self.collection.append(self.draft[cur_pick][0])
            self.update_color_commit(self.draft[cur_pick][0])
            self.update_num_colors()
            self.update_color_bonus()
        else:
            print("All picks made.")
    
    def update_color_commit(self, card):
        """Updates the color_commit of the bot.
        
        :param card: Card name (string).
        """
        #Collect card info.
        card_color_vector = self.rating_dict[card][0]
        card_rating = self.rating_dict[card][1]
        
        #Update each component of color_commit.
        for i in range(len(self.color_commit)):
            if card_color_vector[i] > 0:
                self.color_commit[i] += max(0, card_rating-self.RATING_THRESH)
    
    def update_num_colors(self):
        """Update number of committed colors for the bot.
        """
        #Update committed colors from color_commit.
        temp_num_colors = 0
        for c in self.color_commit:
            if c > self.COLOR_COMMIT_THRESHOLD:
                temp_num_colors += 1
        
        #Update committed colors based on pick number.
        if len(self.collection) >= (self.ps+5):
            temp_num_colors = 2
            
        #Final update.
        self.num_colors = min(temp_num_colors, 2)
        
    def update_color_bonus(self):
        """Updates color bonuses during speculation phase (0-0.9).
        
        Additional modifiers are applied in get_color_bias().
        """
        #Compute color bonus.
        temp_color_bonus = []
        for i in range(len(self.color_commit)):
            cur_bonus = self.color_commit[i] * self.MAX_BONUS_SPEC/self.COLOR_COMMIT_THRESHOLD 
            temp_color_bonus.append(min(cur_bonus, self.MAX_BONUS_SPEC))
        
        #Update color bonus.
        self.color_bonus = temp_color_bonus
                
    def get_color_bias(self, card):
        """Returns the color bias for a given card.
        """
        
        #Get card information.
        card_color_vector = self.rating_dict[card][0]
        num_card_colors = sum([c>0 for c in card_color_vector])
                
        #Uncastable card.
        if num_card_colors >= 4:
            return 0
        
        #print("card", str(card))
        #print("card_color_vector", str(card))
        #print("color_commit", self.color_commit)
        
        #Speculation phase - bot committed to 0-1 colors.
        if self.num_colors == 0 or self.num_colors == 1:
            
            #Colorless card.
            if num_card_colors == 0:
                
                #Reduce bonus when only 1 color is picked.
                picked_colors = sum([x>0 for x in self.color_commit])
                if picked_colors == 1:
                    return max(self.color_bonus) / self.SING_COLOR_BIAS_FACTOR
                else:
                    return max(self.color_bonus)
            
            #Mono colored.
            elif num_card_colors == 1:
                
                #When commited to one color, mono colored cards in the support color get a bonus.
                second_color_commit = sorted(self.color_commit)[-2]
                second_color_index = self.color_commit.index(second_color_commit)
                                
                if self.num_colors == 1 and card_color_vector[second_color_index]>0:
                    
                    #As implemented in draftsim code. Maybe a good idea to use lower bound instead.
                    return self.SING_COLOR_BIAS_FACTOR * self.SECOND_COLOR_FRAC
                
                else:
                    
                    #Reduce bonus when only 1 color is picked.
                    picked_colors = sum([x>0 for x in self.color_commit])
                    cur_bonus = self.color_bonus[card_color_vector.index(max(card_color_vector))]
                    if picked_colors == 1:
                        return cur_bonus / self.SING_COLOR_BIAS_FACTOR
                    else:
                        return cur_bonus
                            
            #Multi colored.
            elif num_card_colors == 2 or num_card_colors == 3:
                
                #Base multicolored penalty.
                cur_bonus = -1 * self.MULTICOLOR_PENALTY
                
                #Reward on-color cards.
                for c in range(5):
                    if card_color_vector[c] > 0:
                        cur_bonus += self.color_bonus[c]
                    else:
                        cur_bonus -= self.color_bonus[c]
                return cur_bonus
            
        #Committed phase - bot committed to two colors.
        elif self.num_colors == 2:
            
            #Compute committed colors.
            color1 = self.color_commit.index(sorted(self.color_commit)[-1])
            color2 = self.color_commit.index(sorted(self.color_commit)[-2])
                        
            #Count off-color mana symbols.
            off_color_mana_symbols = 0
            for c in range(5):
                if c != color1 and c != color2:
                    off_color_mana_symbols += card_color_vector[c]
            
            #Return color bias.
            if off_color_mana_symbols == 0:
                return self.ON_COLOR_BONUS
            else:
                return 1 - off_color_mana_symbols*self.OFF_COLOR_PENALTY
            
        #Catch-all.
        #Broken.
        print("Unable to compute color bias for: " + str(card) + ", draft_count: " + str(self.draft_count))
        print("self.num_colors", self.num_colors)
        return 0
    
    def create_rating_list(self, pack):
        """Creates a relative rating list from a pack.
        """
        
        #Create list of updates. 
        rating_list = []
        for cardname in pack:
                    
            #Compute rating.
            base_rating = self.rating_dict[cardname][1]
            color_bonus = self.get_color_bias(cardname)
            total_rating = base_rating + color_bonus
                    
            #Compute rating difference. Positive means better than picked card.
            if len(rating_list) == 0:
                picked_rating = total_rating
                rating_difference = 0
            else:
                rating_difference = total_rating - picked_rating
                        
            #Create relative list of ratings.
            rating_list.append([cardname, rating_difference])
            
        return rating_list        

    def write_rating_dict(self, filename = "test.tsv"):
        """Writes the rating dict to filename.
        """
    
        #Create name/rating dictionary.
        name_rating = {}
        for k in self.rating_dict.keys():
            name_rating[k] = self.rating_dict[k][1]
    
        #Create data frame.
        rating_df = pd.DataFrame.from_dict(name_rating, orient="index")
        rating_df = rating_df.sort_values(0, ascending=False)
    
        #Save to file and return.
        rating_df.to_csv(filename, sep = "\t")
        print("Wrote rating_dict to: " + str(filename))
        #return rating_df
    
    def write_error(self, filename = "errors.csv"):
        """Writes loss_history to file.
        """
        f = open(filename, "w")
        for c in self.loss_history:
            f.write(str(c) + ", ")
        f.close()
