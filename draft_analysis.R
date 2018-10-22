# --------
# Main draft analysis script
# Currently consists of several parts that need to be executed manually, in a correct order.
# Which is super-annoying. Also the middle part (the reconstruction) is extremely slow,
# and takes several hours, while Python runs same analysis in about 10 seconds. So it will be removed. Soon.
# --------

#install.packages("dplyr")
#install.packages("ggplot2")
require(dplyr)
require(ggplot2)
require(tidyr)

myFolder <- "C:/Users/Sysadmin/Documents/draftsim" # There seems to be no good way to use relative addresses in R
#fileDb <- c("Draftsim Ratings - RIX","Draftsim Ratings - XLN")
#fileData <- "2018-02-23 Two days data from Draftsim.csv"
#fileDb <- "Draftsim Ratings - DOM"
#fileData <- "2018-04-16 Dominiaria initial data-2.csv"
#fileDb <- "Draftsim Ratings - M19"
fileDb <- "Draftsim Ratings - GRN"
#fileData <- "2018-07-23 M19 drafts.csv"
#fileData <- "2018-08-23 m19 drafts round 2.csv"
fileData <- "2018-10-05 GRN Draft Data 1.csv"
currentSet <- "GRN" # Options for now: "M19" "DOM" "XLN"

db <- NULL # Card database
for(iFile in 1:length(fileDb)){
  temp <- read.csv(file=paste(myFolder,"/",fileDb[iFile],".csv",sep=""), header=TRUE, sep=",")
  db <- rbind(db,temp)
}
db <- rename(db,name=Name,cost=Casting.Cost.1) # Simplify names
db <- distinct(db,name,.keep_all = TRUE)    # Remove reprints
db <- mutate(db,id=1:nrow(db))              # Add a column of newly defined id numbers
db <- mutate(db,name=gsub(",_","_",name))   # Fix card names with a comma in them
db <- mutate(db,name=sapply(name, tolower)) # Move all names to lowercase
db <- mutate(db,w = grepl("W",cost)*1,u = grepl("U",cost)*1,
                b = grepl("B",cost)*1,r = grepl("R",cost)*1,g = grepl("G",cost)*1) # Number of symbols for each mana in cost

# Load draft history. This may take a while (about a minute):
d <- read.csv(file=paste(myFolder,"/",fileData,sep=""), header=F, sep=",")

d <- rename(d,draftId=V1,set=V2,h1=V3,h2=V4,h3=V5,h4=V6,h5=V7,h6=V8,h7=V9,h8=V10) # Meaningful column names
d <- subset(d,set==currentSet)              # Only one type of drafts
d <- mutate(d,h1=gsub(",_","_",h1))         # Fix card names with a comma (only hand1 for now)

nDrafts <- nrow(d)
nCards <- nrow(db) # How many cards are there
pairs <- matrix(0L,nrow=nCards,ncol=nCards) # Co-occurence of cards. 0L makes it integer rather than double
prefs <- matrix(0L,nrow=nCards,ncol=nCards) # A matrix of card preferences (relations)
guild <- matrix(0L,nrow=5,ncol=5)           # Guild statistics
order <- rep(1:14,3)     # The order the cards were chosen (pick number for each card, in the final deck)
rank <- rep(0,nCards)    # Future card ranks
freq <- rep(0,nCards)    # How many times total this card was drafted
colorLetters <- c("w","u","b","r","g") # Mostly useful for debugging
colorHist <- NULL        # All consecutive colors will be stored here, for stats

