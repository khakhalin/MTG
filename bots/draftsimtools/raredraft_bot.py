from .bot import *


# --- Naive bot (drafts like a 5-years-old)
class RaredraftBot(Bot):
    
    def __init__(self, card_set):
        self.num_correct = 0
        self.num_total = 0
        self.card_set = card_set # a list with 'Name' column, containing card names and attributes
        
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
        pack_rank = {x:0 for x in draft_frame[0]}
        pack = draft_frame[0]
        collection = draft_frame[1]
        
        # Gets current color 
        color_stats = {'W':0, 'U':0, 'B':0, 'R':0, 'G':0}
        if (len(collection) > 0):
            collection_colors = self.card_set[self.card_set["Name"].isin(collection)]["Casting Cost 1"]
            collection_colors = list(color for color in collection_colors)
            for card_colors in collection_colors:
                for color in card_colors:
                    if color in color_stats:
                        color_stats[color] += 1
        current_color = max(color_stats, key = color_stats.get) 
        
        # Makes the pick based on rarity
        pack_rarity = self.card_set[self.card_set["Name"].isin(pack)]
        mythics = pack_rarity["Name"][pack_rarity.Rarity.str[0] == 'M'] # mythics
        for card in mythics:
            pack_rank[card] += 10
        rares = pack_rarity["Name"][pack_rarity.Rarity.str[0] == 'R'] # rares
        for card in rares:
            pack_rank[card] += 5
        uncommons = pack_rarity["Name"][pack_rarity.Rarity.str[0] == 'U'] # uncommons
        for card in uncommons:
            pack_rank[card] += 2
        on_color = list(current_color in color for color in pack_rarity["Casting Cost 1"]) # on-color bonus
        on_color = pack_rarity[on_color]["Name"]
        for card in on_color:
            pack_rank[card] += 1
        
        return pack_rank