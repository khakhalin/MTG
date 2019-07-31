"""
  draftsimtools.load
  ~~~~~~~~~~~~~~~~~~

  Utilities for loading draftsim set and draft files.
"""

import re

import pandas as pd

def create_set(path1, path2=None):
    """Load set data from the draftsim ratings google doc.

    On the google doc, the ratings for the set should be exported as a tsv. 

    For reference, the draftsim ratings doc is currently here:
    https://docs.google.com/spreadsheets/d/1umtr9q6gg_5BGAWB0n-468RP5h4gcaFg98tW52GXrFE/edit#gid=1763784039

    :param path1: Path a set spreadsheet saved as tsv.

    :param path2: (Optional) Path to supporting set spreadsheet saved as tsv.

    :return: A pandas dataframe containing set information. 
    """
    rd = pd.read_csv(path1, delimiter="\t")
  
    #If provided, load data from supplementary file. 
    if path2 is not None:
        rd = rd.append(pd.read_csv(path2, delimiter="\t"))
        rd = rd.reset_index(drop=True)
        
    #Add color information to dataframe.
    add_color_vec(rd)
    
    return rd

def add_color_vec(rd):
    """Add color information to set dataframe.
    
    Creates a 'Color Vector' column with contains the number of WUBRG mana 
    symbols in each card. 

    The values of the 'Color Vector' typically come from 'Casting Cost 1'.
    However, if the value of 'Casting Cost 2' is greater for a certain color,
    the average of the two (cc1+cc2)/2 is used. 

    :param rd: Set dataframe.

    :return: Set dataframe with 'Color Vector' column added.

    """
    
    #Extract mana cost columns.
    cc1_col = rd["Casting Cost 1"]
    cc2_col = rd["Casting Cost 2"]
    
    #Create color vector for each card.
    color_vec_list = []
    for (cc1, cc2) in zip(cc1_col, cc2_col):        
        cv1 = get_color_vec(cc1)
        cv2 = get_color_vec(cc2)
        
        #Append new card information to color vector.
        cv = []
        for ci in range(5):
            if cv1[ci] >= cv2[ci]:
                cv.append(cv1[ci])
            else:
                cv.append((cv1[ci] + cv2[ci])/2.0)
        color_vec_list.append(cv)
        
    #Add to dataframe.
    rd["Color Vector"] = pd.Series(color_vec_list).values
    return

def get_color_vec(cs):
    """Converts a color string to a color vector.

    The color vector counts the number of mana symbols in the cost. 
    W or w corresponds to [1,0,0,0,0]
    U or u corresponds to [0,1,0,0,0]
    B or b corresponds to [0,0,1,0,0]
    R or r corresponds to [0,0,0,1,0]
    G or g corresponds to [0,0,0,0,1]

    Numeric/colorless symbols are ignored.

    Some other characters are supported for multi/hybrid costs.
    
    :param cs: String containing colored mana symbols.
    
    :return: Color vector with WUBRG components.
    """
    #Handle colorless case.
    cv = [0,0,0,0,0]
    if isinstance(cs, int):
        return cv
    
    #Group characters into WUBRG. Other characters for legacy compatibility.
    for letter in cs:
        if letter in "WwAaVvSsYy":
            cv[0] += 1
        if letter in "UuAaDdMmZz":
            cv[1] += 1
        if letter in "BbDdIiVvKk":
            cv[2] += 1
        if letter in "RrLlSsZzKk":
            cv[3] += 1
        if letter in "GgMmIiYyLl":
            cv[4] += 1
    return cv

def load_drafts(draft_path):
    """Load drafts in the provided csv file.

    The data is stored in a single string. The newline character '\n' 
    separates unique drafts. 

    Each draft consists of a draft number, followed by the set string, 
    followed by a list of cards in the 24 packs in the draft. 
 
    :param draft_path: Path to draft csv data file from database.

    :return: Raw drafts string.
    """
    with open(draft_path) as f:
        drafts = f.read()

    #Remove problematic quote an 

    return drafts

