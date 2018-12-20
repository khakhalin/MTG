Journal of MTG ideas
========================================

## Sep 23 2018

So what we need is:

1) a runnable case (a stand-alone program or a notebook - doesn't matter) that can be asked to run some bots on a draftsim dump, and calculate losses

2) running here means going through the dump, reconstruct the boosters, simulate the draft, calculate resulting hands, then compare "human" hand to the hand actually drafted by a human, calculate the loss

3) for loss, I think we should calculate the final result loss (% of cards in the final pile that matched human draft if bots were left on their own), and card-by-card loss (if all cards prior matched the human draft, and only this current card is proposed by a bot). This actually changes the code for (2) a bit, as we'd have to keep track of 2 alternative set of boosters and piles: a sequence actually drafted, and a sequence would-be drafted. But it feels necessary if we are about to compare bots to humans.

4) for bots, let's go with 3 options: a) current draftsim bots, aka DanDan bots b) bayesian bot, c) low-dim bot that uses MDS embedding results & card ranks, weighted with an optimized pick-by-pick vector length 14*3, to calculate the proposed cards. We've talked about this bot before, and we can discuss the bests way to optimize the "pick vector" later

5) ideally we should be able to assign bot logic to diff bots separately, because if bayes bot drafts well against DanDan bots, it does not necessarily guarantee that it will draft equally well against other Bayesian bots. I mean, most probably it'll be almost the same, but that's something we may be asked about.

Once we have this, and calculate some sample losses, it will mean that we are close enough to churning out a paper, and I'll draft a 3-4 pages description of all that, with some nice pics.

In the meanwhile, we'll have some finishing touches:

6) Finalize rank calculation for the low-dim bot, based on the directed graph calculation we described earlier (the one that uses Bradley-Terry assumptions, but uses pagerank-style process instead of max likelihood - I think it's safer that way). And, Bobby, even if high ranks are noisy, that's totally fine; all that matters is that the low-dim bot picks good cards on first 2 picks or so, as after that synergies will also lead it, because in the MDS plot all fancy cards are on the periphery. It's a peculiar feature or our MDS projection - the rank is indirectly encoded there as a distance from the center, so my prediction is that optimized low-dim bots will be really 90% MDS-driven, and only 10% or so rank-driven. That's also worth describing in the paper btw!

7) Add denoising to bayesian p_ij and low-dim d_ij estimations, by doing 2 passes through the set: one to calculate a proxy, 2nd to ignore "stupid decks". By that time I will have played with this as well, and look at distributions, so it will be easy.

8) Write a program that would split the total dump into, say, 50 pieces, so that we could calculate 50 losses for each set, rather than 1, and have proper plots with more than one value on each =]

9) Run this whole thing on 4 blocks we will have had by then (XLN, DOM, M19, RVC)

And that's all we need for a paper data-wise, I believe. We'll make it short and sweet.

Tell me what you think about it, and what would be your deadlines of preference? I don't think it is too urgent, as I'm trying to finish my current network science paper, but it would be nice to have it done some time this fall, I think. The sooner we do it, the sooner we can give it to Keith, ask for his feedback, figure out where and how to present it, etc. (We should def show it to Keith privately before publishing the pre-print). 

With this in mind, the paper may look like:
1) brief description of the situation: mtg, decks, draft environment, what bots need to do
2) translating into abstractions, closer to math: synergies, ranks, dimensionality of everything, type of data we have
3) ways to mine for synergies and ranks: some nice visuals for different sets (our signature mds pics); also something for ranks and picks (tbc) - maybe a graph-based ranking (now as I can Python, I'll play with it some more)
4) Description of 3 bots (for now I'm thinking of 3, but tbc): manual bot (current); Bayesian bot (described somewhere); light bot (my original one that receives only ranks and 2D or 3D synergies, and crawls in this space)
5) Comparison of performance of these 3 bots
Format (according to KO'H): 6 pages, in two columns. Visuals are important :smiley:
Authors: tbc, but I'd say Bobby first (as the most needy), then 2 Dans and me in some order? we'll figure this out, not that important
Venues: Keith recommended several conferences.
a) One option is AAAI workshops that apparently happen 2 times a year in Stanford?
http://www.aaai.org/Conferences/conferences.php
b) Game Developers Conference
https://www.gdconf.com/
c) The one he most recommended, happens in Florida in spring
https://www.aaai.org/ocs/index.php/FLAIRS/index/schedConfs/archive (edited)
I haven't found the site for the next one yet, but he said submission deadline for the Florida one about in December, maybe late November. Then it is acccepted (or not) around Feb, and the conference itself is in May
He recommended writing everything up, and just submitting it. If it is rejected, we'll know what to concentrate on.
So, to write the paper, we need:
i) Have the bots coded
ii) Have access to data beyond the first booster - that is, full picks for humans with pick order saved to SQL.
iii) Actually run all computational experiments
iv) Nice visuals
v) Write it up
For now I see (iii) as a bottleneck. I can start working first on visuals (including rankings), and then on bot testbed (@Bobby, that is, unless you have it coded already). Even before (iii) is implemented, we can test bots on first 13 cards. It won't tell us much, but we can build the testing environment, and have it ready.
Once visuals are ready, together we can write up 70% of the paper, but to finish it, we'll need these last pieces (testing, bechmarking)
Having it done by late-Nov is ambitious, but it feels sort of almost-doable, what do you think? Please share your opinions :smiley:
(Also at some point we need to find actual info about the conference deadlines and all, see into the rules, etc)

