R Analyses of Magic the Gathering data
========================================

## Drafts from Draftsim

I was lucky to get access to drafting logs from [Draftsim.com](http://draftsim.com) site, and play with this data in R. Together with a team of two more people (Dan Troha and Bobby Mills) we wrote up these analyses as a series of blog posts. As of Nov 2018 we published 3 posts:

1. [Basic analysis](https://draftsim.com/blog/draft-data-analysis/) - introducing the co-drafting distances, and MDS scaling.
2. [Changes in drafting](https://draftsim.com/blog/m19-format-evolution/) : drafting of the same set early in the season, compared to late  in the season. Also, statistics of color preferences (aka Guilds) among players.
3. [Looking for controversial cards](https://draftsim.com/blog/guilds-of-ravnica-first-look/) that are loved by some people, but disliked by others (original idea by Bobby Mills). This analysis turned to be rather fancy, as I ran into a couple of mathematical paradoxes.

Code:

* Basic analysis in R: [markdown notebook](draftsim_analysis.Rmd), and [the same thing rendered in HTML](http://htmlpreview.github.io/?https://github.com/khakhalin/MTG/blob/master/draftsim_analysis.nb.html) (with ggplot graphs and everything).

To be continued!
