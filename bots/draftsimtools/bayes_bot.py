# Wrapper class for any neural-network bot

from .bot import *
from .load import collection_pack_to_x
import pandas as pd
import numpy as np

class BayesBot(Bot):
    
    def __init__(self, le, pCollPath, pPackPath, pFullPath, namesPath):
        self.num_correct = 0
        self.num_total = 0
        self.le = le   # Pre-trained label-encoder mapping card names to numeric class labels

        # Reads in probability matrices and card names
        self.pColl = np.loadtxt(pCollPath, delimiter=",")
        self.pPack = np.loadtxt(pPackPath, delimiter=",")
        self.pF = np.loadtxt(pFullPath, delimiter=",")
        self.names = pd.read_csv(namesPath)

        print(self.names)

        # Sets constants
        minPEver = np.min(self.pColl[self.pColl>0])/2 # Even smaller than the smallest non-zero P observed
        self.pC = np.log(np.maximum(self.pColl,minPEver))-np.log(minPEver) # C from 'Collection'
        self.pP = np.log(np.maximum(self.pPack,minPEver))-np.log(minPEver) # P from 'Pack'
        
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

        # Maps card names to one-hot encoding
        x = collection_pack_to_x(collection, pack, self.le)
        x = np.transpose(x.numpy())
        collectionVector = x[:int(len(x) / 2)]
        packVector = x[int(len(x) / 2):]

        # Gets ratings from bot
        if collection == []: # First card
            ratings = np.matmul(self.pP, packVector) # Only ratings
        else:
            ratings = np.matmul(self.pC, collectionVector) # Only synergies
        ratings = ratings*(packVector > 0)
        
        # Maps ratings to card names
        pack_rank = {str(self.le.inverse_transform([i])[0]) : v for i, v in enumerate(ratings[:,0]) if v > 0}
        
        return pack_rank