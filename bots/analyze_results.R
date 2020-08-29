library(ggplot2)
library(ggthemes)
library(dplyr)
library(tidyr)
library(RColorBrewer)

# Sets working directory
setwd("~/../Documents/Projects/Draftsim/MTG/bots/output_files") # Henry's computer
#setwd("~/Projects/MTG/MTG-git/bots/output_files/") # Arseny's computer

# Loads in data
exact <- read.csv("exact_correct.tsv", sep = "\t")
rank_error <- read.csv("rank_error.tsv", sep = "\t")
card_acc <- read.csv("card_accuracies.tsv", sep = "\t")
ratings <- read.csv("../../../data/standardized_m19/standardized_m19_rating.tsv", sep = "\t", stringsAsFactors = FALSE)
ratings$Rating <- as.numeric(ratings$Rating)

# Corrects DraftsimBot name
colnames(exact)[colnames(exact) == "ClassicBot"] <- "DraftsimBot"
colnames(rank_error)[colnames(rank_error) == "ClassicBot"] <- "DraftsimBot"
colnames(card_acc)[colnames(card_acc) == "ClassicBot"] <- "DraftsimBot"

# Sets explicit colors for each bot
pal <- brewer.pal(5, "Set1")
names(pal) <- colnames(card_acc[2:ncol(card_acc)])

# Appends card ratings to card accuracy values
card_acc$ratings <- ratings$Rating

# Plots overall accuracy across all drafts
draft_acc <- select(exact, -c(pick_num, human_pick))
draft_acc <- draft_acc %>% 
  gather(bot, correct, RandomBot:NNetBot) %>% 
  group_by(draft_num, bot) %>% summarize(draft_acc = sum(correct) / 45)
draft_acc$bot <- factor(draft_acc$bot, levels = c("RandomBot", "RaredraftBot", "BayesBot", "DraftsimBot", "NNetBot"))
ggplot(draft_acc, aes(x = bot, y = draft_acc)) +
  geom_boxplot() +
  xlab("Drafting bot") +
  ylab("Per-draft top-one accuracy") +
  theme_classic(base_size = 20)
ggsave("overall_accuracy.png", width = 10, height = 7)

# Prints mean accuracy
mean(draft_acc$draft_acc[draft_acc$bot == "RandomBot"])
mean(draft_acc$draft_acc[draft_acc$bot == "RaredraftBot"])
mean(draft_acc$draft_acc[draft_acc$bot == "BayesBot"])
mean(draft_acc$draft_acc[draft_acc$bot == "DraftsimBot"])
mean(draft_acc$draft_acc[draft_acc$bot == "NNetBot"])

# Computes one-way ANOVA and Tukey comparisons between all draft accuracies
anova_results <- aov(draft_acc ~ bot, data = draft_acc)
summary(anova_results)
TukeyHSD(anova_results)

# Plots overall rank error across all drafts
draft_error <- select(rank_error, -c(pick_num, human_pick, RandomBot))
draft_error <- draft_error %>% 
  gather(bot, error, RaredraftBot:NNetBot) %>% 
  group_by(draft_num, bot) %>% summarize(draft_error = sum(error) / 45)
draft_error$bot <- factor(draft_error$bot, levels = c("RaredraftBot", "BayesBot", "DraftsimBot", "NNetBot"))
ggplot(draft_error, aes(x = bot, y = draft_error)) +
  geom_boxplot() +
  xlab("Drafting bot") +
  ylab("Per-draft pick distance") +
  theme_classic(base_size = 20) 
ggsave("overall_distance.png", width = 10, height = 7)

# Prints mean accuracy
mean(draft_error$draft_error[draft_error$bot == "RandomBot"])
mean(draft_error$draft_error[draft_error$bot == "RaredraftBot"])
mean(draft_error$draft_error[draft_error$bot == "BayesBot"])
mean(draft_error$draft_error[draft_error$bot == "DraftsimBot"])
mean(draft_error$draft_error[draft_error$bot == "NNetBot"])

# Computes one-way ANOVA and Tukey comparisons between all draft accuracies
anova_results <- aov(draft_error ~ bot, data = draft_error)
summary(anova_results)
TukeyHSD(anova_results)

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
  scale_color_manual(name = "Bot", values = pal)
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
  scale_color_manual(name = "Bot", values = pal)
ggsave("pick_ranks_unnormalized.png", width = 10, height = 7)
ggplot(pick_ranks, aes(pick_num,m/cards_in_pack,color=bot,group=interaction(pack,bot))) + 
  geom_smooth(se=F)+ # Loess
  geom_point() +
  xlab("Pick number") +
  ylab("Pack size-normalized average rank error") +
  labs(color = "Bot") +
  theme_classic(base_size = 20) +
  scale_color_manual(name = "Bot", values = pal)
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
  theme_classic(base_size = 20) +
  scale_color_manual(name = "Bot", values = pal)
ggsave("card_ratings_vs_accuracy.png", width = 10, height = 7)


