require(dplyr)
require(ggplot2)
require(tidyr)
require(ggrepel)

colorRarity <- c('black','red','gold2','gray50')
colorColor <- c("gray","purple","tan2","blue","black","green","red") # Bobby's messed up sequence of colors

plotTitle = 'GRN'

#d <- read.csv("draftsim/jupyter/controversial_cards_m19.csv",header=T)
d <- read.csv("draftsim/jupyter/controversial_cards_grn.csv",header=T)
#d <- read.csv("draftsim/jupyter/controversial_cards_data_onColor.csv",header=T)
names(d)
d <- subset(d,avg<16) # Remove weird cards that were never actually drafted
d <- subset(d,rarity!='Basic Land')

#dbot <- read.csv("draftsim/jupyter/controversial_cards_m19_bot.csv",header=T)
dbot <- read.csv("draftsim/jupyter/controversial_cards_grn_bot.csv",header=T)
#dbot <- read.csv("draftsim/jupyter/controversial_cards_data_onColor.csv",header=T)
names(dbot)
dbot <- subset(dbot,avg<16) # Remove weird cards that were never actually drafted
dbot <- subset(dbot,rarity!='Basic Land')

# Normal pretty plot:
ggplot(d,aes(avg,var)) + theme_bw() + 
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  scale_x_continuous(limits=c(1,13),breaks = seq(2, 12, by = 2)) +
  xlab('Average pick order') + ylab('Variance of pick order') + ggtitle(plotTitle) +
  theme(axis.text.x=element_blank(),         # Empty ticks, no gridlines
        axis.text.y=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  NULL

# Plot with card colors:
ggplot(d,aes(avg,var)) + theme_bw() + 
  geom_point(aes(color=factor(color)),alpha=0.8) +
  scale_color_manual(values=colorColor) +
  scale_x_continuous(limits=c(1,13),breaks = seq(2, 12, by = 2)) +
  xlab('Average pick order') + ylab('Variance of pick order') + ggtitle(plotTitle) +
  theme(axis.text.x=element_blank(),         # Empty ticks, no gridlines
        axis.text.y=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  NULL

# Same plot with labels:
ggplot(d,aes(avg,var)) + theme_bw() + 
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  scale_x_continuous(limits=c(1,13),breaks = seq(2, 12, by = 2)) +
  xlab('Average pick order') + ylab('Variance of pick order') + ggtitle(plotTitle) +
  geom_text_repel(aes(avg,var,label=name),color='black',size=2,box.padding = 0.01, point.padding = 0.01) +
  NULL


# Top cards by rating
d %>% arrange(avg) %>% head
# Bottom cards by rating
d %>% arrange(desc(avg)) %>% head
# Most controversial:
d %>% arrange(desc(var)) %>% head

# Troubleshooting the unexpected early-drafting of stuff by humans
sum(d$count*d$avg)/sum(d$count)
sum(dbot$count*dbot$avg)/sum(dbot$count)
nrow(d)
nrow(dbot)

dbot2 <- select(dbot,name,mbot=avg,vbot=var,countbot=count)
head(dbot)
d <- inner_join(d,dbot2,by="name")
head(d)
d$madj <- d$avg-d$mbot
d$vadj <- d$var-d$vbot

sum(d$count*d$avg)/sum(d$count)
sum(d$countbot*d$mbot)/sum(d$countbot)
sum(d$count)
sum(d$countbot)

# Plot of differences, humans vs bot
ggplot(d,aes(-madj,vadj)) + theme_bw() + 
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  xlab('Uniquely human love') + ylab('Uniquely human uncertainty') +
  #geom_text_repel(aes(label=name),color='black',size=2,box.padding = 0.01, point.padding = 0.01) +
  NULL

# Direct comparison of pick orders
ggplot(d,aes(avg,mbot)) + theme_bw() +
  geom_line(data=data.frame(x=c(1,14)),aes(x,x),color="gray") +
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity)

# Do log scale
ggplot(d,aes(-madj,vadj)) + theme_bw() + 
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  xlab('Human extra preference') + ylab('Human extra variance') +
  scale_y_log10()


# --- A few debugging plots
# Total cards drafted, by humans and bots, comparison
ggplot(d,aes(count,countbot)) + theme_bw() + 
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) + 
  geom_line(data=data.frame(x=c(0,15000)),aes(x,x),color="gray") +
  #geom_text(aes(label=name),color='black',size=2)
  NULL

