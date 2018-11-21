#!/usr/bin/env Rscript

source("/project/csbio/henry/Documents/libraries/lib_util.R")
.libPaths("/project/csbio/henry/Documents/libraries/R")
packages <- c("jsonlite", "ggplot2", "ggthemes", "caret")
for (p in packages) {
  library(p, character.only = TRUE)
}

#####
# MAIN SCRIPT
######

# Begin script
setwd("/project/csbio/henry/Documents/projects/card_analysis")

# Loads in helper functions
source(file.path("src", "card_utilities.R"))
source(file.path("src", "data_utilities.R"))
source(file.path("src", "deck_generator.R"))
source(file.path("src", "testing_utilities.R"))
source(file.path("src", "playtest.R"))

# Loads in card database
all_cards <- load_card_db(file.path("input", "all_sets.json"))

# Loads in decks
info <- load_all_decks(all_cards)
all_main <- info[[1]]
all_side <- info[[2]]

# Loads in basic lands as object "basics"
load(file.path("input", "basics.rda"))

# Sets forge directories
forge_exe_dir <- 
  "C://Users//Henry Ward//Documents//My Games//forge-gui-desktop-1.6.10//"
forge_user_dir <- "C://Users//Henry Ward//AppData//Roaming//Forge"





### ARCHETYPE ANALYSIS

# Sets important parameters
playtest_runs <- 10
playtest_games <- 5
num_tests <- 10
runs <- 1
set_name <- "ZEN"
subset_db <- get_set_info(c(set_name), all_cards)

# Loads target decks
aggro <- load_deck_txt(file.path("input", "standard", "gatecrash_pt",
                                 "eric_froehlich_aggro.txt"), all_cards)
midrange <- load_deck_txt(file.path("input", "standard", "gatecrash_pt",
                                    "stephen_mann_midrange.txt"), all_cards)
control <- load_deck_txt(file.path("input", "standard", "gatecrash_pt",
                                   "ben_stark_control.txt"), all_cards)
aggro_target <- summarize_deck(aggro)[1,]
midrange_target <- summarize_deck(midrange)[1,]
control_target <- summarize_deck(control)[1,]

