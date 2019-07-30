import numpy as np
import csv

import itertools as it

from tqdm import tqdm # Supports progress bar.
import math
import re

#These three variables need to be strings

#output file:
save_filename = 'GRNrecon.csv'
#input file:
data_filename = 'GRNdata.csv'
#format code eg: GRN, M19, DOM etc.
format_abv = 'GRN'


PLAYERS = ['human', 'bot1', 'bot2', 'bot3', 'bot4', 'bot5', 'bot6', 'bot7']
PACK_SIZE = 15
NUM_PACKS = 3

file_length = len(list(csv.reader(open(data_filename))))
line_number = 0

f = open(data_filename, 'r')

line_iterator = it.islice(csv.reader(f), 1, None)

data_set = []

progress_bar = tqdm(total=file_length, position=0)

while line_number <= file_length:
    progress_bar.update()

    #this try/except takes us out of the while loop once we reach the end of the file
    try:
        line = next(line_iterator)
    except StopIteration:
        break


    #get to next line of correct format
    while line[1] != format_abv:
        line = next(line_iterator)

    #get rid of the id and format columns of the line
    line = line[2:]

    #read one line of data
    draft = []
    for p in range(len(PLAYERS)):
        player = line[p]
        # clean data
        player = re.sub(',_', '_', player)
        # add to draft
        draft.append(player.split(','))

    #increment points the packs in the right direction
    #this is how we handle pass left or right
    increment = 1

    collection = []

    #three packs
    for x in range(NUM_PACKS):

        pick_num = 0
        while pick_num < PACK_SIZE:
            pick = draft[0][pick_num + (x * PACK_SIZE)]
            pack = []

            pack_num = pick_num
            player_num = 0
            #construct pack
            while pack_num < PACK_SIZE:
                pack.append(draft[player_num % len(PLAYERS)][pack_num + (x * PACK_SIZE)])
                pack_num += 1
                player_num += increment

            data_set.append(([i for i in collection], pack, pick))
            collection.append(pick)

            pick_num += 1

        increment *= 1


save_file = open(save_filename,'w')

with save_file:
    writer = csv.writer(save_file)
    writer.writerows(data_set)
save_file.close()

















