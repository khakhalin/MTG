# ---
# Compare (visualize) footprints of severeal different sets
# ---

require(dplyr)
require(ggplot2)
require(tidyr)

myFolder <- "C:/Users/Sysadmin/Documents/draftsim"

load(paste(myFolder,'/scale XLN.RData',sep=''))
temp <- scale
temp$set <- 'XLN'
allCards <- temp

load(paste(myFolder,'/scale DOM.RData',sep=''))
temp <- scale
temp$set <- 'DOM'
temp <- select(temp,-Legendary)  # This is the only set for some reason that had Legendaries labeled, 
                                 # so its easier to take them out, otherwise they don't combine with other sets
allCards <- rbind(allCards,temp)

load(paste(myFolder,'/scale M19.RData',sep=''))
temp <- scale
temp$set <- 'M19'
allCards <- rbind(allCards,temp)

load(paste(myFolder,'/scale GRN.RData',sep=''))
temp <- scale
temp$set <- 'GRN'
allCards <- rbind(allCards,temp)

allCards <- mutate(allCards,set=factor(set,levels=c('XLN','DOM','M19','GRN'))) # Put sets in correct order

myColors <- c("gray","tan2","blue","black","red","green","purple")
ggplot(allCards) + theme_minimal() + geom_point(aes(x,y,color=color)) +
  scale_color_manual(values=myColors) + xlab('') + ylab('') +
  theme(axis.text.x=element_blank(),         # Empty ticks, no gridlines
        axis.text.y=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  facet_grid(.~set) +
  guides(color=FALSE)
