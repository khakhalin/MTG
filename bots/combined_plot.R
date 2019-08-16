library(ggplot2)
library(ggthemes)
library(dplyr)
library(tidyr)

# Sets working directory
#setwd("~/Projects/draftsim/MTG/bots/output_files/") # Henry's computer
setwd("~/Projects/MTG/MTG-git/bots/output_files/") # Arseny's computer

dsum1 <- read.csv(file="Henrys_bots_summary.csv")
dsum1 <- dsum1 %>% select(-X)

data2 <- read.csv(file="Arsenys_bots_summary.csv") # a list of points it got right
dsum2 <- data2 %>% group_by(y) %>% summarise(m=n()) %>% mutate(m=m/max(m)) %>% rename(pick_num=y)
dsum2$bot <- "BayesianBot"
dsum2 <- dsum2 %>% mutate(pick_num=pick_num+1) %>% mutate(pack=floor((pick_num-1)/15))

dsum <- rbind(dsum1,dsum2)

ggplot(dsum, aes(pick_num,m,color=bot,group=interaction(pack,bot))) + 
  geom_line()+geom_point()+
  theme_classic()