# Replicates the experiment a given number of times
init_results <- NA
training_results <- NA
testing_results <- NA
for (i in 1:runs) {
  
  # Makes output folder for the current run if it doesn't exist
  output_folder <- file.path("output", set_name, paste("run", i, sep = "_"))
  if (!dir.exists(file.path("output", set_name))) { 
    dir.create(file.path("output", set_name)) 
  }
  if (!dir.exists(output_folder)) { dir.create(output_folder) }
  
  # Sinks results to output file
  sink(file.path(output_folder, "results.txt"))
  
  # Creates a greedy control deck
  results <- create_deck(subset_db, c('U', 'W'), control_target, midrange,
                         "Control", basics, forge_exe_dir, forge_user_dir,
                         playtest_games, playtest_runs)
  init_greedy_control <- results[[1]]
  greedy_control <- results[[2]]
  control_wins <- results[[3]]
  
  # Creates a greedy aggro deck
  results <- create_deck(subset_db, c('R', 'B'), aggro_target, control,
                         "Aggro", basics, forge_exe_dir, forge_user_dir,
                         playtest_games, playtest_runs)
  init_greedy_aggro <- results[[1]]
  greedy_aggro <- results[[2]]
  aggro_wins <- results[[3]]
  
  # Creates a greedy midrange deck
  results <- create_deck(subset_db, c('B', 'G'), midrange_target, aggro,
                         "Midrange", basics, forge_exe_dir, forge_user_dir,
                         playtest_games, playtest_runs)
  init_greedy_midrange <- results[[1]]
  greedy_midrange <- results[[2]]
  midrange_wins <- results[[3]]
  
  # Pits initial greedy aggro-control-midrange against each other
  init_log_1 <- test_decks_forge(init_greedy_aggro, init_greedy_control,
                                 forge_exe_dir, forge_user_dir, num_tests)
  init_results_1 <- parse_forge_log(init_greedy_aggro, init_log_1, 1)
  init_log_2 <- test_decks_forge(init_greedy_aggro, init_greedy_midrange,
                                   forge_exe_dir, forge_user_dir, num_tests)
  init_results_2 <- parse_forge_log(init_greedy_aggro, init_log_2, 1)
  init_log_3 <- test_decks_forge(init_greedy_control, init_greedy_midrange,
                                   forge_exe_dir, forge_user_dir, num_tests)
  init_results_3 <- parse_forge_log(init_greedy_control, init_log_3, 1)

  # Pits greedy aggro-control-midrange against each other
  greedy_log_1 <- test_decks_forge(greedy_aggro, greedy_control,
                                   forge_exe_dir, forge_user_dir, num_tests)
  greedy_results_1 <- parse_forge_log(greedy_aggro, greedy_log_1, 1)
  greedy_log_2 <- test_decks_forge(greedy_aggro, greedy_midrange,
                                   forge_exe_dir, forge_user_dir, num_tests)
  greedy_results_2 <- parse_forge_log(greedy_aggro, greedy_log_2, 1)
  greedy_log_3 <- test_decks_forge(greedy_control, greedy_midrange,
                                   forge_exe_dir, forge_user_dir, num_tests)
  greedy_results_3 <- parse_forge_log(greedy_control, greedy_log_3, 1)

  # Prints all testing results
  end_str <- paste("win ratio out of", num_tests, "games\n")
  cat(paste("\nInitial aggro vs. initial control", end_str))
  cat(paste(init_results_1$ai_1_win, "aggro,", init_results_1$ai_2_win, "control\n"))
  cat(paste("\nInitial aggro vs. initial midrange", end_str))
  cat(paste(init_results_2$ai_1_win, "aggro,", init_results_2$ai_2_win, "midrange\n"))
  cat(paste("\nInitial control vs. initial midrange", end_str))
  cat(paste(init_results_3$ai_1_win, "control,", init_results_3$ai_2_win, "midrange\n"))
  
  cat(paste("\nGreedy aggro vs. greedy control", end_str))
  cat(paste(greedy_results_1$ai_1_win, "aggro,", greedy_results_1$ai_2_win, "control\n"))
  cat(paste("\nGreedy aggro vs. greedy midrange", end_str))
  cat(paste(greedy_results_2$ai_1_win, "aggro,", greedy_results_2$ai_2_win, "midrange\n"))
  cat(paste("\nGreedy control vs. greedy midrange", end_str))
  cat(paste(greedy_results_3$ai_1_win, "control,", greedy_results_3$ai_2_win, "midrange\n"))

  # Builds up training results dataframe
  if (is.na(training_results)) {
    training_results <- data.frame(rbind(control_wins, aggro_wins, midrange_wins))
    colnames(training_results) <- paste("game", 1:playtest_runs, sep="")
  } else {
    training_results <- rbind(training_results, control_wins, 
                              aggro_wins, midrange_wins)
  } 
  
  # Builds up initial and testing results dataframes
  matchup_col <- c("control_vs_aggro", "aggro_vs_midrange", "midrange_vs_control")
  set_col <- c(set_name, set_name, set_name)
  if (is.na(testing_results)) {
    testing_results <- data.frame(cbind(matchup_col, set_col))
    colnames(testing_results) <- c("matchup", "set")
  }
  if (is.na(init_results)) {
    init_results <- data.frame(cbind(matchup_col, set_col))
    colnames(init_results) <- c("matchup", "set")
  }
  testing_results <- cbind(testing_results, c(greedy_results_1$ai_2_win,
                                              greedy_results_2$ai_1_win,
                                              greedy_results_3$ai_2_win))
  init_results <- cbind(init_results, c(init_results_1$ai_2_win,
                                        init_results_2$ai_1_win,
                                        init_results_3$ai_2_win))
  
  # Ends sinking
  sink()
}

# Writes dataframes out to files
training_results$set <- set_name
training_results$archetype <- "Control"
training_results$archetype[seq(2, runs*3 - 1, 3)] <- "Aggro"
training_results$archetype[seq(3, runs*3, 3)] <- "Midrange"
colnames(testing_results)[3:ncol(testing_results)] <- 
  paste("run", 1:(ncol(testing_results)-2), sep = "")
colnames(init_results)[3:ncol(init_results)] <- 
  paste("run", 1:(ncol(init_results)-2), sep = "")
write.csv(training_results, file = file.path("output", set_name, "training_wins.csv"), 
          quote = FALSE, row.names = FALSE)
write.csv(testing_results, file = file.path("output", set_name, "testing_wins.csv"), 
          quote = FALSE, row.names = FALSE)
write.csv(init_results, file = file.path("output", set_name, "init_wins.csv"), 
          quote = FALSE, row.names = FALSE)






# # Pits aggro-control-midrange against each other
# log_1 <- test_decks_forge(aggro, control, forge_exe_dir, forge_user_dir, 100)
# results_1 <- parse_forge_log(aggro, log_1, 1)
# log_2 <- test_decks_forge(aggro, midrange, forge_exe_dir, forge_user_dir, 100)
# results_2 <- parse_forge_log(aggro, log_2, 1)
# log_3 <- test_decks_forge(control, midrange, forge_exe_dir, forge_user_dir, 100)
# results_3 <- parse_forge_log(control, log_3, 1)
# 
# cat("\nAggro vs. control win ratio out of 100 games:\n")
# cat(paste(results_1$ai_1_win, "aggro,", results_1$ai_2_win, "control\n"))
# cat("\nAggro vs. midrange win ratio out of 100 games:\n")
# cat(paste(results_2$ai_1_win, "aggro,", results_2$ai_2_win, "midrange\n"))
# cat("\nControl vs. midrange win ratio out of 100 games:\n")
# cat(paste(results_3$ai_1_win, "control,", results_3$ai_2_win, "midrange\n"))