if(1){ # So that the time measuring command would run together with the rest of the code when Ctrl-Entering
  tic <- Sys.time()
  for(iSession in 1:100){ # Uncomment for testing
  #for(iSession in 1:nDrafts){ # For each session
    if(iSession %% 100 == 0) {cat(sprintf('%d of %d\n',iSession,nrow(d)))} # Reporting
    
    temp <- sapply(d[iSession,]$h1,tolower)                # Lowercase everything
    s <- setNames(data.frame(strsplit(as.character(temp),",")),"name") # Get human hand (h1), explode by commas
    s <- inner_join(s,dplyr::select(db,name,id,w,u,b,r,g),by="name") # Full list of cards
    s <- subset(s,!is.na(s$id))                            # This shouldn't happen, but just in case, purge NAs
    colorVec = c(0,0,0,0,0)  # Vector of colors for this hand
    
    for(iCard in 1:nrow(s)) {                        # For every card in the deck
      iid <- s[iCard,]$id                            # This card's id
      colorVec <- colorVec + c(s[iCard,]$w,s[iCard,]$u,s[iCard,]$b,s[iCard,]$r,s[iCard,]$g)
      freq[iid] <- freq[iid]+1
      if(iCard>1) {                                  # in R for-loops can run from 1 to 0, so need this check
        for(jCard in 1:(iCard-1)){                   # For every other card (for every pair)
          jid <- s[jCard,]$id                        # Other card's id
          if(iid<=jid)
            pairs[[iid,jid]]=pairs[[iid,jid]]+1      # Only fill upper triangle for now
          else
            pairs[[jid,iid]]=pairs[[jid,iid]]+1
        }
      }
    }
    color1 <- which.max(colorVec)   # First color
    colorVec[color1] <- 0
    color2 <- which.max(colorVec)   # Second color
    guild[color1,color2] <- guild[color1,color2]+1
    colorHist[iSession] <- color1   # Track history
    
    #iBooster = 1                                 # I used to have a for loop here, and I don't want to edit the formulas
    #for(iCard in 1:13) {                         # The first 13 cards are always from one booster; after that all bets are off
    #  iid <- s[(iBooster-1)*14+iCard,]$id        # This card's id
    #  rank[iid] <- rank[iid] + iCard             # Running sum of ranks
    #  if(iCard < 13){
    #    for(jCard in (iCard+1):13){              # All cards that were picked after i
    #      jid <- s[(iBooster-1)*14+jCard,]$id
    #      prefs[[iid,jid]] = prefs[[iid,jid]]+1  # i was taken over j. This time i won
    #    }
    #  }
    #}
  }
  as.numeric(difftime(Sys.time(), tic, units = "secs"))
}

for(id in 1:nCards){
  rank[id] <- rank[id]/freq[id]                # From sum-ranks to average pick orders
}

guilds = guild/nrow(d)

### -----------------------------------------
### Here's a good point to save the environment, as it takes about a minute for every 1000 drafts
save(pairs,freq,rank,db,guilds,prefs,colorHist,nDrafts,file=paste(myFolder,"/","pairs.RData",sep=""))
### -----------------------------------------

image(pairs,axes=F,col = grey(seq(0, 1, length = 256)))
#image(prefs,axes=F,col = grey(seq(0, 1, length = 256)))



nCards <- nrow(db)                 # Repeat, in case the data was reloaded
p <- pairs                         # Make a copy
for(jCard in 1:nCards) {
    for(iCard in 1:jCard) {
      p[iCard,jCard] <- p[iCard,jCard]/(freq[iCard]*freq[jCard])*nDrafts
      p[jCard,iCard] <- p[iCard,jCard]
    }
}
#temp <- p
#temp[temp==0] <- 1                       # Replace 0s with 1s
#dist <- 1/temp                        # From associations to distances
#dist <- sqrt(1-0.99*p/max(p))
dist <- (1-0.99*p/max(p))
#dist <- max(p)/(p+1)
#dist <- max(p)^2/(p+1)^2
image(dist,axes=F,col = grey(seq(0, 1, length = 256)))

ndim <- 2  # Number of dimensions ot use

#require(MASS)
#fit <- isoMDS(dist,k=ndim) # Isomapping. k is the number of dim
fit <- cmdscale(dist,eig=TRUE, k=ndim) # Classical scaling

# install.packages("lle")
# One could conceivablhy try lle here, but I'm not sure it's worth investing time

# install.packages("rgl")
# install.packages("car")

