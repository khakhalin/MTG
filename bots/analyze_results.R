library(ggplot2)
library(ggthemes)
library(dplyr)
library(tidyr)

# Sets working directory
#setwd("~/../Documents/Projects/Draftsim/MTG/bots") # Henry's computer
setwd("~/Projects/MTG/MTG-git/bots/output_files/") # Arseny's computer

# Loads in data
exact <- read.csv("exact_correct.tsv", sep = "\t")
fuzzy <- read.csv("fuzzy_correct.tsv", sep = "\t")
rank_error <- read.csv("rank_error.tsv", sep = "\t")
card_acc <- read.csv("card_accuracies.tsv", sep = "\t")

# Plots average differences in pick order. Makes sure that no
# lines are drawn between the last pick on one pack and the 
# first pick of the next pack by adding an additional group


# Plots accuracy by pick order
dsum <- gather(exact, bot, guess, -c(draft_num,pick_num,human_pick)) %>% 
  group_by(bot,pick_num) %>% summarize(m=mean(guess))
dsum <- dsum %>% mutate(pack=floor((pick_num-1)/15))
ggplot(dsum, aes(pick_num,m,color=bot,group=interaction(pack,bot))) + 
  geom_line(size = 1) +
  #geom_smooth(se=F, method = "lm", formula = y ~ splines::bs(x,df=5,degree=4)) +
  geom_point() +
  xlab("Pick number") +
  ylab("Average exact accuracy") +
  labs(color = "Bot") +
  theme_classic(base_size = 20) +
  scale_color_brewer(palette="Set1") +
  NULL
write.csv(dsum, file = "Henrys_bots_summary.csv")
ggsave("pick_order_accuracy.png", width = 10, height = 7)

