
import os
import re
import json
import csv
from random import randint

import numpy as np
import pandas as pd

from src import henry_utils as utils

class Deck:
    def __init__(self):
        pass

    def update_values(self, num_good_lands, num_lands, n):
        self.num_good_lands = num_good_lands    # Total number of lands with desired color in deck
        self.num_lands = num_lands              # Total number of lands in the deck
        self.n = n                              # Total number of cards in the deck

    def draw_card(self):

        # Instantiates variables
        card = randint(0, self.n)+1
        card_type = 0
        good_land_cutoff = self.num_good_lands
        land_cutoff = self.num_lands

        # If the card is a land that gives the desired color...
        if card <= good_land_cutoff:        
            card_type = 1
            self.num_good_lands -= 1
            self.num_lands -= 1
            self.n -= 1
        # If the card is a land that does not give the desired color...
        elif card <= land_cutoff:
            card_type = 2
            self.num_lands -= 1
            self.n -= 1
        # If the card is anything else...
        elif card > land_cutoff:
            card_type = 3
            self.n -= 1
        return card_type

# Calculates number of successful games for a fixed number of desired mana sources.
# num_iter = number of iterations to run simulation for
# cost = number of colored sources required for the given card
# turn = desired turn to be able to cast card by
# n = number of cards in the deck
# num_lands = total number of lands in the deck
def simulate_games(num_iter, cost, turn, n, num_lands, num_good_lands):

    count_ok = 0            # Number of games where we cast the card on the target turn
    count_conditional = 0   # Number of games where we hit enough lands, but not the right colors

    # Instantiates variables
    deck = Deck()
    card_type = 0
    lands_in_hand = 0
    good_lands_in_hand = 0
    starting_hand_size = 0
    mulligan = False
    good_land_on_top = False

    # Runs simulation a given number of times
    for i in range(num_iter):

        # Draws opening hand
        deck.update_values(num_good_lands, num_lands, n)
        lands_in_hand = 0
        good_lands_in_hand = 0
        for j in range(7):
            card_type = deck.draw_card()
            if card_type < 3:
                lands_in_hand += 1
            if card_type == 1:
                good_lands_in_hand += 1
        starting_hand_size = 7
        mulligan = False
        if lands_in_hand < 2 or lands_in_hand > 5:
            mulligan = True

        # Mulligans to 6
        if mulligan:
            deck.update_values(num_good_lands, num_lands, n)
            lands_in_hand = 0
            good_lands_in_hand = 0
            for j in range(6):
                card_type = deck.draw_card()
                if card_type < 3: 
                    lands_in_hand += 1
                if card_type == 1: 
                    good_lands_in_hand += 1
            starting_hand_size = 6
            mulligan = False
            if lands_in_hand < 2 or lands_in_hand > 4:
                mulligan = True

        # Mulligans to 5
        if mulligan:
            deck.update_values(num_good_lands, num_lands, n)
            lands_in_hand = 0
            good_lands_in_hand = 0
            for j in range(5):
                card_type = deck.draw_card()
                if card_type < 3: 
                    lands_in_hand += 1
                if card_type == 1: 
                    good_lands_in_hand += 1
            starting_hand_size = 5
            mulligan = False
            if lands_in_hand < 1 or lands_in_hand > 4:
                mulligan = True

        # Mulligans to 4
        if mulligan:
            deck.update_values(num_good_lands, num_lands, n)
            lands_in_hand = 0
            good_lands_in_hand = 0
            for j in range(4):
                card_type = deck.draw_card()
                if card_type < 3: 
                    lands_in_hand += 1
                if card_type == 1: 
                    good_lands_in_hand += 1
            starting_hand_size = 4

        # Draws a card for turn 2.
        # Handles Vancouver mulligan by leaving any land that can produce the right color on top.
        good_land_on_top = False
        if starting_hand_size < 7:
            card_type = deck.draw_card()
            if card_type == 1:
                good_land_on_top = True
        if turn > 1:
            if good_land_on_top:
                good_lands_in_hand += 1
                lands_in_hand += 1
            else:
                card_type = deck.draw_card()
                if card_type < 3:
                    lands_in_hand += 1
                if card_type == 1:
                    good_lands_in_hand += 1

        # Draws cards until the target turn
        for current_turn in range(3, turn):
            card_type = deck.draw_card()
            if card_type < 3:
                lands_in_hand += 1
            if card_type == 1:
                good_lands_in_hand += 1
            
        # Calculates result
        if good_lands_in_hand >= cost and lands_in_hand >= turn:
            count_ok += 1
        if lands_in_hand >= turn:
            count_conditional += 1

    # Returns tuple of result
    result = (count_ok, count_conditional)
    return result

