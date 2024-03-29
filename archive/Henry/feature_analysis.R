#!/usr/bin/env Rscript

source("/project/csbio/henry/Documents/libraries/lib_util.R")
.libPaths("/project/csbio/henry/Documents/libraries/R")
packages <- c("jsonlite", "ggplot2", "ggthemes", "caret", "cluster", "fpc", "stringr")
for (p in packages) {
  library(p, character.only = TRUE)
}

#####
# DATA PREPARATION
#####

# Begin script
setwd("/project/csbio/henry/Documents/projects/draftsim")

# Loads in helper functions
source(file.path("MTG", "Henry", "card_utilities.R"))

# Sets important parameters
set <- "GRN"
n_drafts <- 5000
remove_last_picks <- TRUE
latest_drafts <- TRUE

# Loads in card database 
all_cards <- load_card_db(file.path("data", "all_sets.json"))

# Loads in standard decks
angels <- load_deck_txt(file.path("decks", "standard_wmc", "Boros_Angels_Kon_Fai_Wu.txt"), all_cards)
drakes <- load_deck_txt(file.path("decks", "standard_wmc", "Izzet_Drakes_by_Shahar_Shenhar.txt"), all_cards)
tokens <- load_deck_txt(file.path("decks", "standard_wmc", "Selesnya_Tokens_by_Timothee_Jammot.txt"), all_cards)
jeskai <- load_deck_txt(file.path("decks", "standard_wmc", "Jeskai_Control_by_Arnaud_Hocquemiller.txt"), all_cards)
wr_aggro <- load_deck_txt(file.path("decks", "standard_wmc", "Boros_Aggro_by_Yuval_Zuckerman.txt"), all_cards)
gb_aggro <- load_deck_txt(file.path("decks", "standard_wmc", "Golgari_Aggro_by_Jean-Emmanuel_Depraz.txt"), all_cards)

# Gets feature vectors of standard decks
angels_sum <- summarize_deck(angels)[1,]
drakes_sum <- summarize_deck(drakes)[1,]
tokens_sum <- summarize_deck(tokens)[1,]
jeskai_sum <- summarize_deck(jeskai)[1,]
wr_aggro_sum <- summarize_deck(wr_aggro)[1,]
gb_aggro_sum <- summarize_deck(gb_aggro)[1,]

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
                             "num_enchantments" = rep(NA, n_drafts), "num_planeswalkers" = rep(NA, n_drafts),
                             "num_W" = rep(NA, n_drafts), "num_U" = rep(NA, n_drafts), 
                             "num_B" = rep(NA, n_drafts), "num_R" = rep(NA, n_drafts),
                             "num_G" = rep(NA, n_drafts))
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

# Gets dominant colors for each deck
human_features$dominant_color <- "none"
for (i in 1:nrow(human_features)) {
  deck <- human_features[i,(colnames(human_features) %in% c("num_W", "num_U", "num_B", "num_R", "num_G"))]
  colnames(deck) <- c("W", "U", "B", "R", "G")
  if (sum(deck > 0.3) >= 2) {
    human_features$dominant_color[i] <- paste(colnames(deck)[deck > 0.3], collapse = "/")
  } else if (sum(deck > 0.4) >= 1 & sum(deck > 0.2) >= 1) {
    human_features$dominant_color[i] <- paste(colnames(deck)[deck > 0.4 | deck > 0.2], collapse = "/")
  }
}

# Gets closest strategy to each deck
human_features$closest_strategy <- NA
for (i in 1:nrow(human_features)) {
  draft_deck <- human_features[i, 1:(ncol(human_features) - 7)]
  angels_cor <- deck_cor(draft_deck, angels_sum[,1:(ncol(angels_sum) - 5)])
  drakes_cor <- deck_cor(draft_deck, drakes_sum[,1:(ncol(drakes_sum) - 5)])
  tokens_cor <- deck_cor(draft_deck, tokens_sum[,1:(ncol(tokens_sum) - 5)])
  jeskai_cor <- deck_cor(draft_deck, jeskai_sum[,1:(ncol(jeskai_sum) - 5)])
  wr_aggro_cor <- deck_cor(draft_deck, wr_aggro_sum[,1:(ncol(wr_aggro_sum) - 5)])
  gb_aggro_cor <- deck_cor(draft_deck, gb_aggro_sum[,1:(ncol(gb_aggro_sum) - 5)])
  strats <- c("Aggro" = max(wr_aggro_cor, gb_aggro_cor),
              "Midrange" = max(angels_cor, tokens_cor),
              "Control" = jeskai_cor,
              "Tempo" = drakes_cor)
  human_features$closest_strategy[i] = names(which.max(strats))
}

