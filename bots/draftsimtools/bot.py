from random import randint

class Bot(object):

    #Class CONSTANTS
    #None for base bots but yours should go here in ALL_CAPS


    def __init__(self):
        self.num_correct = 0
        self.num_total = 0


    def decide(self, draft_frame):
        '''
        INPUT: one draft frame in form [pack, collection, pick]
        OUTPUT: index of pack of chosen card
        NOTE: use list not tuple or dict for input
    
        This method is to be called by the testing script. Modify the get_choice method
        with the drafting logic of you bot's subclass.
        '''
        choice = self.__get_choice(draft_frame)

        self.num_total += 1

        if draft_frame[1][choice] == draft_frame[2]:
            self.num_correct += 1

        return choice


    def __get_choice(self, draft_frame):
        '''
        INPUT: the input from decide
        OUTPUT same as decide
    
        This is where your bot logic should go. In your bot subclass, overwrite this function
        with your own evaluation method. INPUTS and OUTPUTS must be standard across all bots.
        '''
        choice = randint(0, len(draft_frame[1])) - 1
        return choice


    def get_performance(self):
        ''' Return tuple of number of correct picks so far. '''
        return self.num_total, self.num_correct
    
    
    def clear_history(self):
        ''' Reset class variables. '''
        self.num_correct = 0
        self.num_total = 0
