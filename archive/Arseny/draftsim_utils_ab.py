#import pandas as pd
#import numpy as np

#import csv
import re           # Regular expressions
#import itertools

def fixName(name):
    res = re.sub(' ', '_', name)
    res = re.sub(',_', '_', res)
    res = re.sub('_\d+', '', res) #remove _number from lands
    res = re.sub('_\([a-zA-Z]\)', '', res) #remove guildgate types
    res = res.lower()
    return res
	
	
def getName(card):
    s = '_'
    #names only occurs in split cards
    if card['layout'] == 'split':
        return s.join(
            [fixName(x) for x in card['names']]) #format split card names
    else: #else just use name
        return fixName(card['name'])
		
	
def isLegendary(card):
    return 'supertypes' in card.keys() and 'Legendary' in card['supertypes']
	
	
def getCardColor(card):
    colors = ['W', 'U', 'B', 'R', 'G'] # Unlike Bobby's original file, the color sequence is correct here
    pattern = "[W,U,B,R,G]"
    
    if 'manaCost' in card.keys():
        mana = re.findall(pattern, card['manaCost'])
        mana = list(set(mana)) #delete duplicates
        if len(mana) == 0:
            return 0
        elif len(mana) > 1:
            return 1
        else:
            return colors.index(mana[0]) + 2
        return mana
    
    #for colored land cards
    elif 'colorIdentity' in card.keys():
        mana = card['colorIdentity']
        if len(mana) == 0:
            return 0
        elif len(mana) > 1:
            return 1
        else:
            return colors.index(mana[0]) + 2
        return mana
    #colorless lands
    else:
        return 0
		
		
