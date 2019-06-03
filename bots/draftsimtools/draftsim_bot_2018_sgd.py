from .draftsim_bot_2018 import *

class DraftsimSGDBot(DraftsimBot):

    def sgd_optimization(self,
                         drafts,
                         learning_rate = pow(10,-2)):
        """Update parameters in rating dict using Stochastic Gradient Descent.

        Runs through a collection of drafts once.
        """

        #Collect a list of drafts.
        num_drafts = len(drafts)
        shuffled_draft_order = [i for i in range(num_drafts)]

        #Shuffle the order of the picks.
        shuffle(shuffled_draft_order)

        #Loop over each draft.
        for d in shuffled_draft_order:

            #Print updates.
            if self.draft_count % 100 == 0:
                print("Starting SGD optimization for draft " + str(self.draft_count))

            #Start the draft.
            self.new_draft(drafts[d])
            for p in range(len(self.draft)):

                #Get the relative ratings.
                pack = self.draft[p]
                cardname_picked = pack[0]
                rating_list = self.create_rating_list(pack)

                #Prepare gradient descent ratings update.
                temp_rating_dict = deepcopy(self.rating_dict)
                for r in rating_list:

                    #Update when there is an error.
                    cur_cardname = r[0]
                    residual = max(r[1], 0)
                    if residual > 0:

                        #Update using squared error.
                        #update_amount = learning_rate #Linear error.
                        update_amount = learning_rate * 2 * residual #Quadratic error
                        temp_rating_dict[cardname_picked][1] += update_amount
                        temp_rating_dict[cur_cardname][1] -= update_amount
                        self.loss_current += pow(update_amount, 2)

                #Advance to next pick.
                self.make_pick()

                #Update ratings.
                self.rating_dict = temp_rating_dict

        #Save loss function.
        self.loss_history.append(self.loss_current)
        self.loss_current = 0

