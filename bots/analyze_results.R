library(ggplot2)
library(ggthemes)
library(dplyr)
library(tidyr)

# Sets working directory
setwd("~/../Documents/Projects/Draftsim/MTG/bots/output_files") # Henry's computer
#setwd("~/Projects/MTG/MTG-git/bots/output_files/") # Arseny's computer

# Loads in data
exact <- read.csv("exact_correct.tsv", sep = "\t")
fuzzy <- read.csv("fuzzy_correct.tsv", sep = "\t")
rank_error <- read.csv("rank_error.tsv", sep = "\t")
card_acc <- read.csv("card_accuracies.tsv", sep = "\t")
ratings <- read.csv("../../../data/standardized_m19/standardized_m19_rating.tsv", sep = "\t")

# Appends card ratings to card accuracy values
card_acc$ratings <- ratings$Rating

# Plots average differences in pick order. Makes sure that no
# lines are drawn between the last pick on one pack and the 
# first pick of the next pack by adding an additional group

# Plots accuracy by pick order
dsum <- gather(exact, bot, guess, -c(draft_num,pick_num,human_pick)) %>% 
  group_by(bot,pick_num) %>% summarize(m=mean(guess))
dsum <- dsum %>% mutate(pack=floor((pick_num-1)/15))
ggplot(dsum, aes(pick_num,m,color=bot,group=interaction(pack,bot))) + 
  #geom_line(size = 1) +
  #geom_smooth(se=F, method = "lm", formula = y ~ splines::bs(x,df=5,degree=4)) +
  geom_smooth(se=F)+ # Loess
  geom_point() +
  xlab("Pick number") +
  ylab("Average top-one accuracy") +
  labs(color = "Bot") +
  theme_classic(base_size = 20) +
  scale_color_brewer(palette="Set1")
write.csv(dsum, file = "bot_summaries.csv")
ggsave("pick_order_accuracy.png", width = 10, height = 7)

# Plots rank error
temp <- select(rank_error, -c(RandomBot, RaredraftBot))
pick_ranks <- gather(temp, bot, rank, -c(draft_num,pick_num,human_pick)) %>% 
  group_by(bot,pick_num) %>% summarize(m=mean(rank))
pick_ranks <- pick_ranks %>% mutate(pack=floor((pick_num-1)/15))

# Gets cards in each pack
pick_ranks$cards_in_pack <- rev(((pick_ranks$pick_num - 1) %% 15) + 1)

ggplot(pick_ranks, aes(pick_num,m,color=bot,group=interaction(pack,bot))) + 
  geom_smooth(se=F)+ # Loess
  geom_point() +
  xlab("Pick number") +
  ylab("Average rank error") +
  labs(color = "Bot") +
  theme_classic(base_size = 20) +
  scale_color_brewer(palette="Set1")
ggsave("pick_ranks_unnormalized.png", width = 10, height = 7)
ggplot(pick_ranks, aes(pick_num,m/cards_in_pack,color=bot,group=interaction(pack,bot))) + 
  geom_smooth(se=F)+ # Loess
  geom_point() +
  xlab("Pick number") +
  ylab("Pack size-normalized average rank error") +
  labs(color = "Bot") +
  theme_classic(base_size = 20) +
  scale_color_brewer(palette="Set1")
ggsave("pick_ranks_normalized.png", width = 10, height = 7)

# Plots card ratings against bot accuracies
card_df <- gather(card_acc, bot, acc, -c(human_pick, ratings)) %>% 
  group_by(bot)
card_df <- card_df[card_df$ratings >= 0,] # Removes basic lands
ggplot(card_df, aes(x = ratings, y = acc, color = bot)) +
  geom_smooth(se=F) + 
  xlab("Draftsim rating") +
  ylab("Per-card accuracy") +
  labs(color = "Bot") +
  theme_tufte(base_size = 20) +
  scale_color_brewer(palette="Set1")
ggsave("card_ratings_vs_accuracy.png", width = 10, height = 7)