## Sep 18 2018

Bayesian pseudocode:

```
n <- number of cards
seenBP <- zeros(n,n)
seenBB <- zeros(n,n)
pickB <- zeros(n,n)
pickP <- zeros(n,n)
for each half-picked Booster and "current" Pile of already drafted cards
    the card that actually got picked -> k
    
    for each card i in Booster
        if(i~=k)
            pickB(i,k)++        # k won over i in this booster 
            seenBB(i,k)++       # and they were seen together
            seenBB(k,i)++       # this matrix is symmetric
        
        for each card j in Pile
            seenBP(i,j)++       # these two cards (one in Booster, one in Pile) were seen together. Note that here m~=m'
            if(i==k)
                pickP(k,j)++    # but only this one got picked
                
                
# Once this is done for all drafts, we'll have two conditional probabilities
# P_BB(k drafted over i | k and i seen together) = pickB(k,i)/seenBB(k,i)
# P_BP(k drafted | j was already in the pile) = pickP(k,j)/seenBP(k,j)
# During the actual draft:
for each card k in Booster
    love(k) <- 0
    for each card i in Booster, i~=k
        love <- love + log(pickB(k,i)) - log(seenBB(k,i))
    for each card j in Pile
        love <- love + log(pickP(k,i)) - log(seenBP(k,i))
        
card to draft <- argmax(love(i))
# Obviously we pre-calculate all log(), it's just for clarity here
```

## Sep 17 2018

I was reading about the Bayesian analysis of Federalist papers ( https://github.com/mkmcc/FederalistPapers ) and suddenly realized that there's a very simple and elegant approach to boting what we should definitely try. Let's consider card picks as a probabilistic event, and pick the card with highest "probability" of being drafted. It means that for every card k, using the Bayes theorem, the probability of it being drafted can be calculated as P = 1/m * prod_i{P_h(k|i) * prod_j(P_b(k|j) where 1/m is a prior (if we are currently seeing m cards), P_h(k|i) is a conditional probability of drawing card k if you already have card i in your hand, and P_b(k|j) is a probability of drawing card k if you have card a "competing" j in the booster.

Imagine a simplistic case: you have 2 cards in front of you (k and j), you need to pick one of them, and you already drafted card i. You know that the odds (actually - just statistics) of drafting card k over j is 2:1 (it's a better card). Odds of drafting k if you have i in your hand is 1:3 (color conflict), while drafting j if i is in hand is 1:1 (no synergy, but no conflict). In this case you'd draft k, because 2/3 is higher than 1/2.

And both probabilities are easy to calculate. P_h(k|i) = P(ki)/P(i) - something I already calculate in my matrix. We'll only need to calculate P_b(k|j) = P(kj)/P(j) based on the draft reconstruction, and instead of translating them into ratings we'll use them directly!

Moreover, in practice of course nobody is calculating prod(), as we can take log() of each of them, and use sum(). Max(prod(x)) will still be achieved at the same card for which sum(log(x)) will be achieved!

But see what's happening here: unlike in my current "idea of an approach", this one is symmetrical towards hand and booster synergies and "anti-synergies". Which means that it will change logic of choice automatically! For the first card it will be entirely rating ( log(P_b(k|j)) ) , but already for the 2nd one it will be a mix of both. Further into the booster, synergies will become more and more important; once you start 2nd booster, rating and synergy will be approximately equally important (as you'll have 14 card in hand, and 13 card in booster to compare to). But then it will shift over to synergy again. And for the first booster it's highly unlikely that any single card will win over ~28 synergies.

There's no guarantee of course that it will draft exactly like a human, or better than any other "fine-tuned" bot, but the sheer simplicity of this approach means that I really like to try it! I'm lazy and I don't want to code draft reconstructor from scratch in Python, and also I don't want to do it in R as it will take forever, but once you share Python code, I'll be happy to code this thing. Unless you want to code it first of course =]

And see, it also takes care of "self-distances", it takes care of many intuitions we had sort of "automatically". It may be nice!

## Mar 3 2018

That's true. For now I was thinking that at every step i'd pick a card with min(L) 
where L = w(t)*distance + (1-w(t))*rank
where w(t) is an arbitrary weight function of what pick it is within the draft (t is an integer that runs from 1 to 14*3)
distance = sum_i{d_ij} where i runs through all cards in a hand, j runs through all cards in a deck, and d_ij = 1/p(i,j) is reverse probability that cards type i and j were in the past drafted in the same deck.
rank is some sort of absolute card rank (similar to current logic, but data-driven)

There are several ways to calculate distance (directly or with dimensionality reduction), and there are several ways to calculate ranks, but it wouldn't change the main idea.

Which means that the total optimization space is 14*3 for w + n for ranks + n(n-1)/2 for distances . It's a lot, but not an awful lot. One could use different optimization techniques to fine tune it.