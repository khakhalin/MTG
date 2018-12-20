from random import shuffle


class Bot(object):

    # Class CONSTANTS
    # None for base bots but yours should go here in ALL_CAPS

    def __init__(self):
        self.num_correct = 0
        self.num_total = 0

    '''
    INPUT: one draft frame in form [pack, collection, pick]
    OUTPUT: index of pack of chosen card
    NOTE: use list not tuple or dict for input
    
    This method is to be called by the testing script. Modify the get_choice method
    with the drafting logic of you bot's subclass.
    '''
    def decide(self, draft_frame):
        choice = self.get_choice(draft_frame)[-1]

        self.num_total += 1

        if draft_frame[1][choice] == draft_frame[2]:
            self.num_correct += 1

        return choice


    '''
    INPUT: the input from decide
    OUTPUT: argsorted list of indices of a pack
    
    This is where your bot logic should go. In your bot subclass, overwrite this function
    with your own evaluation method. INPUTS and OUTPUTS must be standard across all bots.
    '''
    def __get_choice(self, draft_frame):
        return shuffle(draft_frame[1])

    # return tuple of number correct and total so far
    def get_performance(self):
        return self.num_total, self.num_correct

    # reset class variables
    def clear_history(self):
        self.num_correct = 0
        self.num_total = 0