# Main script to get optimal number of lands for the deck, to emulate original analysis.
# If any number of lands gives >=90% chance to cast the card, return the smallest number.
# Otherwise, return the number of lands that gives the maximum casting chance
def original_find_optimal_good_lands(num_iter, cost, turn, n, num_lands, min_good_lands, max_good_lands):
    casting_chances = []
    for num_good_lands in range(min_good_lands, max_good_lands+1):
        result = simulate_games(num_iter, cost, turn, n, num_lands, num_good_lands)
        casting_chances.append(float(result[0]) / float(result[1]))
    casting_chances = np.asarray(casting_chances)
    if np.sum(casting_chances >= 0.9) > 0:
        return (np.where(casting_chances >= 0.9)[0][0] + 1)
    else:
        return (np.argmax(casting_chances) + 1)

# Like above function, but uses completed playability matrix
def find_optimal_good_lands(playability, cost, turn, max_good_lands):
    casting_chances = playability[cost, turn, 0:(max_good_lands+1)]
    if np.sum(casting_chances >= 0.9) > 0:
        return (np.where(casting_chances >= 0.9)[0][0])
    else:
        return (np.argmax(casting_chances))
        
# Simulates results for an arbitrary collection of cards, where each is a tuple of (cost, turn, num_good_lands).
# Calculates average value for each card in the deck
def simulate_pool(pool, num_iter, n, num_lands):
    avg_result = 0
    for cost, turn, num_good_lands in pool:
        result = simulate_games(num_iter, cost, turn, n, num_lands, num_good_lands)
        avg_result += float(result[0]) / float(result[1])
    return float(avg_result) / float(len(pool))

# Tests simulation on a pool of cards
def test_simulation_pool():
    pool = [(1, 2, 8), (1, 2, 8), (3, 3, 11), (3, 3, 11)]
    pool_avg = simulate_pool(pool, 10000, 40, 17)
    print(pool_avg)

# Fills out 3d numpy matrix of playability percents, for the axes (cost, turn, num_good_lands)
def fill_playability_matrix(max_cost, max_turn, max_num_good_lands, n, num_lands):
    num_iter = 10000
    results = np.zeros((max_cost + 1, max_turn + 1, max_num_good_lands + 1))
    for cost in range(max_cost + 1):
        for turn in range(max_turn + 1):
            for num_good_lands in range(max_num_good_lands + 1):
                val = simulate_games(num_iter, cost, turn, n, num_lands, num_good_lands)
                results[cost, turn, num_good_lands] = float(val[0]) / float(val[1])
    return results

# Gets the number of colored mana symbols for a given pool of cards
def get_colored_symbols(pool):
    colors = {'W':0, 'U':0, 'B':0, 'R':0, 'G':0}
    for i in range(len(pool)):

        # Gets card and mana cost, skipping it if it doesn't have one
        card = pool[i]
        if 'manaCost' not in card:
            continue
        else:
            mana_cost = card['manaCost']
        
        # Treats hybrid-cost cards as different cards
        if 'W' in mana_cost:
            colors['W'] += mana_cost.count('W')
        if 'U' in mana_cost:
            colors['U'] += mana_cost.count('U')
        if 'B' in mana_cost:
            colors['B'] += mana_cost.count('B')
        if 'R' in mana_cost:
            colors['R'] += mana_cost.count('R')
        if 'G' in mana_cost:
            colors['G'] += mana_cost.count('G')
    return colors

