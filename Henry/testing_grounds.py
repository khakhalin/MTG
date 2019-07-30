# Preprocessing imports 
from sklearn import preprocessing

import draftsimtools as ds

# Main script
def main():

    # Load M19 drafts (dump #2)
    m19_set = ds.create_set("data/m19_rating.tsv", "data/m19_land_rating.tsv")
    raw_drafts = ds.load_drafts("data/m19_2.csv")
    m19_set, raw_drafts = ds.fix_commas(m19_set, raw_drafts)

    # Creates rating dictionary
    rating_dict = ds.create_rating_dict(m19_set)

    # Process the drafts
    drafts = ds.process_drafts(raw_drafts)
    
    # Creates an M19 player and optimizes it
    b = ds.SGDBot(rating_dict)
    for x in range(10):
        b.sgd_optimization(drafts[0:25], 0.05)
    print("Done optimizing SGD bot")

    # Gets bot accuracy for some packs
    testing_set = drafts[26:10000]
    tester = ds.BotTester(testing_set)
    tester.evaluate_bots([b], ["SGD"])
    tester.write_evaluations()

main()