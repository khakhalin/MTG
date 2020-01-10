# Wrapper class for any neural-network bot

from .bot import *
from .load import collection_pack_to_x

class NeuralNetBot(Bot):
    
    def __init__(self, net, le):
        self.num_correct = 0
        self.num_total = 0
        self.net = net # Pre-trained neural net that ranks cards from one-hot encoded [collection, pack] vector
        self.le = le   # Pre-trained label-encoder mapping card names to numeric class labels
        
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
    
        Picks the rarest on-color card in each pack.
        """
        
        # Initializes pack ranking and separates pack from collection
        pack = draft_frame[0]
        collection = draft_frame[1]

        # Maps card names to one-hot encoding and gets nnet ranking
        x = collection_pack_to_x(collection, pack, self.le)
        pred = self.net(x)
        
        # Maps predictions to card names
        pack_rank = {str(self.le.inverse_transform([i])[0]) : float(v.detach().numpy()) for i, v in enumerate(pred[0,:]) if v > 0}
        
        return pack_rank