R Analyses of Magic the Gathering data
========================================

This is a collection of scripts to analyze draft logs from [Draftsim.com](http://draftsim.com) site. The project is supported by a small team of people (Arseny Khakhalin, Bobby Mills, Dan Trocha, and Henry Ward), and we are gradually writing the results of these analyses up, as a series of blog posts. As of Nov 2018 we published 3 posts:

1. [Basic analysis](https://draftsim.com/blog/draft-data-analysis/) - introducing the co-drafting distances, and MDS scaling.
2. [Changes in drafting](https://draftsim.com/blog/m19-format-evolution/) : drafting of the same set early in the season, compared to late  in the season. Also, statistics of color preferences (aka Guilds) among players.
3. [Looking for controversial cards](https://draftsim.com/blog/guilds-of-ravnica-first-look/) that are loved by some people, but disliked by others (original idea by Bobby Mills). This analysis turned to be rather fancy, as I ran into a couple of mathematical paradoxes.

Code commentaries:

* Basic analysis in R: [markdown notebook](draftsim_analysis.Rmd), and [the same thing rendered in HTML](http://htmlpreview.github.io/?https://github.com/khakhalin/MTG/blob/master/draftsim_analysis.nb.html) (with ggplot graphs and everything).

To be continued!

![rotating cube](https://draftsim.com/blog/wp-content/uploads/2018/08/rotating-m19-cube.gif)