if(ndim<3) {
  scale <- data.frame(x=fit$points[,1],y=fit$points[,2])
} else {
  scale <- data.frame(x=fit$points[,1],y=fit$points[,2],z=fit$points[,3])
}
scale <- mutate(scale,id=1:nrow(scale))
scale <- inner_join(scale,db,by="id")
# scale <- mutate(scale,w = grepl("W",cost)*1,u = grepl("U",cost)*1,
#                b = grepl("B",cost)*1,r = grepl("R",cost)*1,g = grepl("G",cost)*1)
# wubrg now come from db itself
scale <- mutate(scale,color_n=0)
scale <- mutate(scale,color_n=w*1+u*2+b*3+r*4+g*5)
scale <- mutate(scale,color_n=color_n*((w+u+b+r+g)==1)+6*((w+u+b+r+g)>1))
colorList <- data.frame(color_n=c(0,1,2,3,4,5,6),
                        color=c("0","W","U","B","R","G","M"))
colorList$color = factor(colorList$color,levels=c("0","W","U","B","R","G","M"),ordered=T)
scale <- inner_join(scale,colorList,by="color_n")
scale <- mutate(scale,rank=rank)
myColors <- c("gray","tan2","blue","black","red","green","purple")

# Clustering, only points
ggplot(scale) + theme_bw() + geom_point(aes(x,y,color=color)) +
  scale_color_manual(values=myColors) + xlab('') + ylab('')

# Points and labels
#install.packages("ggrepel")
require(ggrepel)
ggplot(scale) + theme_bw() + geom_point(aes(x,y,color=color)) +
  scale_color_manual(values=c("gray","tan2","blue","black","red","green","purple")) +
  geom_text_repel(aes(x,y,label=name),size=2,box.padding = 0.01, point.padding = 0.01) +
  xlab('') + ylab('') 

# Zoom in on the core
ggplot(scale) + theme_bw() + geom_point(aes(x,y,color=color)) +
  scale_color_manual(values=c("gray","tan2","blue","black","red","green","purple")) +
  geom_text_repel(aes(x,y,label=name),size=2,box.padding = 0.01, point.padding = 0.01) +
  xlim(-0.15,0.15) + ylim(-0.15,0.15)

# Rank
ggplot(scale) + theme_bw() + geom_point(aes(rank,Rating,color=color)) +
  scale_color_manual(values=myColors) +
  xlab("Draft point within a pack, 1 to 14") + ylab("Dan's rating")

temp <- scale
temp$r <- rank(temp$rank)
ggplot(temp,aes(Rating,r)) + theme_bw() + geom_point(aes(color=color)) +
  scale_color_manual(values=myColors) + ylab("Draft Rank") + xlab("Dan's rating") +
  geom_text(aes(label=name),size=2,hjust=-0.05) + xlim(0,6)

### ----------------------- 3d plot ---------
# (For it to work, scaling above shoudl be performed to 3D instead of 2D)
require(rgl)
require(car)
require(magick)

plot3d(scale$x,scale$y,scale$z,surface=F,col=myColors[scale$color],
       xlab="", ylab="", zlab="", size=4, alpha=0.8)
movie3d(spin3d(axis = c(0,0,1), rpm = 2), duration=10, type="gif", dir=myFolder)


# ----------- Guilds
gdf <- data.frame(guilds)
colorVector <- c("W","U","B","R","G")
gdf$c1 <- 1:5
gdf2 <- gather(gdf,c2,val,-c1) 
gdf2 <- gdf2 %>% mutate(c2 = factor(c2,labels=colorVector), c1 = factor(c1,labels=colorVector))
guilds

ggplot(data=gdf2,aes(c1,c2,fill=val)) + theme_bw() + geom_tile() +
  scale_fill_gradient2(low="navy", mid="white", high="red") +
  geom_text(aes(c1,c2,label=sprintf("%2d%%",round(100*val))),color="brown") +
  xlab('Color 1') + ylab('Color 2') + guides(fill=F)


# ----------- Color history
histData <- NULL
histData <- data.frame()
binLength <- 1000
for(i in 1:floor(length(colorHist)/binLength)){
  h <- hist(colorHist[(1+(i-1)*binLength):(i*binLength)],c(1:6)-0.5)
  histData <- rbind(histData,data.frame(t=i,
      w=h$density[1],u=h$density[2],b=h$density[3],r=h$density[4],g=h$density[5]))
}
histData2 <- gather(histData,Color,Value,-t)
histData2$Color <- factor(histData2$Color,levels=c('w','u','b','r','g'))
myColors2 <- c("tan2","blue","black","red",muted("green"),"purple")
ggplot(data=histData2,aes(t,Value,fill=Color)) + theme_bw() +
  scale_fill_manual(values=myColors2) +
  geom_area(alpha=0.8) + 
  xlab('Thousands of drafts into the guild') + ylab('Share as a 1st color')