# Overall shapes of drafts, bots vs humans
ggplot(d) + theme_bw() +
  geom_point(aes(count,avg),color='red',alpha=0.5) +
  geom_point(aes(countbot,mbot),color='black',alpha=0.5)

# The best troubleshooting graph showing how bot draft results compare to human
d2 <- gather(select(d,name,human=avg,ch=count,bot=mbot,cb=countbot),"type","m",-name,-ch,-cb)
d2 <- mutate(d2,c=ifelse(type=="bot",cb,ch))
head(d2)
ggplot(d2,aes(c,m,color=type)) + theme_bw() +
  geom_line(aes(group=name),color="gray",alpha=0.5) +
  geom_point(alpha=0.5)


### --- Other FAILED attempts to smoothen out the parabola of card controversies
# Maybe let's try to draw a backbone through the curve, and subtract it?
# Spoiler: doesn't work that well, and is overall confusing
model = loess(data=d,var~avg)
d$backbone = predict(model,data.frame(avg=d$avg))

d$adj = d$var-d$backbone

# Adjusted:
ggplot(d,aes(avg,adj)) + theme_bw() + 
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  scale_x_continuous(limits=c(1,13),breaks = seq(2, 12, by = 2)) +
  xlab('Average pick order') + ylab('Adjusted variance') +
  theme(panel.grid.major = element_blank(),panel.grid.minor = element_blank())

# Adjusted with ggrepel
ggplot(d,aes(avg,adj)) + theme_bw() + 
  geom_point(aes(color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  scale_x_continuous(limits=c(1,13),breaks = seq(2, 12, by = 2)) +
  xlab('Average pick order') + ylab('Adjusted variance') +
  theme(panel.grid.major = element_blank(),panel.grid.minor = element_blank()) +
  geom_text_repel(aes(avg,adj,label=name),size=2,box.padding = 0.01, point.padding = 0.01)


# And here I tried to manually adjust lower and higher bounds.
# This approach failed, as while they look kinda parabolic, they are not actually parabolas,
# so stretching points from a curl into a square didn't work.
x <- 1:12
ggplot(d) + theme_bw() + 
  geom_point(aes(avg,var,color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  geom_line(data=data.frame(x=x,y=(x-1)*(20-x)/20*0.7),aes(x,y)) +
  geom_line(data=data.frame(x=x,y=(x-1)*(16-x)/20*6),aes(x,y)) +
  scale_x_continuous(limits=c(1,13),breaks = seq(2, 12, by = 2))

d <- mutate(d,low = (avg-0.9)*0.6, 
              hi  = (avg-0.9)*(16-avg)/20*6)
d$relvar <- (d$var-d$low)/(d$hi-d$low)

ggplot(d) + theme_bw() + 
  geom_point(aes(avg,relvar,color=rarity),alpha=0.8) +
  scale_color_manual(values=colorRarity) +
  scale_x_continuous(limits=c(1,13),breaks = seq(2, 12, by = 2))


# --- Show controversial cards on the synergy plot

load("draftsim/scale GRN.RData")

scale2 <- inner_join(scale,dplyr::select(d,name,avg,var,madj,vadj),by="name")
require(viridis)

ggplot(scale2) + theme_bw() + geom_point(aes(x,y,color=avg)) +
  xlab('') + ylab('') +
  theme(axis.text.x=element_blank(),         # Empty ticks, no gridlines
        axis.text.y=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  scale_color_viridis() +
  ggtitle("GRN, Synergy plot, colored by mean pick")

ggplot(scale2) + theme_bw() + geom_point(aes(x,y,color=var)) +
  xlab('') + ylab('') +
  theme(axis.text.x=element_blank(),         # Empty ticks, no gridlines
        axis.text.y=element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  scale_color_viridis(option="plasma") +
  ggtitle("GRN, Synergy plot, colored by var pick")

