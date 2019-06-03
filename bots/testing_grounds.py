# Preprocessing imports 
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

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

    # Splits into (toy) training and test sets. NOTE: For real training, use all drafts.
    subset_drafts = drafts[5000:5500]
    train, test = train_test_split(subset_drafts, test_size = 0.4)

    # Creates a bot that implements current Draftsim logic
    draftsim_bot = ds.DraftsimBot(rating_dict)
    
    # Creates a bot that implements current Draftsim logic with SGD optimization
    sgd_bot = ds.DraftsimSGDBot(rating_dict)
    epochs = 5
    for x in range(epochs):
        sgd_bot.sgd_optimization(train, 0.05)
    print("Done optimizing SGD bot")

    # Gets bot accuracy for some packs
    tester = ds.BotTester(test)
    tester.evaluate_bots([draftsim_bot, sgd_bot], ["Draftsim2018", "Draftsim2018SGD"])
    tester.write_evaluations()

main()