# Gets tuple of (mana_cost, turn, colors, card_name) for each card in the deck.
# mana_cost: number of mana symbols for the given color
# colors: color of mana
# turn: CMC of card
# card_name: name of card
def get_costs(pool):
    costs = []
    for i in range(len(pool)):

        # Gets card and mana cost, skipping it if it doesn't have one or if it's a land
        card = pool[i]
        name = card['name']
        cmc = int(card['convertedManaCost'])
        if 'manaCost' not in card:
            continue
        else:
            mana_cost = card['manaCost']
        
        # Treats hybrid-cost cards as different cards
        if 'W' in mana_cost:
            costs.append((mana_cost.count('W'), cmc, 'W', name))
        if 'U' in mana_cost:
            costs.append((mana_cost.count('U'), cmc, 'U', name))
        if 'B' in mana_cost:
            costs.append((mana_cost.count('B'), cmc, 'B', name))
        if 'R' in mana_cost:
            costs.append((mana_cost.count('R'), cmc, 'R', name))
        if 'G' in mana_cost:
            costs.append((mana_cost.count('G'), cmc, 'G', name))
    return costs

# Gets optimal lands for each card in the deck
def get_optimal_lands(playability, costs, main_colors):
    results = []
    for cost in costs:
        max_good_lands = 0
        if cost[2] in main_colors:
            max_good_lands = 17
        else:
            max_good_lands = 3
        optimal = find_optimal_good_lands(playability, cost[0], cost[1], max_good_lands)
        results.append((cost[3], cost[2], cost[0], cost[1], optimal))
    return results

# Main script
def main():

    # Sets working directory
    os.chdir("/project/csbio/henry/Documents/projects/draftsim/MTG")

    # Gets playability matrix
    playability_file = "../data/40_card_playability.npy"
    playability = None
    if os.path.isfile(playability_file):
        playability = np.load(playability_file)
    else:
        playability = fill_playability_matrix(4, 8, 17, 40, 17)
        np.save("../data/40_card_playability.npy", playability)
    
    # Reads in mtgJSON data
    setName = 'GRN'
    jsonSubset = None
    with open('../data/all_sets.json', 'r',encoding='utf-8') as json_data:
        mtgJSON = json.load(json_data)
        jsonSubset = mtgJSON[setName]['cards']
    if setName=='XLN':
        jsonSubset = jsonSubset + mtgJSON['RIX']['cards']

    # Converts cards to dict with lowercase names as indices for cards
    this_set = {utils.getName(card) : card for card in jsonSubset}
    dict((k.lower(), v) for k, v in this_set.items())    
    cardlist = list(this_set.keys())

    # Reads in draftsim data and formats it
    pools = pd.read_csv("../data/grn_subset.csv")
    pools = pools.iloc[:,[3]]
    pools = pools.values
    #pools = [re.sub('_\d+', '', x[0]).lower() for x in pools]

    # Works with 10 pools for testing
    for i in range(len(pools)):
        cards = utils.fixName(str(pools[i])).lower().split(',')
        print(cards)
        info = [this_set[x] for x in cards]

        # Gets top two colors in the deck
        colors = get_colored_symbols(info)
        sorted_colors = sorted(colors, key=colors.get, reverse=True)
        main_colors = sorted_colors[0:2]
        
        # Gets mana costs, color and target turn for each nonland card
        costs = get_costs(info)

        # Gets optimal number of lands for each card in the deck. 
        adjusted_costs = get_optimal_lands(playability, costs, main_colors)
        
        # Writes costs to file
        deck_file = '../decks/mana_analysis/draft_deck_' + str(i+1) + '.csv'
        with open(deck_file, 'w') as f:
            csv_conn = csv.writer(f)
            csv_conn.writerow(['Card', 'Color', 'Colored_cost', 'CMC', 'Optimal_lands'])
            for row in adjusted_costs:
                csv_conn.writerow(row)
    return




main()