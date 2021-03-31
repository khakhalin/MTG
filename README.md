Building Magic: the Gathering Drafting Bots
========================================

This repository contains code for building and evaluating MTG drafting bots, discussed in our recent paper: "**AI solutions for drafting in Magic: the Gathering**" by Henry N. Ward, Daniel J. Brooks, Dan Troha, Bobby Mills, and Arseny S. Khakhalin (2020). https://arxiv.org/abs/2009.00655

![Visual profiles of 4 MtG sets](bots/output_files/all_footprints.svg)

All code for drafting bots can be found in the *bots* folder. Most scripts take MTG drafts collected from [Draftsim.com](http://draftsim.com) as an input. The data is licensed under a CC BY 4.0 International license and is downloadable [here](https://draftsim.com/draft-data/).

To introduce each major folder and script:

- *draftsimtools* is a module that contains a variety of utility functions and classes for handling Draftsim data and implementing bots.
- *create_standardized_set.ipynb* takes in raw Draftsim data and processes it.
- *create_cv_dataset.ipynb* takes in processed Draftsim data and generates training and testing sets. 
- *load_standardized_set.ipynb* demonstrates the use of processed Draftsim data. 
- *bayesbot_preprocessor.ipynb* trains the BayesBot agent.
- *train_nnet.py* trains the NNetBot agent. 
- *testing_grounds.ipynb* evaluates all bots on testing drafts.  
- *analyze_results.R* generates all stats and figures reported in the paper. 

And for files in *draftsimtools*:

- *bot.py* contains the base class that all bots inherit from. 
- *random_bot.py* implements the Randombot agent. 
- *raredraft_bot.py* implements the RaredraftBot agent. 
- *classic_bot.py* implements the DraftsimBot agent. 
- *bayes_bot.py* implements the BayesBot agent (after training). 
- *nnet_bot.py* implements the NNetBot agent (after training). 
- *bot_tester.py* contains the class that evaluates bots on testing data.

To make and evaluate new drafting bots, we recommend following the process outlined below:

1. Download training and testing drafts from the link above.
2. Process the drafts as demonstrated in *load_standardized_set.ipynb*.
3. Make a new bot class that inherits from *bot.py* in *draftsimtools* and implements your drafting logic. 
4. Evaluate your bot against our existing bots by modifying *bot_tester.py.*

## Media

In addition to Ward et al. (2020), we also published several blog posts that dig deep into exploratory analyses of Draftsim data. 

1. [Basic analysis](https://draftsim.com/blog/draft-data-analysis/): introduces co-drafting distances and MDS scaling.
2. [Changes in drafting](https://draftsim.com/blog/m19-format-evolution/): discusses drafting of the same set early in the season, compared to late  in the season. Also, statistics of color preferences (aka Guilds) among players.
3. [Controversial cards](https://draftsim.com/blog/guilds-of-ravnica-first-look/): discusses cards that are loved by some people, but disliked by others (original idea by Bobby Mills). This analysis turned to be rather fancy, as we ran into a couple of mathematical paradoxes.
4. [Color wheel](https://draftsim.com/blog/ravnica-allegiance-first-look/): similar analyses as the above for guild-based blocks (GRN and RNA).
5. [Eldraine bot](https://draftsim.com/ryan-saxe-bot-model/): Ryan Saxe's bot presents a very cool offshoot of this project. 

![rotating cube](https://draftsim.com/wp-content/uploads/2018/08/rotating-m19-cube.gif)

## Raw data

Raw data used in this project (for the M19 MtG set) is available here: https://draftsim.com/draft-data/

## Other scripts

In addition to drafting bot code, the *archive* folder contains miscellaneous scripts for visualizing and analyzing Draftsim data. 

Code commentaries:

* Basic analysis in R: [markdown notebook](Arseny/writeup_intro.Rmd), and [the same thing rendered in HTML](http://htmlpreview.github.io/?https://github.com/khakhalin/MTG/blob/master/Arseny/writeup_intro.nb.html) (with ggplot graphs and everything).

## About Us

The project is supported by a small team of people: Arseny Khakhalin, Bobby Mills, Dan Troha, Daniel Brooks, and Henry Ward. Feel free to reach out to us with any questions or comments.  
