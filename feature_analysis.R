#!/usr/bin/env Rscript

source("/project/csbio/henry/Documents/libraries/lib_util.R")
.libPaths("/project/csbio/henry/Documents/libraries/R")
packages <- c("jsonlite", "ggplot2", "ggthemes", "caret", "cluster", "fpc")
for (p in packages) {
  library(p, character.only = TRUE)
}

#####
# DATA PREPARATION
#####

# Begin script
setwd("/project/csbio/henry/Documents/projects/draftsim")

# Loads in helper functions
source(file.path("MTG", "src", "card_utilities.R"))

# Sets important parameters
set <- "GRN"
n_drafts <- 5000
remove_last_picks <- TRUE
latest_drafts <- TRUE

# Loads in card database 
all_cards <- load_card_db(file.path("data", "all_sets.json"))

# Loads in draftsim data, formats it, subsets DB to current set, and gets all human drafts
all_drafts <- data.frame()
subset_db <- NA
draft_cols <- c("draftId", "set", "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8")
if (set == "GRN") {
  all_drafts <- read.csv(file.path("data", "grn_1.csv"), header = FALSE, col.names = draft_cols,
                         stringsAsFactors = FALSE)
  all_drafts <- all_drafts[all_drafts$set == "GRN",]
  subset_db <- get_set_info(c("GRN"), all_cards)
} else if (set == "M19") {
  all_drafts <- read.csv(file.path("data", "m19_2.csv"), header = FALSE, col.names = draft_cols, 
                         stringsAsFactors = FALSE)
  all_drafts <- all_drafts[all_drafts$set == "M19",]
  subset_db <- get_set_info(c("M19"), all_cards)
}
human_drafts <- all_drafts[,1:3]

# If we want the latest drafts as opposed to the earliest drafts, we reverse the dataframe
if (latest_drafts) {
  human_drafts <- human_drafts[nrow(human_drafts):1,]
}

# Loops through all human drafts and gets deck feature vectors
human_features <- data.frame("avg_cmc" = rep(0, n_drafts), "sd_cmc" = rep(0, n_drafts),
                             "avg_power" = rep(0, n_drafts), "avg_tough" = rep(0, n_drafts), 
                             "avg_copies" = rep(NA, n_drafts), "num_lands" = rep(NA, n_drafts), 
                             "num_creatures" = rep(NA, n_drafts), "num_instants" = rep(NA, n_drafts), 
                             "num_sorceries" = rep(NA, n_drafts), "num_artifacts" = rep(NA, n_drafts), 
                             "num_enchantments" = rep(NA, n_drafts), "num_planeswalkers" = rep(NA, n_drafts))
for (i in 1:n_drafts) {
  pool <- human_drafts[i,3]
  pool <- strsplit(pool, ",")[[1]]
  
  # Joins cards with commas in their names
  joined_pool <- pool
  for (j in 1:length(pool)) {
    if (startsWith(pool[j], "_")) {
      joined_pool[j-1] <- paste0(pool[j-1], ",", pool[j])
      joined_pool[j] <- NA
    }
  }
  pool <- joined_pool[complete.cases(joined_pool)]
  
  # Removes last picks in each pack
  if (remove_last_picks) {
    pack_1 <- pool[1:14]
    pack_2 <- c(pool, pool[16:29])
    pool <- c(pool, pool[31:44]) 
  }
  
  # Formats vectors for look-up into MTGJSON database, and gets dataframe of card info
  pool <- gsub("_", " ", pool)
  pool <- gsub('[[:digit:]]+', '', pool)
  pool <- trimws(pool)
  pool_df <- load_deck_string(pool, subset_db)
  
  # Gets feature vector for the current deck
  human_features[i,] <- summarize_deck(pool_df)
}

# Removes number of planeswalkers feature
df <- human_features[,!(colnames(human_features) %in% c("num_planeswalkers"))]

# Writes data to file
write.table(df, file.path("data", paste0(set, "_deck_features.tsv")), sep = "\t", 
            row.names = FALSE, col.names = TRUE, quote = FALSE)

#####
# PCA ANALYSIS
#####

# Clusters decks using PCA on scaled data
pca <- prcomp(df, scale = TRUE)
pca_data <- data.frame(scale(as.matrix(df)) %*% pca$rotation[,1:2])

# Plots PCs
ggplot(pca_data, aes(PC1, PC2)) +
  geom_point(size = 1.5, alpha = 0.8) +
  xlab("PC1") +
  ylab("PC2") +
  theme_tufte(base_size = 14)
ggsave(file.path("MTG", "plots", paste0(set, "_pca.png")), dpi = 400, width = 8, height = 6)



