import numpy as np
import pandas as pd
from operator import itemgetter
from copy import deepcopy

class BotTester(object):
    """The BotTester object is used to evaluate how close a collection of bot's picks match human picks.
    
    This can be used in the following manner:
        tester = BotTester(drafts)
        tester.evaluate_bots([bot], ["SGD"])
        tester.write_rating_dict()
    """
   
    def __init__(self, drafts):
        """Create a new BotTester instance.

        Fields:
          self.drafts - a collection of multiple draft objects (list of list of list of cardnames)
          self.correct - numpy array of all bot's correct choices compared to human picks
          self.fuzzy_correct - numpy array of all bot's correct choices (if human pick in top 3 bot picks)
        
        :param drafts: Attach a set of drafts to the BotTester
        """
        self.drafts = deepcopy(drafts)
        self.correct = pd.DataFrame(columns = ['draft_num', 'pick_num', 'human_pick'])
        self.fuzzy_correct = pd.DataFrame(columns = ['draft_num', 'pick_num', 'human_pick'])

        # Instantiates accuracy DataFrames with draft, pack and card info
        counter = 0
        for i in range(len(self.drafts)):
            draft = self.drafts[i]
            for j in range(len(draft)):
                pack = draft[j]
                self.correct.loc[counter] = [i + 1, j + 1, pack[0]]
                self.fuzzy_correct.loc[counter] = [i + 1, j + 1, pack[0]]
                counter = counter + 1

    def evaluate_bots(self, bots, bot_names):
        """Evaluates accuracy and fuzzy accuracy of a list of bots. 
        
        "Correct" is whether or not the bot's top choice matched the human's top choice.
        "Fuzzy correct" is whether or not the human's top choice was in the bot's top 3 choices.
        These values are stored the DataFrames acc and fuzz_acc for all bots.

        :param bots: List of bots that all inherit from "bot.py"
        :param bot_names: List of bot names (strings) of the same size as the list of bots.
        """

        temp_names = []
        for i in range(len(bots)):
            bot = bots[i]
            all_correct = []
            all_fuzzy = []
            for j in range(len(self.drafts)):
                bot.new_draft(self.drafts[i])
                for pack in bot.draft:
                    rating_list = bot.create_rating_list(pack)
                    exact_correct = self.is_bot_correct(pack, rating_list)
                    fuzzy_correct = self.is_bot_correct(pack, rating_list, fuzzy = True)
                    all_correct.append(exact_correct[1])
                    all_fuzzy.append(fuzzy_correct[1])
            bot_name = bot_names[i]
            self.correct[bot_name] = all_correct
            self.fuzzy_correct[bot_name] = all_fuzzy

    def write_rating_dict(self, exact_filename = "exact_correct.tsv", fuzzy_filename = "fuzzy_correct.tsv"):
        """Writes the correctness DataFrames to filenames.
        """
        self.correct.to_csv(exact_filename, sep = "\t", index = False)
        print("Wrote correct to: " + str(exact_filename))
        self.fuzzy_correct.to_csv(fuzzy_filename, sep = "\t", index = False)
        print("Wrote fuzzy_correct to: " + str(fuzzy_filename))
    
    def is_bot_correct(self, pack, rating_list, fuzzy = False):
        """ Checks whether or not a bot's pick matches a human's pick.
        
        Returns a tuple of (cardname, bot_correct) for whether or not the
        bot's top choice matched the user's choice. If fuzzy = True, then
        instead the bot is correct if the user's choice is in bot's top 3
        """
        bot_correct = 0
        rating_list = sorted(rating_list, key = itemgetter(1), reverse = True)
        if not fuzzy:
            bot_pick = rating_list[0]
            if pack[0] == bot_pick[0]:
                bot_correct = 1
        elif fuzzy:
            for i in range(min(len(rating_list), 3)):
                bot_pick = rating_list[i]
                if pack[0] == bot_pick[0]:
                    bot_correct = 1
        return (pack[0], bot_correct)

