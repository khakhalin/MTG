# AI solutions for competitive drafting in Magic: the Gathering
Authors: Dan Brooks, Henry, Dan Troha, Bobby, Arseny - in this order? Or random? Or something else?

Possible venues: AIIDE, GDC and FLAIRS

# Abstract

TODO

# Introduction

AI agents have recently achieved superhuman performance on challenging games such as chess, shogi, go, and poker [refs], and ongoing work aims to create AI that conquer real-time strategy games and multiplayer online battle arenas (MOBAs). These successes open opportunities to branch out and to create game-playing AI for other complex games. Much like strategy and MOBA games, collectible card games (CCGs) such as Hearthstone and “Magic: the Gathering” (MTG) present challenging milestones for AI, due to their mechanical complexity, multiplayer nature, and large amount of hidden information. Although some previous work investigated AI for Hearthstone [Świechowski 2018, more], relatively little work exists on building game-playing AI for MTG [Bjorke 2017, more].

In this paper, we focus on a game mode known as “drafting”, that involves progressive deck-building, with players taking turns to select cards for their collection from a given initial set of cards [Kowalski 2020]. From the final collections of cards, each player then builds a deck, to play games against each other, and determine the winner of the draft. We focus on drafting in Magic: the Gathering. MTG features one of the most complicated and popular drafting environments, where each of eight players opens a pack of 15 semi-random cards, selects one card from that pack, and passes the remainder of the pack to an adjacent player. This process is repeated until all cards are drafted, and then is repeated all over again for two more packs (with the second pack passed in the opposite direction). By the end of the draft, each player has a pool of 45 cards from which they select 20-25 cards to build a deck. Critically, each player's current pick and a growing collection are hidden from other players.

While the core idea of building a deck by progressively selecting cards is shared by all drafting games, other key aspects of drafting are quite variable. On the simpler end of the spectrum, Hearthstone's drafting game (known as Arena) presents a single player with three semi-random cards from which they choose one to add to their deck. The player is given 30 choices, and ends up with a 30-card deck. While drafting in MtG and Hearthstone both involve progressive deck-building from randomly-assorted cards, unlike Hearthstone, MtG drafting is complicated by its competitive multiplayer nature, larger search space, and a substantial amount of hidden information. It is therefore likely that successful MtG drafting agents will rely on strategies that generalize to other, simpler drafting games like Hearthstone Arena. A summary of key aspects in which popular drafting games vary is listed in Table 1.