### SEALED ANALYSIS

# # Subsets the database to Dominaria
# subset_db <- get_set_info(c("XLN", "RIX", "DOM"), all_cards)
# 
# # Loads in target deck
# target_deck <- file.path("input", "sealed_targets", "vamps.txt")
# target_deck <- summarize_deck(load_deck_txt(target_deck, subset_db))[1,]
# target_deck$num_planeswalkers <- target_deck$num_planeswalkers + 2
# 
# # Loads in sealed pool and appends basics
# pool <- file.path("input", "sealed_pools", "dom_sealed_1.dec")
# pool <- load_deck_txt(pool, subset_db)
# basics_info <- load_deck_txt(file.path("input", "basics.txt"), subset_db)
# pool <- rbind(pool, basics_info)
# pool <- pool[!is.na(pool$name),]
# 
# # Gets decks for all two-color combinations
# sealed_decks <- list()
# color_combos <- list(c('W', 'U'), c('W', 'B'), c('W', 'R'), c('W', 'G'), c('U', 'B'),
#                      c('U', 'R'), c('U', 'G'), c('B', 'R'), c('B', 'G'), c('R', 'G'))
# for (i in 1:length(color_combos)) {
#   
#   # Gets a seed set for the target deck and removes cards from pool
#   colors <- color_combos[[i]]
#   pool_temp <- subset_to_colors_pool(pool, colors, include_colorless = TRUE)
#   seed_set <- get_seed_set_pool(pool_temp, target_deck, 2)
#   pool_temp$copies[pool_temp$name %in% seed_set$name] <- 
#     pool_temp$copies[pool_temp$name %in% seed_set$name] - 1
#   pool_temp <- pool_temp[pool_temp$copies > 0,]
#   
#   # Generates a deck from the pool in the current colors
#   greedy_sealed <- generate_greedy_sealed_deck(seed_set, target_deck, pool_temp)
#   sealed_decks[[i]] <- greedy_sealed
# }









# ### EXPLORATORY ANALYSIS

# # Clusters decks using PCA on scaled data
# pca <- prcomp(all_main[,1:6], scale = TRUE)
# print(summary(pca))
# pca_data <- data.frame(scale(as.matrix(all_main[,1:10])) %*% pca$rotation[,1:6])
# pca_data$archetype <- all_main$archetype

# ggplot(all_main, aes(avg_cmc, avg_power, shape = archetype)) +
#   geom_point(aes(color = archetype), size = 3.5) + 
#   scale_shape_manual(values=1:length(unique(all_main$archetype))) +
#   theme_tufte(base_size = 14) +
#   xlab("Average CMC") +
#   ylab("Average power")
# ggsave(file.path("output", "cmc_plot.png"), dpi = 400, width = 8, height = 6)
# 
# # Makes plots of PCA data
# ggplot(pca_data, aes(PC1, PC2, shape = archetype)) +
#   geom_point(aes(color = archetype), size = 3.5) + 
#   scale_shape_manual(values=1:length(unique(pca_data$archetype))) +
#   theme_tufte(base_size = 14) +
#   xlab("PC1") +
#   ylab("PC2")
# ggsave(file.path("output", "pca_plot.png"), dpi = 400, width = 8, height = 6)
# 



# # Trains KNN models on the PCA data, the full data, and the subset data
# pca_results <- c()
# full_results <- c()
# subset_results <- c()
# for (i in 1:100) {
#   training_ind <- createDataPartition(pca_data$archetype, p = 0.6, list = FALSE)
#   train <- pca_data[training_ind,]
#   test <- pca_data[-training_ind,]
#   model <- train_deck_model(train, "knn")
#   pred <- predict(model, newdata = test)
#   pca_results <- c(pca_results, sum(pred == test$archetype)/nrow(test))
#   
#   train <- all_main[training_ind,]
#   test <- all_main[-training_ind,]
#   model <- train_deck_model(train, "knn")
#   pred <- predict(model, newdata = test)
#   full_results <- c(full_results, sum(pred == test$archetype)/nrow(test))
#   
#   temp <- all_main[,(colnames(all_main) %in% c("avg_cmc", "avg_power", "archetype"))]
#   train <- temp[training_ind,]
#   test <- temp[-training_ind,]
#   model <- train_deck_model(train, "knn")
#   pred <- predict(model, newdata = test)
#   subset_results <- c(subset_results, sum(pred == test$archetype)/nrow(test))
# }
# cat(paste("PCA testing accuracy:", mean(pca_results), "\n"))
# cat(paste("Full data testing accuracy:", mean(full_results), "\n"))
# cat(paste("Subset data testing accuracy:", mean(subset_results), "\n"))
# print(p.adjust(t.test(pca_results, full_results)$p.value, "BH", 3))
# print(p.adjust(t.test(pca_results, subset_results)$p.value, "BH", 3))
# print(p.adjust(t.test(subset_results, full_results)$p.value, "BH", 3))