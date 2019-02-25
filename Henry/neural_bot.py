
import pandas as pd
import numpy as np

import csv
import json
import itertools
import time
import re
import os
import ast

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler 
from sklearn.metrics import mean_absolute_error

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

# Utility functions lifted from basic_analysis.py
def getCardColor(card):
    colors = ['W', 'U', 'B', 'R', 'G'] 
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

def main():

    # Sets working directory
    os.chdir("/project/csbio/henry/Documents/projects/draftsim/MTG")
    output_folder = ("ml")

    # Sets seed for reproducibility
    seed = 5001
    
    # Reads in mtgJSON data
    setName = 'GRN'
    jsonSubset = None
    with open('../data/all_sets.json', 'r',encoding='utf-8') as json_data:
        mtgJSON = json.load(json_data)
        jsonSubset = mtgJSON[setName]['cards']
    if setName=='XLN':
        jsonSubset = jsonSubset+ mtgJSON['RIX']['cards']

    # Converts cards to dict with lowercase names as indices for cards
    this_set = {getName(card) : card for card in jsonSubset}
    dict((k.lower(), v) for k, v in this_set.items())    
    cardlist = list(this_set.keys())

    # Reads in draftsim data and formats it
    rec_data = pd.read_csv("../data/GRNrecdata.csv", names = ["deck", "pack", "pick"])
    rec_data = rec_data.drop(["deck"], axis = 1)
    rec_data["pack"] = [re.sub('_\d+', '', x).lower() for x in rec_data["pack"]]
    rec_data["pick"] = [re.sub('_\d+', '', x).lower() for x in rec_data["pick"]]

    # One-hot encodes draftsim data
    labels = dict(zip(cardlist, range(len(cardlist))))
    rec_data["pick"] = [labels[x] for x in rec_data["pick"]]
    rec_data["pack"] = rec_data["pack"].astype(object)
    rec_data["pick"] = rec_data["pick"].astype(object)
    rec_data["pack"] = [ast.literal_eval(x) for x in rec_data["pack"]]
    formatted = rec_data
    for index, row in rec_data.iterrows():
        pick_encode = [0 for i in range(len(cardlist))]
        pack_encode = [0 for i in range(len(cardlist))]
        pick_encode[row["pick"]] = 1
        for name in row["pack"]:
            pack_encode[labels[name]] = 1
        formatted.at[index, "pick"] = pick_encode
        formatted.at[index, "pack"] = pack_encode

    final = np.zeros(formatted.shape[0], dtype=[('x','int', len(cardlist)), ('y','int', len(cardlist))])
    for i in range(formatted.shape[0]):
        final["x"][i] = [el for el in formatted["pack"][i]]
        final["y"][i] = [el for el in formatted["pick"][i]]

    # Converts to training/test data with an 80/20 split
    x_train, x_test, y_train, y_test, = train_test_split(final["x"], final["y"], test_size=0.2, random_state=seed) 

    # Trains an MLP regressor
    model = MLPRegressor()
    grid = dict(activation=["relu"],
                solver=["adam"],
                hidden_layer_sizes=[(500,1000,500)],
                alpha=[1e-5, 1e-3, 0.1, 10],
                random_state=[seed],
                early_stopping=[True],
                max_iter=[50])
    model = GridSearchCV(model, param_grid=grid, verbose=True, n_jobs=16, cv=5)
    model.fit(x_train, y_train)
    print(model.best_params_)

    # Gets training and testing metrics
    train_predictions = np.asarray(model.predict(x_train))
    test_predictions = np.asarray(model.predict(x_test))
    train_correct = 0
    test_correct = 0
    for i in range(train_predictions.shape[0]):
        choices = np.where(x_train[i] == 1)
        predictions = train_predictions[i][choices]
        correct_ind = np.where(y_train[i][choices] == 1)
        ranks =  np.sort(predictions)[::-1]
        if(len(ranks) > 1):
            if ranks[0] == correct_ind or ranks[1] == correct_ind:
                train_correct += 1
        else:
            if ranks[0] == correct_ind:
                train_correct += 1
    for i in range(test_predictions.shape[0]):
        choices = np.where(x_test[i] == 1)
        predictions = test_predictions[i][choices]
        correct_ind = np.where(y_test[i][choices] == 1)
        #ranks =  np.sort(predictions)[::-1]
        ranks =  np.sort(predictions)
        if(len(ranks) > 1):
            if ranks[0] == correct_ind or ranks[1] == correct_ind:
                test_correct += 1
        else:
            if ranks[0] == correct_ind:
                test_correct += 1
    print(train_correct)
    print(float(train_correct) / float(len(train_predictions)) * 100)
    print(float(test_correct) / float(len(test_predictions)) * 100)



    

main()