# Writes data to file
write.table(human_features, file.path("data", paste0(set, "_deck_features.tsv")), sep = "\t", 
            row.names = FALSE, col.names = TRUE, quote = FALSE)

#####
# PCA ANALYSIS
#####

# Sets colors
pal <- c("W/G" = "#80c080", "B/G" = "#808000", "U/B" = "000080", "W/R" = "#ff8080", 
         "U/R" = "800080", "none" = "gray", "U" = "blue", "U/B/G" = "#002a45", 
         "R" = "red", "W/B/G" = "#466a46", "G" = "green", "W/R/G" = "#c06040", 
         "U/B/R" = "#400040", "W" = "grey95", "R/G" = "#8c3a00", "W/U/R" = "#b973b9", 
         "W/U" = "#7373ff", "W/B" = "#808080", "B/R" = "#800000", "U/G" = "#004673", 
         "B" = "black", "W/U/B" = "#4040c0", "B/R/G" = "#463a00", "W/U/G" = "#3f798c",
         "W/B/R" = "#804040", "U/R/G" = "#463a46")

# Clusters decks using PCA on scaled data
pca <- prcomp(human_features[1:(ncol(human_features) - 7)], scale = TRUE)
pca_data <- data.frame(scale(as.matrix(human_features[1:(ncol(human_features) - 7)])) %*% pca$rotation[,1:2])
pca_data$dominant_color <- human_features$dominant_color
pca_data$closest_strategy <- human_features$closest_strategy

# Plots PCs
ggplot(pca_data, aes(PC1, PC2)) +
  geom_point(size = 1.5, alpha = 0.6, aes(color = dominant_color, shape = closest_strategy)) +
  xlab("PC1") +
  ylab("PC2") +
  labs(color = "Dominant colors", shape = "Closest strategy") +
  scale_colour_manual(values = pal) +
  theme_tufte(base_size = 14)
ggsave(file.path("MTG", "Henry", "plots", paste0(set, "_no_colors_pca.png")), 
       dpi = 400, width = 8, height = 6)

# Plots PCs with decks that don't map to certain colors removed
pca_data <- pca_data[pca_data$dominant_color != "none",]
ggplot(pca_data, aes(PC1, PC2)) +
  geom_point(size = 1.5, alpha = 0.6, aes(color = dominant_color, shape = closest_strategy)) +
  xlab("PC1") +
  ylab("PC2") +
  labs(color = "Dominant colors", shape = "Closest strategy") +
  scale_colour_manual(values = pal) +
  theme_tufte(base_size = 14)
ggsave(file.path("MTG", "Henry", "plots", paste0(set, "_no_colors_filtered_pca.png")), 
       dpi = 400, width = 8, height = 6)

# Clusters decks using PCA on scaled data with colors added
pca <- prcomp(human_features[1:(ncol(human_features) - 2)], scale = TRUE)
pca_data <- data.frame(scale(as.matrix(human_features[1:(ncol(human_features) - 2)])) %*% pca$rotation[,1:2])
pca_data$dominant_color <- human_features$dominant_color
pca_data$closest_strategy <- human_features$closest_strategy

# Plots PCs
ggplot(pca_data, aes(PC1, PC2)) +
  geom_point(size = 1.5, alpha = 0.6, aes(color = dominant_color, shape = closest_strategy)) +
  xlab("PC1") +
  ylab("PC2") +
  labs(color = "Dominant colors", shape = "Closest strategy") +
  scale_colour_manual(values = pal) +
  theme_tufte(base_size = 14)
ggsave(file.path("MTG", "Henry", "plots", paste0(set, "_with_colors_pca.png")), 
       dpi = 400, width = 8, height = 6)

# Plots PCs with decks that don't map to certain colors removed
pca_data <- pca_data[pca_data$dominant_color != "none",]
ggplot(pca_data, aes(PC1, PC2)) +
  geom_point(size = 1.5, alpha = 0.6, aes(color = dominant_color, shape = closest_strategy)) +
  xlab("PC1") +
  ylab("PC2") +
  labs(color = "Dominant colors", shape = "Closest strategy") +
  scale_colour_manual(values = pal) +
  theme_tufte(base_size = 14)
ggsave(file.path("MTG", "Henry", "plots", paste0(set, "_with_colors_filtered_pca.png")), 
       dpi = 400, width = 8, height = 6)