require(scales)
ggplot(data=histData2,aes(t,Value,color=Color)) + theme_bw() +
  geom_point(alpha=0.3) + geom_smooth(method=lm,se=F) +
  scale_color_manual(values=myColors2) +
  facet_grid(.~Color) + 
  xlab('Thousands of drafts into the guild') + ylab('Share as a 1st color')

# ------------- Save results
write.table(scale, file = "C:/Users/Sysadmin/Documents/draftsim/out.csv", sep = ",",col.names = NA, qmethod = "double")
write.table(dist, file = "C:/Users/Sysadmin/Documents/draftsim/dist.csv", sep = ",",
            col.names = F, row.names=F, qmethod = "double")
write.table(prefs, file = "C:/Users/Sysadmin/Documents/draftsim/prefs.csv", sep = ",",
            col.names = F, row.names=F, qmethod = "double")


# ----------------------------------------------------------------------
# ------------- Comparisons of earlier and later drafts (relies on pre-saved files)
# To run it, either recalculate the scales, or save some somewhere once and for all

load("C:/Users/Sysadmin/Documents/draftsim/pairs variable M19 part 1 v3.RData")
# Now run everything above
scale1 <- scale # First analyze one set, do this
guilds1 <- guilds

load("C:/Users/Sysadmin/Documents/draftsim/pairs variable M19 part 2 v3.RData")
# Run stuff above
scale2 <- scale # Then repeat with another set, and do this
guilds2 <- guilds

# General prepping
scale1 <- rename(scale1,x1=x,y1=y,z1=z,rank1=rank)
scale2 <- rename(scale2,x2=x,y2=y,z2=z,rank2=rank)
names(scale1)
names(scale2)
full <- inner_join(scale1,dplyr::select(scale2,id,x2,y2,z2,rank2),by="id") #
names(full)
modelx <- lm(data=full,x2~x1+y1+z1) # Best way to transform xy into x2y2
modely <- lm(data=full,y2~x1+y1+z1)
modelz <- lm(data=full,z2~x1+y1+z1)
full$x1 <- fitted(modelx) # So now try to transform xy towards x2y2.  
full$y1 <- fitted(modely) # You'll get x1y1 that are comparable with x2y2 (rotated similarly)
full$z1 <- fitted(modelz)
full <- select(full,id,name,color,Rating,rank1,rank2,x1,y1,x2,y2)
names(full)

# Sense-check: do we reproduce old scatters? (yes)
ggplot(full) + theme_bw() + geom_point(aes(x1,y1,color=color)) + scale_color_manual(values=myColors)
ggplot(full) + theme_bw() + geom_point(aes(x2,y2,color=color)) + scale_color_manual(values=myColors)
head(full)

# Combine both
full2 <- gather(full, key = stage, value=x, -id, -name, -color, -Rating, -rank1,-rank2, -y1, -y2) # Combine old and new
full2$y <- ifelse(full2$stage=="x1",full2$y1,full2$y2) # Take appropriate y
full2$rank <- ifelse(full2$stage=="x1",full2$rank1,full2$rank2)
full2 <- full2 %>% mutate(stage=factor(stage,labels=c("Jul","Aug")))
names(full2)
head(full2)

freq2 <- data.frame(freq=freq)
freq2$id <- 1:nrow(freq2)
full2 <- inner_join(full2,freq2,by="id")
names(full2)

# Flocks
ggplot(full2,aes(x,y,color=color,shape=stage,group=id)) + theme_bw() + geom_point() + 
  geom_line() + scale_color_manual(values=myColors) + scale_shape_manual(values=c(20,15)) +
  xlab('') + ylab('')