def fix_commas(set_var, drafts):
    """Removes commas and quotes from cardnames in set and draft variables.

    This is used to prevent issues with character conflicts.

    :param set_var: Set variable with problematic characters.
    
    :param drafts: Draft data variable with problematic characters.

    :return set_var: Set variable with problematic characters removed.

    :return drafts: Draft data variable with problematic characters removed.
    """
    
    #Remove quote characters from draft.
    drafts = re.sub('"', '', drafts)
    
    #Identify names with commas.
    comma_names = []
    for name in set_var["Name"]:
        if "," in name:
            comma_names.append(name)
    
    #Remove commas from drafts.
    for name in comma_names:
        fixed_name = re.sub(",", "", name)
        drafts = re.sub(name, fixed_name, drafts)
        
    #Remove commas from set variable.
    set_var["Name"] = [re.sub(",", "", name) for name in set_var["Name"]]
    return set_var, drafts

def sort_draft(single_draft):
    """Given a single draft string, process that string into a list of picks.

    :param single_draft: A list of unsorted draft tokens from database.

    :return: A list of picks of length 3*ps. Each pick is a list of cardnames 
             in the pack shown to the user. The card picked by the user is 
             always the top card.
    """

    #Extract picks from draft.
    picks = single_draft[2:]  # PICKS is all drafted cards in a row, first human pile, then all bots; 3*ps cards in each pile
    pick_list = []
    
    #Get the pack size. 
    ps = int(len(picks) / 24) # 24=8*3: 8 players, 3 packs. PICKS is 3*8*packsize (ps) long.

    #Track all picks in pack 1.
    for pick in range(ps):                                # For each card in the final pile, reconstruct the hand.
        cur_pick = []                                     # A hand player was starting at, while picking PICKth card.
        for x in range(pick, (3*ps+1)*(ps-pick), 3*ps+1): # Step size: 3ps to move to next player + 1 to get next card
                                                          # If player2 drafted card at step2, player1 saw it at step1 etc.
            x = x % (24*ps)                               # Cheat to avoid manual wrapping up after 8th pick.
            cur_pick.append(picks[x])                     # Populate the hand
        pick_list.append(cur_pick)                        # Save the hand
    
    #Track all picks in pack 2.
    for pick in range(ps):
        cur_pick = []
        for x in range(ps+pick, (-3*ps+1)*(ps-1-pick), -3*ps+1): # Same, but opposite direction, and PS deep in each pile
            x = x % (24*ps)
            cur_pick.append(picks[x])
        pick_list.append(cur_pick)

    #Track all picks in pack 3.
    for pick in range(ps):
        cur_pick = []
        for x in range(2*ps+pick, (3*ps+1)*(ps-pick), 3*ps+1):   # Again positive direction, 2*PS deep in the pile
            x = x % (24*ps)
            cur_pick.append(picks[x])            
        pick_list.append(cur_pick)        
    return pick_list

def process_drafts(drafts, print_every=10000):
    """Process a raw multi-draft string into a list of sorted drafts.

    :param drafts: Raw string from draft database containing multiple drafts.

    :param print_every: (Optional) Print an update every this many drafts.

    :return: List of sorted drafts.
    """
 
    #Store each draft as a string.
    string_drafts = drafts.split("\n")
    
    #Store each draft as an unsorted list.
    unsorted_drafts = []
    for d in string_drafts:
        unsorted_drafts.append(d.split(","))
        
    #Create pick lists when possible.
    sorted_drafts = []
    for num, u in enumerate(unsorted_drafts):
        if num % print_every == 0:
            print("Processing draft: " + str(num) + ".")
        try:
            sorted_drafts.append(sort_draft(u))
        except:
            pass
    return sorted_drafts

def create_rating_dict(set_df):
    """Creates a rating dictionary for efficient rating updates. 

    :param set_df: Dataframe for a single set.
    
    :return: Returns a rating dictionary. The keys in the dictionary are 
             cardnames (strings). The value corresponding to each key is a 
             list of length two. The first element of the list is the 'Color
             Vector' for the card. The second element is the rating for the 
             card. The rating is allowed to change during optimization.
    """
    rating_dict = {}
    for index, row in set_df.iterrows():
        rating_dict[row["Name"]] = [row["Color Vector"], row["Rating"]]
    return rating_dict


