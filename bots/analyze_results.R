library(ggplot2)
library(ggthemes)
library(dplyr)
library(tidyr)

# Sets working directory
#setwd("~/Projects/draftsim/MTG/bots/output_files/") # Henry's computer
setwd("~/Projects/MTG/MTG-git/bots/output_files/") # Arseny's computer

# Loads in data
exact <- read.csv("exact_correct.tsv", sep = "\t")
fuzzy <- read.csv("fuzzy_correct.tsv", sep = "\t")
rank_error <- read.csv("rank_error.tsv", sep = "\t")
card_acc <- read.csv("card_accuracies.tsv", sep = "\t")

# Plots average differences in pick order. Makes sure that no
# lines are drawn between the last pick on one pack and the 
# first pick of the next pack by adding an additional group


# Arseny's version:
dsum <- gather(exact, bot, guess, -c(draft_num,pick_num,human_pick)) %>% 
  group_by(bot,pick_num) %>% summarize(m=mean(guess))
dsum <- dsum %>% mutate(pack=floor((pick_num-1)/15))
ggplot(dsum, aes(pick_num,m,color=bot,group=interaction(pack,bot))) + 
  geom_line()+geom_point()+
  theme_classic()
write.csv(dsum, file = "Henrys_bots_summary.csv")

# Henry's version:
exact_pick_order <- exact %>% 
  group_by(pick_num) %>%
  summarize(random_pick_acc = mean(RandomBot),
            raredraft_pick_acc = mean(RaredraftBot),
            classic_pick_acc = mean(ClassicBot)) %>%
  gather(key = "bot", value = "accuracy", 
         random_pick_acc, raredraft_pick_acc)
exact_pick_order$line_group <- c(rep(1, 15), rep(2, 15), rep(3, 15))

ggplot(exact_pick_order, aes(x = factor(pick_num), y = accuracy, 
                             group = interaction(bot, line_group), 
                             color = bot, shape = bot)) +
  geom_point(size = 3) +
  geom_line() +
  scale_color_manual(name = "Bot", 
                     labels = c("Random", "Raredraft", "Classic"),
                     values = c("Black", "Blue", "Red")) +
  scale_shape_manual(name = "Bot", 
                     labels = c("Random", "Raredraft", "Classic"),
                     values = c(1, 2, 3)) +
  xlab("Pick number") +
  ylab("Average exact accuracy") +
  theme_tufte(base_size = 20) +
  theme(legend.position = c(0.1, 0.9),
        axis.text.x = element_text(angle = 45, size = 14))

#ggsave("pick_order_accuracy.png", width = 10, height = 7)

