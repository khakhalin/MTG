import random


class Bot(object):

    #Class CONSTANTS
    #None for base bots but yours should go here in ALL_CAPS

    def __init__(self):
        self.num_correct = 0
        self.num_total = 0


    def rank_pack(self, draft_frame):
        """
        INPUT: one draft frame in form [pack, collection], where the human pick is the first 
               card name in the pack
        OUTPUT: ranked list of pick preferences. E.g. for the pack ["cardA", "cardB", "cardC"], could
                return ["cardB":1, "cardA":0.2, "cardC":0] in decreasing order of preference
        NOTE: use list not tuple or dict for input
    
        This method is to be called by the testing script. Modify the get_choice method
        with the drafting logic of your bot's subclass.
        """
        pack_rank = self.__get_ranking(draft_frame)
        top_pick = self.get_top_pick(pack_rank)

        self.num_total += 1

        if top_pick == draft_frame[0][0]:
            self.num_correct += 1

        return pack_rank


    def __get_ranking(self, draft_frame):
        """
        INPUT: one draft frame in form [pack, collection], where the human pick is the first 
               card name in the pack
        OUTPUT: list of pick preferences in same order as input. E.g. for the pack 
                ["cardA", "cardB", "cardC"], could return ["cardA":0.2, "cardB":1, "cardC":0]
    
        This is where your bot logic should go. In your bot subclass, overwrite this function
        with your own evaluation method. INPUTS and OUTPUTS must be standard across all bots.
        """
        
        # Default logic implements a random choice of card
        pack_rank = {x:0 for x in draft_frame[0]}
        pack_rank[random.choice(list(pack_rank))] = 1
        
        return pack_rank

    def get_performance(self):
        """Return tuple of number of correct picks so far."""
        return self.num_total, self.num_correct
    
    def get_top_pick(self, pack_rank):
        """
        Returns the card name of the top-ranked pick within a pack.
        """
        return max(pack_rank, key = pack_rank.get)
    
    def clear_history(self):
        """Reset class variables."""
        self.num_correct = 0
        self.num_total = 0

