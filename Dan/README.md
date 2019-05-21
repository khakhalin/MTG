# draftsimtools
draftsimtools is a python package that can help with the development of draftsim bots. 

An example use case is shown in <b>draftsimtools_interactive.ipynb</b>

Helper functions are available in <b>load.py</b>:  
```
  ds.create_set(set_csv_path) - Read card and rating information. Returns pandas dataframe.  
  ds.fix_commas(set_var, drafts) - Remove problematic comma and quote characters from cardnames.  
  ds.create_rating_dict(set_df) - Store draft information as {"cardname" : [color_vector, rating]}. Useful for efficient rating updates.  
  ds.process_drafts(draft) - Process draft into a list of packs shown to the human drafter. The human pick is always the first card in the pack.  
```

A base bot class is available in <b>bot.py</b>:  
This bot makes picks and can compute the recommendation from the current draftsim model.  

A simple bot is shown in <b>sgd_bot.py</b>:  
This bot optimizes the ratings of the draftsim model using SGD minimization.  

Future bots can extend the bot.py class. This allows for the re-use of draft reconstruction logic and draftsim ratings.  