# Flocks with labels
ggplot(full2,aes(x,y,color=color,shape=stage,group=id)) + theme_bw() + geom_point() + 
  geom_line() + scale_color_manual(values=myColors) + scale_shape_manual(values=c(20,15)) +
  xlab('') + ylab('') +
  geom_text_repel(data=subset(full2,stage=="Aug"),aes(x,y,label=name),
                  size=2,box.padding = 0.01, point.padding = 0.01,color="black")

# Guilds
guildChange <- guilds2-guilds1
gdf <- data.frame(guildChange)
colorVector <- c("W","U","B","R","G")
gdf$c1 <- 1:5
gdf2 <- gather(gdf,c2,val,-c1) 
gdf2 <- gdf2 %>% mutate(c2 = factor(c2,labels=colorVector), c1 = factor(c1,labels=colorVector))
guildChange

ggplot(data=gdf2,aes(c1,c2,fill=val)) + theme_bw() + geom_tile() +
  scale_fill_gradient2(low="navy", mid="white", high="red") +
  scale_color_gradient2(low="black", mid="gray", high="brown") +
  geom_text(aes(c1,c2,label=sprintf("%2d%%",round(100*val)),color=val)) +
  xlab('Color 1') + ylab('Color 2') + guides(fill=F,color=F)


# Ranks. First - via correlation
ggplot(full,aes(rank1,rank2,color=color)) + theme_bw() + geom_point() + 
  scale_color_manual(values=myColors) + xlab("Pick # within a booster, July") + ylab("Pick within a booster, August")

#ggplot(full,aes(rank1,rank2,color=color)) + theme_bw() + geom_point() + 
#  scale_color_manual(values=myColors) + xlab("Pick # within booster, July") + ylab("Pick within booster, August") +
#  geom_text_repel(aes(label=name),size=2,box.padding = 0.01, point.padding = 0.01,color="black")

# What color lost in pick order in ranks the most? Black.
ggplot(full,aes(color,rank2-rank1,color=color)) + theme_bw() + geom_point() +
  scale_color_manual(values=myColors) +
  stat_summary(fun.y="mean",color="black",shape=22,size=3,geom="point") +
  ylab("Pick order, Aug - July") + guides(color=F)

ggplot(full2,aes(stage,rank,color=color)) + theme_bw() + geom_point() +
  scale_color_manual(values=myColors) + guides(color=F) +
  facet_grid(.~color) + geom_line(aes(group=id),alpha=0.5)

# Canceling color effect
m <- lm(data=full2,rank2~rank1+color) # Estimate shift of rank2 compared to rank1 by color
full2$rank2prime <- full$rank2-(fitted(m)-full$rank1) # Subtract these shifts from rank2
#ggplot(full2,aes(rank2,rank2prime,color=color)) + geom_point() + theme_bw() +
#  scale_color_manual(values=myColors)

if(1){ # Set to 1 to cancel color effect
  full2sub <- subset(full2,abs(rank2prime-rank1)>quantile(abs(rank2prime-rank1),0.75))
  full2sub$rank2 <- full2sub$rank2prime # Give up, just overwrite old rank2 with the new one
}else{
  full2sub <- subset(full2,abs(rank2prime-rank1)>quantile(abs(rank2-rank1),0.75))
}
full2sub$rank1 <- rank(full2sub$rank1)
full2sub$rank2 <- rank(full2sub$rank2)
full2sub$rank <- ifelse(full2sub$stage=="Jul",full2sub$rank1,full2sub$rank2) # Take appropriate rank

# Optimal combo
ggplot(full2sub,aes(stage,125-rank,group=id)) + theme_bw()  + 
  geom_line(aes(color=(rank2<rank1),alpha=abs(rank2-rank))) + 
  geom_point() +
  scale_color_manual(values=c("0"="gray60","W"="gold4","U"=myColors[3],"B"=myColors[4],
                              "R"="red3","G"=myColors[6],"M"=myColors[7],
                              "FALSE"="deepskyblue","TRUE"="red3")) +
  geom_text(aes("Aug",125-rank2,label=name,color=color),size=2,hjust="left",position = position_nudge(x = 0.05)) +
  guides(color=F,alpha=F) + ylab("Ranked card score (higher is better)")
    