![](https://paper-attachments.dropbox.com/s_3E11CDC24047F49065A86D936DF62D9D76CC43487E9B96F1F6E4D5C159806FE4_1579537700230_table1.PNG)


These key attributes of drafting games present interesting challenges for AI agents, and are further complicated by the large search space of a single draft. When evaluating a single pack of cards to decide which card to pick, a successful MtG drafting agent must take into account the individual strength of each card, the synergies between each card and the cards already in the collection, and the strategies their opponents may be pursuing. In a full draft, a drafting agent sees a total of 315 cards, and makes 45 consecutive decisions of which card to take, bringing the total number of direct card-to-card comparisons to 7,080. In addition, the agent could potentially compare the distribution of cards it receives from its opponents to an expected distribution, as well as note which cards were not drafted after each pack of 15 cards traveled around the table of 8 players for the first time. Overall, for a set of 250 different cards, the full landscape of a draft comprises about 10^{700} starting conditions and roughly 10^{40} potential deck-building trajectories, rendering brute-force approaches impossible.

Here, we design, implement, and compare several strategies for building human-like MtG drafting agents. It is important to note that we are not concerned with making agents that draft “better than human players,” and we do not evaluate the quality of decks drafted by agents. Rather, we aim to create agents that draft similarly to human players. As online CCGs such as MtG Arena frequently pit players against drafting agents (bots) and not against other players, the creation of human-like agents could benefit both players and game development teams. While drafting agents currently employed in games such as MtG Arena enable asynchronous play, they seem to rely on simple heuristics that frequently result in negative gameplay experiences for players. Human-like drafting bots could provide a better experience and allow human players to build decks with more varied strategies.

To the best of our knowledge, this article (together with a sister project by Ryan Saxe [https://draftsim.com/ryan-saxe-bot-model/]) presents the first attempt to build drafting agents for MtG. Previous work has formulated constructed deck-building in CCGs as a combinatorial optimization problem, where the goal is to construct a deck with an optimized winning rate against a given “metagame” (the set of possible decks the player may expect to play against) [Chen 2018, more]. This approach however does not work well for MtG drafting, due to the inherent variability of the game and the large amount of hidden information involved. Moreover, public data from actual drafts is scarce, which makes the evaluation of drafting agents challenging.

We address these challenges by presenting a dataset of MtG drafts performed by human players, collected from anonymous users of the draft simulator website draftsim.com, and formulate the problem of building human-like drafting agents as a classification task. We benchmark several drafting strategies, including a neural-network approach and a Bayesian approach, against simple heuristic-based approaches, and show that they predict human choices with relatively high accuracy.

Our work contributes the following:
                We present the first large-scale, publicly-available dataset of human MTG drafts, enabling the study of drafting to the AI and game-development community writ large.
                We frame drafting as a classification problem with the goal of creating drafting agents that accurately predict human card choices.
                We show that a deep neural-network approach can predict human card choices, and suggest that similar approaches can help game developers interested in building new drafting agents.
                
All code and data used in this paper are available on: https://github.com/khakhalin/MTG

# Relevant work

While no previous work exists on drafting in online CCGs (1), several papers investigate constructed deck-building in Hearthstone and MTG (2-5). These works frame deck-construction as a combinatorial optimization problem, where the goal is to select cards to add to a deck that maximize the winning rate of the completed deck against a set of known decks. Evolutionary algorithms, Q-learning, and a utility system were employed to address this problem. Similar work applies evolutionary or quality-diversity algorithms towards deck-building in Hearthstone and Dominion with the aim of investigating or evolving game balance (6-8).

Unfortunately, previous research on constructed deck-building cannot be directly reapplied to building human-like drafting bots. To leverage this body of work, assumptions would have to be made about the decks to optimize against, before the draft is even completed. This is a potentially difficult problem in its own right: even disregarding the high variability of drafts within a specific format, players only select roughly half of the cards they draft to put into their deck. Assuming that players use exactly 17 basic lands in their deck and thus choose 23 cards from their total pool of 45 cards to complete a 40-card deck, there are well over 10^12 possible ways to construct a deck from a single draft. Accordingly, a crucial prerequisite for framing drafting as a combinatorial optimization problem is the existence of an efficient algorithm for building a realistic deck from a completed draft pool, which is beyond the scope of this work. 
 
Outside of online CCGs, a small body of research examines drafting in multiplayer online battle arenas (MOBAs) such as League of Legends and DotA 2 (9-12). MOBAs task players with sequentially choosing a team of in-game avatars that have different skillsets and synergies with each other, alternating choices with the opposing team which they aim to beat during a subsequent game. Much like drafting in MTG, MOBA drafting involves sequentially choosing heroes from a depleting pool. Previous research on this topic aimed to build recommender systems for hero choices (9,10), or to predict hero choices as drafts progress (10-11). Like the work presented here, these authors typically use machine learning techniques to predict the next chosen hero or the optimal combination of heroes based on training datasets of actual drafts.

Drafting games seen in MOBAs as well as the autobattler genre [ref] likely benefit from existing research on team formation problems. Previous work has formulated fantasy football as a sequentially-optimal team formation problem (13). The key distinctions between selecting players in fantasy football and selecting heroes during MOBA drafts are the gameplay phases that occur after each fantasy football draft (MOBAs only have one gameplay phase, which occurs after the draft is completed), the fact that MOBA heroes are limited resources (unlike fantasy football players, which can be chosen by multiple human players), and the economy system in fantasy football that assigns prices to players (MOBA drafting lacks an economy system). Autobattlers are perhaps more similar to fantasy football, because they also feature an economy system and alternate drafting phases and gameplay phases. However, heroes selected in autobattlers, like heroes in MOBA drafts, are a limited resource. While it may be possible to build drafting agents for MOBAs and autobattlers that treat the games as team formation problems, further research is necessary to enable the adaptation of previous team formation work to these games (15-17). 

Citations
1: The Many AI Challenges of Hearthstone. https://arxiv.org/pdf/1907.06562.pdf
2: Evolutionary Deckbuilding in Hearthstone. [http://geneura.ugr.es/~pgarcia/papers/2016/hs-cig2016.pdf](http://geneura.ugr.es/~pgarcia/papers/2016/hs-cig2016.pdf)
3: Q-DeckRec: A Fast Deck Recommendation System for Collectible Card Games. [https://arxiv.org/pdf/1806.09771.pdf](https://arxiv.org/pdf/1806.09771.pdf)
4: Deckbuilding in Magic: The Gathering using a Genetic Algorithm. [https://ntnuopen.ntnu.no/ntnu-xmlui/bitstream/handle/11250/2462429/16274_FULLTEXT.pdf?sequence=1](https://ntnuopen.ntnu.no/ntnu-xmlui/bitstream/handle/11250/2462429/16274_FULLTEXT.pdf?sequence=1)
5: Evolving the Hearthstone Meta. [https://arxiv.org/pdf/1907.01623.pdf](https://arxiv.org/pdf/1907.01623.pdf)
6: Exploring the Hearthstone Deck Space. [http://game.engineering.nyu.edu/wp-content/uploads/2018/07/exploring-hearthstone-deck.pdf](http://game.engineering.nyu.edu/wp-content/uploads/2018/07/exploring-hearthstone-deck.pdf)
7: Evolving Card Sets Towards Balancing Dominion. [http://julian.togelius.com/Mahlmann2012Evolving.pdf](http://julian.togelius.com/Mahlmann2012Evolving.pdf)
8: Mapping Hearthstone Deck Spaces through MAP-Elites with Sliding Boundaries. [https://arxiv.org/pdf/1904.10656.pdf](https://arxiv.org/pdf/1904.10656.pdf)
9: A Recommender System for Hero Line-Ups in MOBA Games. [https://aaai.org/ocs/index.php/AIIDE/AIIDE17/paper/view/15902](https://aaai.org/ocs/index.php/AIIDE/AIIDE17/paper/view/15902)
10: The Art of Drafting: A Team-Oriented Hero Recommendation System for Multiplayer Online Battle Arena Games. [https://arxiv.org/pdf/1806.10130.pdf](https://arxiv.org/pdf/1806.10130.pdf)
11: Draft-Analysis of the Ancients: Predicting Draft Picks in DotA 2 Using Machine Learning. [https://aaai.org/ocs/index.php/AIIDE/AIIDE16/paper/view/14075](https://aaai.org/ocs/index.php/AIIDE/AIIDE16/paper/view/14075)
12: E-Sports Ban/Pick Prediction Based on Bi-LSTM Meta Learning Network. [https://link.springer.com/chapter/10.1007/978-3-030-24274-9_9](https://link.springer.com/chapter/10.1007/978-3-030-24274-9_9)
13: Competing with Humans at Fantasy Football: Team Formation in Large Partially-Observable Domains https://www.aaai.org/ocs/index.php/AAAI/AAAI12/paper/viewFile/5088/5473
15: Capacitated Team Formation Problem on Social Networks. https://arxiv.org/pdf/1205.3643.pdf
16: The multiple team formation problem using sociometry. https://www.sciencedirect.com/science/article/pii/S0305054816301198
17: Finding a team of experts in social networks. https://dl.acm.org/doi/abs/10.1145/1557019.1557074

# MTG Terminology

Here we describe terminology for drafting games in general, and MTG in particular.

## Drafting Games

We define *drafting games* as games which include drafting as a core mechanic. *D**rafting* is defined as sequential deck-building from a rotating, limited resource. Drafting games typically include one or more *drafting phases*, where players build or improve their decks, and *gameplay phases*, where players pit their deck against other players’ decks. These phases are nearly always discrete. 

## Drafting Modes

The two games that follow the traditional drafting mechanics described above, are MTG and Eternal. We will refer to their gameplay as *drafting*, as they are characterized by multiplayer drafting from relatively large, rotating packs. Drafting games that follow Hearthstone’s model and present a more limited set of choices to a single player will be referred to as *arena* modes (named after Hearthstone’s drafting mode, Arena). Additionally, many MOBAs such as DotA and League of Legends can also be considered drafting games, because before each game they require two teams of five people to sequentially select heroes to represent them in the game (which have different strengths, weaknesses, and synergies with other heroes). However, because MOBA drafting is particularly straightforward, we will instead refer to it as a *team formation* problem. Lastly, a new genre of games known as autobattlers (exemplified by Autochess and Teamfight Tactics) couples traditional drafting mechanics with an economy system. We will refer to these types of drafting games as *autobattlers*. 

## MTG Overview

MTG is a card game in which two or more players use their decks to compete against each other in best-of-three matches. A player wins by reducing their opponent's life total from the starting value of 20 to 0. Each player starts with a hand of seven cards and draws one additional card each turn. Players use special “land” cards to generate mana, which can then be used to play other cards. Mana comes in five different colors (white, blue, black, red, and green), and “effect” cards can cost any combination of different colors of mana to cast. While most cards are limited to four copies per deck, a deck can have an unlimited amount of basic lands.

## Domain Complexity

MTG's comprehensive rules are approximately 200 pages long, and judges are employed at every significant tournament to resolve frequent rule-based misunderstandings. Moreover, previous work has shown that the set of MTG rules is Turing-complete [ref], and the problem of checking whether or not a single MTG action is legal can be coNP [ref].  

In total, there are over 17,000 MTG cards. However, a given set used for drafting typically contains somewhere between 250 and 350 unique cards. On occasion, drafts may include multiple packs of different sets.

## Card Features

Magic cards are distinguished by a variety of categorical features. Each card belongs to one or more of the seven major types: creature, sorcery, instant, artifact, enchantment, land, planeswalker, and tribal. Each non-land card has a mana cost, which represents the amount of mana required to play it. This mana cost may include both colored mana and colorless mana (which can be of any color), and the total of a card's colored and colorless mana cost is referred to as its converted mana cost. Creatures also have power and toughness values, which are used in combat and generally range from 0 to 10.

# Data description and exploratory analyses
## Data description

The website draftsim.com collects draft data from its users since spring 2017. The site offers a drafting experience, in which a human player drafts against 7 bots, each of them following the same manually tuned heuristic strategy, described in detail below (“Complex heuristic” bot). At the beginning of a draft, the user picks a set of cards to draft from. Each set typically contains around 250-300 different cards and is specifically balanced around drafting. From the chosen set, booster packs are randomly generated with a card frequency distribution matching that of real booster packs. In total, 11/15 cards are “common” rarity, 3/15 are “uncommon”, 7/120 are “rare”, and 1/120 are “mythic” [ref]. The user then goes through the draft, and all their choices, as well as choices made by the 7 bots they draft against, are recorded anonymously and saved in an SQL database. Draftsim does not record player ids, their IP or location, or the time it took them to make each individual pick. As of summer 2020, Draftsim has data for 14 different sets (all sets released after Jan 2018), with about 100,000 completed drafts for popular sets. Each full draft (one data point) consists of 45 consecutive decisions, made by the player.

## Training and testing data

All drafting agents presented below were trained and evaluated on drafts of a single MtG set, Core Set 2019 (abbreviated as M19). This set contains 280 different cards, including 16 mythic rare cards, 53 rare cards, 80 uncommon cards and 111 common cards. We obtained a total of 107,949 user drafts of the M19 set from the Draftsim website, and split these into a training set of 86,359 drafts and a testing set of 21,590 drafts (an 80/20 split). As each draft contains 24 unique packs of cards, a total of 2,072,616 packs were seen by drafting agents during training, and a total of 518,160 packs were used to evaluate the drafting agents’ performances. 

## Analysis and visualization of the data

Cards of every MtG set form a complex network of interactions. Some cards are designed to “synergize” with each other, either because they require similar resources to be played (such as a mana of a particular color), or because one card changes its behavior when another card is present on the field. Certain pairs of cards can also either complement each other, or compete with each other in terms of optimizing the distribution of converted mana costs within the deck. This brings the logic of drafting far beyond picking an “objectively best” card from a pile, but makes it resemble a stochastic descent towards one of the powerful deck configurations, as players try to pick cards that work best together. These powerful deck configurations are unique for each drafting environment.

To visualize this multidimensional optimization landscape, and to inform the creation of AI agents, for each pair of cards $$(i,j)$$ in our data, we looked into whether they were likely to be drafted together by human players. We calculated the frequency of pairs of cards ending up in the same collection $$P_{ij}$$, and compared it to the probability that these cards would be drafted together by chance, if drafting was completely random ($$P_i P_j$$). The cards may be called synergistic (not in the narrow sense, used by MtG players, but in a broader, statistical sense) if $$P_{ij}>P_i P_j$$, and the ratio of two probabilities $$S_{ij} = P_{ij}/P_i P_j$$ can be used as a measure of this synergy. 

To visualize a “profile” of each set, we considered a weighted graph, defined by a distance matrix $$D$$, that placed card closer to each other if they were often drafted together, with card-to-card distances given by a formula: $$D_{ij} = (1-S_{ij}/\text{max}_{ij}(S_{ij}))$$ . We projected this graph to a 2D plane using a linear multidimensional scaling algorithm that maximized the Pearson correlation coefficient between the “true” distances $$D_{ij}$$, and the Euclidean distances within the 2D projection $$\hat{D}_{ij}$$. Visual profiles, or “synergy plots”, for several MTG sets are shown in Fig 1B, with each card represented by a point, and the color of this point matching the color of mana required to play this card.

![](https://paper-attachments.dropbox.com/s_CEE80E23ED798A9C68C76CD8F413BBE041F8CF2BB6F3C2991E9BFD8D51B4C2D8_1566424775786_image.png)


It is clear from the synergy plots that cards indeed form clusters, based on whether they can be used together in a meaningful deck. For most sets these clusters are mostly defined by card colors (with the exception of RIX, Fig 2a, that was designed as a so-called “tribal set”). We found that these “profile plots” reflect the intuitions that experienced players have about each set, in terms of colors that are easier to combine (their clusters are placed closer to each other on the plot); and cards that belong to more than one archetype (that end up located between distinct clusters) [refs our blog articles]. It is also interesting that different sets produce profile plots of different shapes, reflecting the work of MtG gameplay designers [ref one of the Rosewater’s blog posts?].

The synergy plots also illustrate why a good drafting AI algorithm is crucial for making virtual drafting compelling for human players. As eight players engage in a draft, they are competing for synergistic decks, each trying to settle into one of the clusters on a synergy plot (known as deck archetypes). As a result of this competition, the final decks can be expected to be most streamlined and powerful if each player commits to a certain archetype, freeing cards that belong to other archetypes to other players. This interplay between competitive and collaborating drafting explains the demand for good drafting bots that is repeatedly expressed by players in online discussion venues [https://www.reddit.com/r/MagicArena/comments/b31449/as_good_as_arena_is_draft_still_isnt_real_magic/], as drafting against weak players does not feel as productive and rewarding as drafting against good drafters.

# Goals for drafting agents

Using the data described above, we designed drafting agents that approximate the behavior of human players. In other words, we trained bots to predict the card that was actually picked by a human player at each stage of a draft, given the choice of cards in the pack, and cards already in the collection. 

# Drafting agents

We constructed five different drafting agents which implement different drafting strategies. Two of these agents, **RandomBot** and **SimpleBot**, serve as baselines to compare other bots against. They implement, respectively, random card-picking, and card-ranking based on a simple heuristics. The other three bots use more complex strategies. **DraftsimBot** ranks cards based on heuristic estimations of their strength, but also accounting for whether their color matches the color of cards already in the  agent’s collection. **BayesBot** ranks cards based on estimated log-likelihoods of human users from the Draftsim dataset picking cards from a given pack, given the current collection. **NNetBot** ranks cards based on the output of a deep neural network trained to predict human choices in the Draftsim dataset (Table #). The agents are described in detail below.


![](https://paper-attachments.dropbox.com/s_3E11CDC24047F49065A86D936DF62D9D76CC43487E9B96F1F6E4D5C159806FE4_1581008041008_image.png)

## RandomBot: Random drafting

As the lowest baseline to compare against, we constructed a bot that ranks all cards in a pack randomly.

## SimpleBot: Simple heuristics

As a more realistic baseline, we constructed a bot that uses simple heuristics to emulate the simplest drafting strategy often used by inexperienced human players. SimpleBot always drafts the rarest card in the pack first. To break ties between cards of the same rarity, it randomly chooses between all cards whose color matches the most common color in the bot’s current collection. 

## DraftsimBot: Complex heuristics

The current Draftsim algorithm ranks cards based on approximations of individual card strength provided by a human expert, as well as on whether each card matches the most common colors among the stronger cards in the current bot’s collection. The strength ratings are set in the [0, 5] range by a human annotator, and roughly correspond to the following basic classes: 

5.0 Premium rares
4.0 Powerful rares
3.5 Powerful uncommons
3.0 Premium commons, removal
2.5 Playable creatures
2.0 Marginal creatures
1.5 Weak creatures, sideboard material
1.0 Rarely playable

The rating for a card $$c$$ is given by the scalar output of the function $$rating$$. The bot’s collection is represented as a vector of card names, $$d$$. Then, rating **is computed as the sum of a strength rating, $$strength(c)$$, and a color bias term, $$colorbias(c)|_d$$.

$$rating(c)|_d = strength(c) + colorbias(c)|_d$$

A card’s colored mana costs are expressed as a color vector, $$colors$$. The $$i$$th component of the color vector represents the required number of colored mana of the $$i$$th color. The indices 1, 2, 3, 4, 5 correspond to white, blue, red, green, and black, respectively.

$$colors(c)[i]=\textrm{required mana of ith color}$$

The pull of a card, $$pull(c)$$, is the amount that its strength exceeds a threshold for minimum card strength (2.0). For M19, a total of 53 cards (the weakest 20% of the set) do not meet this threshold. The reason for this thresholding is to exclude the effect of weakest cards on the drafting process (those cards that nobody wants to take, but that are still drafted towards the end of each of three draft phases).

$$pull(c)=max\big(0, strength(c) - 2.0\big)$$

A player’s commitment to a color, $$colorcommit$$, is calculated by summing the pull of cards in that player’s deck $$D$$ containing that color. 

$$colorcommit[i]|_D = \Sigma_{c\in D \ | \ colors(c)[i] > 0} \; pull(c)$$

The color bonus, $$C(i)$$, is a complex heuristic, computed from $$colorcommit$$, designed to balance picking individually powerful cards and committing to a two-color pair.  The color bonus is calculated differently early in the draft (the phase we call “speculation”), and later in the draft (the phase we call “commitment”).

The agent starts in the “speculation” phase, and during this phase, one-color cards of color $$i$$ are assigned a color bonus proportional to that player’s $$colorcommit$$ for this color (capped at 0.9): 


    $$colorbonus(c) = max(0.257 * colorcommit[i], \; 0.9)$$

Colorless cards are assigned a color bonus equal to the maximum color bonus of 1-color cards. Multicolored cards with 2-3 colors are assigned a rating equal to the color bonus of the cards colors minus the color bonus of other colors minus a multicolored penalty of 0.6. Multicolored cards with 4+ colors are ignored by the model and assigned a color bonus of 0 during the speculation phase. 


    $$colorbonus(c) = \Sigma (colorbonus(on) - colorbonus(off))-0.6$$

The speculation phase lasts until the playing agent is committed to 2+ colors, or until the fourth pick of the second pack, whichever comes first. The agent is considered “committed” to a color $$i$$ when the summary $$colorcommit[i]$$ exceeds $$3.5$$. A player can be committed to 0, 1, or 2+ colors. If a player is committed to 2+ colors, the two colors with greatest $$colorcommit$$ are referred to as that player’s primary colors. 

During the committed phase, on-color cards are assigned a large bonus of +2.0, while off color cards are assigned a penalty of -1.0 for each off color mana symbol beyond the first. 

Together, these rules create a behavior that roughly approximate a behavior of a human drafter, as the agent first goes for better cards, with an increasingly strong tendency to draft cards “in-color”, until at some point they “make their mind”, and switch to a more strict drafting strategy.

## BayesBot: Bayesian card-ranking

This agent explicitly relies on the statistics of collected human drafts, and gives priority to pairs of cards that were drafted together more frequently than by chance. In this sense, its logic is similar to the logic of set visualizations, presented above.

The Bayesian agent used two different strategies to pick the first card within a draft, and to pick all other cards. For the first card, when the collection is empty, it looks for the card that was most often picked first by human players, across all cards in the first pack. In practice, we look at all picks made by human players in the training set, count all cases $$m_{ij}$$ when both cards $$i$$ and $$j$$ were present in the pack, and all sub-cases $$m_{i>j}$$ when card $$i$$ was picked earlier than card $$j$$, to calculate the probability that card i is picked over card j: $$P(i>j) = m_{i>j}/m_{ij}$$ 

Then we use the Naive Bayes approximation, assuming independence of probabilities $$P(i>j)$$, and relying on pre-calculated log-likelihood values, to find the card with highest overall probability of being picked first:

$$i = \text{argmax}_i \prod_j P(i>j) = \text{argmax}_i \sum_j \log(m_{i>j}/m_{ij})$$

For all cards starting from the second card, the collection is not empty, and the picks of the agent are based on the maximization of total “synergy” between the newly picked card, and cards already in the collection. In practice, we use the training set to count all cases $$n_{ij}$$ when card i was present in the pack, and card j was already in the collection, and all sub-cases when after that the card i was actually drafted $$n_{i\rightarrow j}$$. The ratio of these two numbers gives a marginal probability that card i is drafted when card j is already collected:

$$P(i\rightarrow j\;|\;i\in pack \land j\in collection) = n_{i\rightarrow j}/n_{ij}$$.

In Naive Bayes approximation, the probability of drafting a card i given a full collection of cards $$\{j\}$$ is equal to a product of probabilities $$P(i\rightarrow j|i,j)$$ across all cards in $$\{j\}$$, as these probabilities are (naively) assumed to be independent. Therefore, the full probability of drafting a card i $$P(i)$$ is assumed to be equal to:

$$P(i) = \prod_j P(i\rightarrow j | i,j) = \prod_j n_{i\rightarrow j}/n_{ij}$$

The card with highest total probability is actually drafted, and the winner is also calculated using log-likelihood values:

$$i = \text{argmax}_i \prod_j n_{i\rightarrow j}/n_{ij} =$$ $$\text{argmax}_i \sum_j \log(n_{i\rightarrow j}/n_{ij})$$

In practice, these formulas are also vectorized as $$P = Q \cdot c$$, where $$Q_{ij} = \log(n_{i\rightarrow j}/n_{ij})$$ is a matrix of log-transformed probabilities of drafting card i from the pack to join card j already in the collection, and $$c$$ is the indicator vector of all cards in the collection ($$c_j$$ is the number of cards of type j present in the collection). Note, that while $$Q$$ seems to quantify “attraction” between the cards, it also indirectly encodes the rating of each card, as the values of $$Q_{ij}$$ are larger when the card i is strong and the probability of it being drafted $$P(i\rightarrow j)$$ is high. The matrix $$Q$$ is also asymmetric, as depending on the relative power and frequencies of cards i and j, the probabilities $$P(i\rightarrow j|i,j)$$ and $$P(j\rightarrow i|j,i)$$ may be very different from each other.


## NNetBot: Deep neural network card-ranking

For the Deep Neural Network agent, each pick is preprocessed into a vector representation. The card that user picked is represented by the target variable $$y \in \Re^S$$ : a one-hot encoded vector length S, where S is the number of cards in the set.

The independent variable x consists of three concatenated components: a one-hot encoded collection vector, a one-hot encoded pack vector, and (optionally) collection summary features. 

$$x = [x_{collection}, \; x_{pack}, \; x_{collection\_summary}]$$

The ith component of the collection vector is the number of cards i in that player’s collection. The pack vector is structured in the same way. 

The (optional) collection summary vector is derived from the collection vector and some of the readily available card properties, such as rarity, color, and converted mana cost. The collection summary vector did not meaningfully improve the performance of our models trained on large datasets. A full discussion is provided in the appendix. 

The collection information$$$$$$[x_{collection}, x_{collection\_summary}]$$ was fed into the input layer of a 3 layer-deep multi-layer perceptron (MLP) where each layer contained a linear, batchnorm, leakyrelu (0.01) and dropout (0.5) components. The pack vector $$[x_{pack}]$$ is multiplied by the output of the MLP to enforce the constraint that only cards in the pack can be selected. 

This model was trained for 25 epochs using cross entropy loss. 

# Comparisons of bot performance

To evaluate whether our agents drafted similarly to human players, we measured each drafting agent’s top-one accuracy for predicting actual user choices across all 21,590 drafts in the testing set. As an alternative, and potentially more sensitive measure of alignment between agent guesses and human picks, we also measured how low the human’s choice ranked in the list of each agent’s predictions (referred to as “pick distance”). The two baseline agents had mean per-draft accuracies of 22.15% for the RandomBot and 30.54% for the RaredraftBot, and performed worse than all three complex agents. The deep neural-network agent, NNetBot, performed the best with a mean per-draft accuracy of 48.32%, outperforming both original human-tuned Draftsim agent (DraftsimBot) that had an accuracy of 44.54%, and the BayesBot that has the accuracy of 43.36%. Similarly, the NNetBot had the lowest pick distance with a mean pick distance of 1.52, again outperforming the DraftsimBot (pick distance of 1.62), the BayesBot  (pick distance of 1.74), and the RaredraftBot (pick distance of 2.62). This indicates that, on average, the actual choice of human players was within the top three choices across all drafts for all complex bots. All differences between groups, for both top-one accuracy and pick distance, were significant (Tukey test p<2e-16).


![](https://paper-attachments.dropbox.com/s_3E11CDC24047F49065A86D936DF62D9D76CC43487E9B96F1F6E4D5C159806FE4_1581019196851_overall_accuracy.png)



![If we include this figure, we need to note that pick distance is not informative for the RandomBot.](https://paper-attachments.dropbox.com/s_3E11CDC24047F49065A86D936DF62D9D76CC43487E9B96F1F6E4D5C159806FE4_1581019212560_overall_distance.png)


In addition to measuring overall accuracy of each agent, we also measured its top-one accuracy for each turn during the draft (from 1 to 45). As pack size decreases as packs are depleted, from 15 cards to 1 card for picks 1 to 15, 16 to 30 and 31 to 45, the per-pick accuracy could better reflect the players’ shifting goals during the draft. The first card of each pack, for example, is often picked based on its rarity or its strength; cards in the middle of each pack are more likely to be picked based on their synergy with existing collections, while the last cards of each pack are typically not desirable to any player. Per-pick accuracy for all bots on the testing set is shown in Fig XXX.  


![](https://paper-attachments.dropbox.com/s_3E11CDC24047F49065A86D936DF62D9D76CC43487E9B96F1F6E4D5C159806FE4_1580782283249_pick_order_accuracy.png)


Per-pick accuracies further highlight the differences between our agents. First, the NNetBot consistently outperformed all other bots, while the DraftsimBot and BayesBot performed similarly. All three complex bots outperformed the two baseline bots. Second, all three bots performed better at the beginning than during the middle of every pack. This supports the assumption that players’ goals shift throughout the draft: players are more likely to pick cards based on estimated strength or rarity early on in each pack, and are more likely to pick cards for other reasons (such as synergy with their collection) during the middle of each pack. Third, the RaredraftBot performed far better than the RandomBot across all picks, showing that agents with simple heuristics make a far more compelling baseline for assessing drafting agents than a straightforward “randomized” solution. 

Lastly, we also compared each card’s estimated strength (the expert-provided rating of each card, as used by the DraftsimBot agent) to each agent’s accuracy in picking that card at a correct moment during the draft (Fig. X). As described earlier, “card ratings” proceeded from 0 (low), to just below 5 (high). Fig. 4 shows that the average pick accuracy was quite different both for different cards, and for different drafting agents. The RandomBot was only “good” with picking weakest cards, simply by virtue of having no choice, as these cards were the last to be drafted. The RaredraftBot and BayesBot agents did well with both weak cards and strongest cards, but struggled to pick medium-strength cards accurately. The expert-tuned DraftsimBot and especially the NNetBot outperformed all other agents for medium-strength cards, but actually did slightly worse for weakest and strongest cards. 

![](https://paper-attachments.dropbox.com/s_3E11CDC24047F49065A86D936DF62D9D76CC43487E9B96F1F6E4D5C159806FE4_1581440358144_card_ratings_vs_accuracy.png)


The most probable explanation for this surprising under-performance of two best AI agents for edge-case cards lies in a social phenomenon known as “raredrafting”. MtG cards are designed by Wizards of the Coast to fit several different game formats, so there is a small share of cards in every set that are objectively bad, or even completely unplayable in a drafting environment, but are prized and much sought after in other formats. In a real drafting situation a player is always tempted to take a useless but expensive card (e.g. a niche “mythical rare”) instead of a card that could help them to win a game. While all games on draftsim website were obviously virtual, it seems that a high share of players still “raredrafted”, and picked “bad rares” instead of a more reasonable card, as their first or second pick (either because it felt good, or because they tried to make the draft simulation more realistic). This “irrational” raredrafting behavior threw off two most efficient drafting agents (NNBot and DraftsimBot), but was embraced by the BayesianBot (that essentially went with a data-driven card rating for the first pick), and the RaredraftBot (by definition).

# Discussion

In this report, we compare several approaches to building human-like drafting agents for a single MTG set. We suggest that human-like drafting agents should be evaluated based on how well they approximate human choices in a set testing drafts. We show that a relatively neural network-based agent outperforms other agents, including those based on expert-tuned heuristics, and Naive Bias approach. 

At the same time, our approach has some limitations. First, as both the training and testing data were produced by humans drafting in a simulated environment (Draftsim website), it is possible that our data does not approximate competitive MTG drafting well. Some players may used the site to randomly click through the cards, to get an overall impression from the set. Some might have ranked cards using the “suggestions” function on the draftsim site, that displays expert card ratings, similar to those used by the DraftsimBot. Some users might have drafted suboptimally on purpose, trying to explore the flexiblity of the set (an exercise known as “forcing an archetype”). These limitations should not impact the bots’ ability to emulate human drafting, but they could hamper the bots’ ability to generalize to competitive drafting environments. Second, because deck-building algorithms for MTG are outside the scope of this work, we do not evaluate the strength of decks built from completed drafts in simulated matches, which may impact how well the agents generalize to competitive environments. Lastly, we performed all analyses on data from a single MTG set. Future work may investigate how well bots perform on different MTG sets. 

One important contribution of our paper involves benchmarking against heuristic-based bots. Previous research in automated deck-building has primarily benchmarked results against random strategies [refs], yet we observe a substantial performance benefit for simple heuristics compared to random chance. Based on these results, we propose that future drafting and deck-building work should benchmark results for complex agents against agents that employ simple heuristics. 

In addition to generalizing agent-based drafting to other MtG sets, and even mixes of different sets (known as “cubes”, [Ryan’s blog]), further work may include investigation of deck-building strategies from completed draft pools; the development of even more complex drafting agents; the analysis of typical inefficiencies in human drafting, and the study of aspects of cooperation and competition between agents during a drafting session. The creation of algorithms for building decks from completed drafts is a prerequisite for testing the strength of draft pools in simulated MtG games. This, in turn, can open the door for creating agents that rely on reinforcement learning and active deck space exploration [refs Alpha-Go style?]. On the other hand, this type of data analysis, and especially a comparison between human drafting and optimized drafting by AI agents, can help to identify unusual patterns in human play, that may help in the development of new MtG sets, or provide useful feedback to players that want to improve their drafting skills. Lastly, because drafting is a multiplayer environment where bots seek to specialize into certain strategies, future work could investigate how cooperation and competition affect drafting agents (for example, via phenomena known in the MtG lore as “signalling” and “hate-drafting” [refs?]). 

# References
#  

