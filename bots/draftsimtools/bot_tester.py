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
          self.correct - DataFrame of all bots' correct choices compared to human picks
          self.fuzzy_correct - DataFrame of all bots' correct choices (if human pick in top 3 bot picks)
          self.card_acc - DataFrame of per-card accuracy metrics for all bots
        
        :param drafts: Attach a set of drafts to the BotTester
        """
        self.drafts = deepcopy(drafts)
        self.correct = pd.DataFrame(columns = ['draft_num', 'pick_num', 'human_pick'])
        self.fuzzy_correct = pd.DataFrame(columns = ['draft_num', 'pick_num', 'human_pick'])
        self.card_acc = pd.DataFrame(columns = ['human_pick'])

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

        # Fills in dataframes of correct choices
        temp_names = []
        for i in range(len(bots)): # AKh: better to rename to iBot
            bot = bots[i]
            all_correct = []
            all_fuzzy = []
            for j in range(len(self.drafts)):
                bot.new_draft(self.drafts[j])
                for pack in bot.draft:        # AKh: bot.draft is deepcopied from new_draft arg; why use it here?
                    rating_list = bot.create_rating_list(pack)
                    exact_correct = self.is_bot_correct(pack, rating_list)
                    fuzzy_correct = self.is_bot_correct(pack, rating_list, fuzzy = True)
                    all_correct.append(exact_correct[1])
                    all_fuzzy.append(fuzzy_correct[1])
            bot_name = bot_names[i]
            self.correct[bot_name] = all_correct
            self.fuzzy_correct[bot_name] = all_fuzzy

        # Fills in dataframes of per-card accuracies
        unique_cards = np.sort(self.correct['human_pick'].unique())
        self.card_acc['human_pick'] = unique_cards # Actually all card names; human_pick is just where they came from
        for bot_name in bot_names:
            accuracies = []
            for human_pick in unique_cards:
                all_picks = self.correct.loc[self.correct['human_pick'] == human_pick]
                accuracies.append(all_picks[bot_name].sum() / all_picks.shape[0])
            self.card_acc[bot_name] = accuracies

    def write_evaluations(self, exact_filename = "exact_correct.tsv", fuzzy_filename = "fuzzy_correct.tsv", acc_filename = "card_accuracies.tsv"):
        """Writes correctness and accuracy DataFrames to filenames.
        """
        self.correct.to_csv(exact_filename, sep = "\t", index = False)
        print("Wrote correct to: " + str(exact_filename))
        self.fuzzy_correct.to_csv(fuzzy_filename, sep = "\t", index = False)
        print("Wrote fuzzy_correct to: " + str(fuzzy_filename))
        self.card_acc.to_csv(acc_filename, sep = "\t", index = False)
        print("Wrote card_acc to: " + str(acc_filename))
    
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

