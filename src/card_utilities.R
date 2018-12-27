###### 
# UTILITY FUNCTIONS
######

# Gets a given number of random cards from a pool of cards
get_random_cards_pool <- function(pool, num_cards = 1, replace = FALSE, 
                                  remove_basics = TRUE) {
  
  # Removes basic lands if specified
  card_names <- pool$name
  if (remove_basics) {
    basics <- c("Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes")
    card_names <- card_names[!(card_names %in% basics)]
  }
  
  # Resets seed to a random one. See the following for more info:
  # https://stackoverflow.com/questions/8810338/same-random-numbers-every-time
  rm(.Random.seed, envir = globalenv())
  card_names <- sample(card_names, num_cards, replace = replace)
  
  # Returns the card info by subsetting the pool
  return(pool[pool$name %in% card_names,])
}

# Gets a given number of random cards from a card database
get_random_cards <- function(card_db, num_cards = 1, replace = FALSE, 
                             remove_basics = TRUE, no_lands = FALSE) {
  card_names <- c()
  for (set in names(card_db)) { 
    cards <- card_db[[set]][["cards"]]
    
    # Removes lands if specified
    if (no_lands) {
      cards <- cards[!grepl("Land", cards$type),]
    }
    
    # Gets all card names
    card_names <- c(card_names, cards$name)
  }
  
  # Removes basic lands if specified
  if (remove_basics & !no_lands) {
    basics <- c("Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes")
    card_names <- card_names[!(card_names %in% basics)]
  }
  
  # Resets seed to a random one. See the following for more info:
  # https://stackoverflow.com/questions/8810338/same-random-numbers-every-time
  rm(.Random.seed, envir = globalenv())
  card_names <- sample(card_names, num_cards, replace = replace)
  
  # Gets the card info for all sampled cards by treating it as a deck
  card_names <- paste("1", card_names)
  temp_file <- "temp.txt"
  write(card_names, file = temp_file)
  card_info <- load_deck_txt(temp_file, card_db)
  file.remove(temp_file)
  return(card_info)
}

# Subsets a card database to the given colors
subset_to_colors <- function(card_db, colors, include_colorless = TRUE,
                             include_nonbasics = TRUE, clean = TRUE) {
  for (set in names(card_db)) {
    cards <- card_db[[set]][["cards"]]
    ind <- NA
    if (include_colorless) {
      ind <- unlist(lapply(cards$colorIdentity, function (x) all(x %in% colors)))
      ind_2 <- unlist(lapply(cards$colorIdentity, function (x) length(x) == 0))
      ind <- ind | ind_2
    } else {
      ind <- unlist(lapply(cards$colorIdentity, function (x) all(x %in% colors)))
      ind_2 <- unlist(lapply(cards$colorIdentity, function (x) length(x) != 0))
      ind <- ind & ind_2
    }
    cards <- cards[ind,]
    if (!include_nonbasics) {
      ind <- !((cards$type %in% "Land") | (cards$type %in% "Basic"))
      cards <- cards[ind,]
    }
    
    # Optionally cleans special features of the cards
    if (clean) {
      special_power_ind <- which(cards$power == "*")
      cards$power[special_power_ind] <- 0
      special_tough_ind <- which(cards$toughness == "*")
      cards$toughness[special_tough_ind] <- 0
    }
    
    card_db[[set]][["cards"]] <- cards
  }
  return(card_db)
}

# Subsets a pool to the given colors
subset_to_colors_pool <- function(pool, colors, include_colorless = TRUE,
                             clean = TRUE) {
  ind <- NA
  if (include_colorless) {
    ind <- unlist(lapply(pool$colorIdentity, function (x) all(x %in% colors)))
    ind_2 <- unlist(lapply(pool$colorIdentity, function (x) length(x) == 0))
    ind <- ind | ind_2
  } else {
    ind <- unlist(lapply(pool$colorIdentity, function (x) all(x %in% colors)))
    ind_2 <- unlist(lapply(pool$colorIdentity, function (x) length(x) != 0))
    ind <- ind & ind_2
  }
  pool <- pool[ind,]
  
  # Optionally cleans special features of the cards
  if (clean) {
    special_power_ind <- which(pool$power == "*")
    pool$power[special_power_ind] <- 0
    if ("toughness" %in% colnames(pool)) {
      special_tough_ind <- which(pool$toughness == "*")
      pool$toughness[special_tough_ind] <- 0
    } else if ("tough" %in% colnames(pool)) {
      special_tough_ind <- which(pool$tough == "*")
      pool$tough[special_tough_ind] <- 0
    }
  }
  return(pool)
}

# Gets the info of each card in the given sets
get_set_info <- function(sets, card_db) {
  subset_db <- card_db[names(card_db) %in% sets]
  return(subset_db)
}

# Trains a model on a given df of deck stats to predict their archetype
train_deck_model <- function(training_decks, method) {
  tr_control <- trainControl(method = "cv",
                             number = 5)
  model <- train(archetype ~ .,
                 data = training_decks,
                 method = method,
                 trControl = tr_control)
  return(model)
}

# Calculates summary stats for a given deck dataframe
summarize_deck <- function(deck) {
  main_stats <- summarize_deck_inner(deck[deck$mainboard,])
  if (sum(!deck$mainboard) > 0) {
    side_stats <- summarize_deck_inner(deck[!deck$mainboard,])
    return(rbind(main_stats, side_stats))
  }
  else {
    return(main_stats)
  }
}

# Inner function to calculate stats for either the sideboard or the mainboard
summarize_deck_inner <- function(deck) {
  stats <- data.frame("avg_cmc" = 0, "sd_cmc" = 0, "avg_power" = 0, "avg_tough" = 0, 
                      "avg_copies" = NA, "num_lands" = NA, "num_creatures" = NA, 
                      "num_instants" = NA, "num_sorceries" = NA, "num_artifacts" = NA, 
                      "num_enchantments" = NA, "num_planeswalkers" = NA,
                      "num_W" = NA, "num_U" = NA, "num_B" = NA, 
                      "num_R" = NA, "num_G" = NA)
  m <- sum(deck$copies)
  stats$avg_copies <- mean(deck$copies, na.rm = TRUE)
  stats$num_lands <- sum(deck[grepl("Land", deck$type),]$copies, na.rm = TRUE) / m
  stats$num_creatures <- sum(deck[grepl("Creature", deck$type),]$copies, na.rm = TRUE) / m
  stats$num_instants <- sum(deck[grepl("Instant", deck$type),]$copies, na.rm = TRUE) / m
  stats$num_sorceries <- sum(deck[grepl("Sorcery", deck$type),]$copies, na.rm = TRUE) / m
  stats$num_artifacts <- sum(deck[grepl("Artifact", deck$type),]$copies, na.rm = TRUE) / m
  stats$num_enchantments <- sum(deck[grepl("Enchantment", deck$type),]$copies, 
                                na.rm = TRUE) / m
  stats$num_planeswalkers <- sum(deck[grepl("Planeswalker", deck$type),]$copies, 
                                 na.rm = TRUE) / m
  stats$num_W = sum(str_count(deck$manaCost, "W"), na.rm = TRUE)
  stats$num_U = sum(str_count(deck$manaCost, "U"), na.rm = TRUE)
  stats$num_B = sum(str_count(deck$manaCost, "B"), na.rm = TRUE)
  stats$num_R = sum(str_count(deck$manaCost, "R"), na.rm = TRUE)
  stats$num_G = sum(str_count(deck$manaCost, "G"), na.rm = TRUE)
  
  # Scales averages appropriately by number of copies
  nonland <- deck[!grepl("Land", deck$type),]
  creatures <- deck[grepl("Creature", deck$type),]
  if (nrow(nonland) > 0) {
    n <- sum(nonland$copies)
    all_cmc <- c()
    for(i in 1:nrow(nonland)) {
      stats$avg_cmc <- stats$avg_cmc + (nonland$copies[i]/n)*nonland$cmc[i]
      for (j in 1:nonland$copies[i]) {
        all_cmc <- c(all_cmc, nonland$cmc[i])
      }
    } 
    stats$sd_cmc <- sd(all_cmc)
  }
  if (nrow(creatures) > 0) {
    n <- sum(creatures$copies)
    for(i in 1:nrow(creatures)) {
      stats$avg_power <- stats$avg_power + (creatures$copies[i]/n)*creatures$power[i]
      stats$avg_tough <- stats$avg_tough + (creatures$copies[i]/n)*creatures$tough[i]
    }
  }
  total_colors <- stats$num_W + stats$num_U + stats$num_B + stats$num_R + stats$num_G
  if (total_colors > 0) {
    stats$num_W <- stats$num_W / total_colors
    stats$num_U <- stats$num_U / total_colors
    stats$num_B <- stats$num_B / total_colors
    stats$num_R <- stats$num_R / total_colors
    stats$num_G <- stats$num_G / total_colors
  }
  return(stats)
}

# Joins decks together into one pool of cards
decks_to_pool <- function(decks) {
  if(length(decks) < 2) { 
    return(decks[[1]])
  } else {
    pool <- decks[[1]] 
    for (i in 2:length(decks)) {
      deck <- decks[[i]]
      for (j in 1:nrow(deck)) {
        card <- deck$name[j]
        if (card %in% pool$name) {
          pool$copies[pool$name == card] <- pool$copies[pool$name == card] + 1
        } else {
          valid_cols <-intersect(colnames(pool), colnames(deck[j,]))
          pool <- rbind(pool[, valid_cols], deck[j, valid_cols])
        }
      }
    }
    return(pool)
  }
}

# Loads card database from file
load_card_db <- function(db_path) {
  db <- read_json(db_path, simplifyVector = TRUE)
}

# Finds a given card's info within the card database
find_card_info <- function(card_name, card_db, num_copies = 1) {
  card_info <- NA
  found_set <- NA
  for (set in names(card_db)) {
    set_info <- card_db[[set]][["cards"]]
    is_split_card <- grep("/", card_name)
    if (length(is_split_card) > 0) {
      card_name <- strsplit(card_name, " ")[[1]][1]
    }
    ind <- grep(paste("^", card_name, "$", sep = ""), set_info$name)
    if (length(ind) != 0) {
      card_info <- set_info[ind[1],]
      found_set <- set
      card_info["found_set"] <- found_set
      card_info["copies"] <- num_copies
      break
    }
  }
  return(card_info)
}

# Summarizes all decks in a given archetype
summarize_archetype <- function(archetype, archetype_name) {
  main_df <- data.frame()
  side_df <- data.frame()
  for (deck in archetype) {
    df <- summarize_deck(deck)
    if (length(main_df) == 0) {
      main_df <- df[1,]
      side_df <- df[2,]
    } else {
      main_df <- rbind(main_df, df[1,])
      side_df <- rbind(side_df, df[2,])
    }
  }
  main_df$archetype <- archetype_name
  side_df$archetype <- archetype_name
  return(list(main_df, side_df))
}

# Gets correlation between two decks
deck_cor <- function(deck_1, deck_2, method = "cosine") {
  deck_1 <- t(unname(as.vector(deck_1)))
  deck_2 <- t(unname(as.vector(deck_2)))
  if (method == "pearson") {
    return(cor(deck_1, deck_2, method = method))
  } else if (method == "cosine") {
    return(1 - dist(t(deck_1), t(deck_2), method="cosine")[[1]])
  }
}

# Loads all decks in a given folder
load_archetype <- function(folder, card_db) {
  deck_files <- dir(folder, pattern = ".txt", full.names = TRUE)
  all_decks <- lapply(deck_files, function(x) load_deck_txt(x, card_db))
  return(all_decks)
}

# Cleans and formats data for a given deck represented by a vector of card names
load_deck_string <- function(cards, card_db) {
  
  # Reads a vector of card names into a deck dataframe
  df <- data.frame()
  first_card <- TRUE
  exclude_cols <- c("variations", "watermark", "names", "foreignData")
  mainboard <- TRUE
  for (card in cards) {
    
    num_copies <- 1
    card_info <- find_card_info(card, card_db, num_copies)
    card_info <- card_info[!(names(card_info) %in% exclude_cols)]
    card_info["mainboard"] <- mainboard
    
    # Adds new row to dataframe
    if (length(df) == 0) {
      
      # Skips card if it doesn't map to any cards in the db
      if (length(card_info) <= 1) {
        next
      }
      
      # Otherwise we instantiate dataframe
      df <- data.frame(card_info)
      colnames(df) <- names(card_info)
    } else {
      
      # Skips card if it doesn't map to any cards in the db
      if (length(card_info) <= 1) {
        next
      }
      
      # Increments the number of copies of the card if already in the deck
      if (card %in% df$name) {
        df$copies[df$name == card] <-df$copies[df$name == card] + 1
        next
      }
      
      # Ensures that the columns of all cards match
      new_card_info_cols <- colnames(df)[!(colnames(df) %in% names(card_info))]
      new_df_cols <- names(card_info)[!(names(card_info) %in% colnames(df))]
      for (col in new_card_info_cols) {
        card_info[col] <- NA
      }
      for (col in new_df_cols) {
        df[col] <- NA
      }
      
      # Adds previously un-encountered columns to card info and df
      df <- rbind(df, card_info)
    }
  }
  
  # Cleans certain values for annoying cards or categories and returns
  df <- clean_special_cases(df)
  df$cmc <- df$convertedManaCost
  df <- df[,!(colnames(df) %in% c("convertedManaCost"))]
  df$power <- as.numeric(df$power)
  df$tough <- as.numeric(df$toughness)
  df <- df[,!(colnames(df) %in% c("toughness"))]
  return(df)
}

# Cleans and formats data for a given deck loaded from txt
load_deck_txt <- function(file, card_db) {
  
  # Reads file into a df
  lines <- readLines(file)
  df <- data.frame()
  first_card <- TRUE
  exclude_cols <- c("variations", "watermark", "names")
  mainboard <- TRUE
  
  for (i in 1:length(lines)) {
    line <- lines[i]
    if ((line == "") | (line == "Sideboard")) {
      mainboard <- FALSE
      next
    }
    tokens <- strsplit(line, " ")[[1]]
    num_copies <- as.numeric(tokens[1])
    card_name <- paste(tokens[2:(length(tokens))], collapse=" ")
    card_info <- find_card_info(card_name, card_db, num_copies)
    card_info <- card_info[!(names(card_info) %in% exclude_cols)]
    card_info["mainboard"] <- mainboard
    
    # Adds new row to dataframe
    if (length(df) == 0) {
      df <- card_info
      colnames(df) <- names(card_info)
    } else {
      new_card_info_cols <- colnames(df)[!(colnames(df) %in% names(card_info))]
      new_df_cols <- names(card_info)[!(names(card_info) %in% colnames(df))]
      for (col in new_card_info_cols) {
        card_info[col] <- NA
      }
      for (col in new_df_cols) {
        df[col] <- NA
      }
      
      # Ensures that rownames don't overlap
      print(card_info)
      row.names(card_info) <- as.character(i)
      print(row.names(card_info))
      print(row.names(card_info) %in% row.names(df))
      
      # Adds previously un-encountered columns to card info and df
      df <- rbind(df, card_info)
    }
  }
  
  # Cleans certain values for annoying cards or categories and returns
  df <- clean_special_cases(df)
  df$power <- as.numeric(df$power)
  df$tough <- as.numeric(df$toughness)
  df <- df[,!(colnames(df) %in% c("toughness"))]
  return(df)
}

# Loads and formats data for a given deck loaded from csv
load_deck_csv <- function(file) {
  df <- read.csv(file)
  df <- df[,c(1, 3, 4, 5, 6, 7)]
  colnames(df) <- c("ID", "Name", "CMC", "Adj_CMC", "Type", "Sideboard")
  encoding <- data.frame(model.matrix(~Type-1, df))
  colnames(encoding) <- c("Artifact", "Creature", "Land", "Spell")
  df <- cbind(df, encoding)
  df <- df[df$ID <= 60,!(colnames(df) %in% c("Type"))]  # Removes sideboard
  return(df)
}

# Writes a given deck to a .dck file (especially for use in Forge)
write_to_dck <- function(deck, output_file, name = "deck") {
  
  # Gets the header and separates out the mainboard cards
  header <- paste("[metadata]\nName=", name, "\n[Main]", sep = "")
  deck_main <- deck[deck$mainboard,]
  main <- paste(deck_main$copies, deck_main$name)
  main <- paste(main, collapse = "\n")
  
  # Also gets the sideboard cards if applicable
  side <- ""
  if (nrow(deck_main) != nrow(deck)) {
    deck_side <- deck[!deck$mainboard,]
    side <- paste(deck_side$copies, deck_side$name)
    side <- paste(side, collapse = "\n")
  }
  
  write(paste(header, main, side, sep = "\n"), file = output_file)
}

# Replaces problematic values of certain cards
clean_special_cases <- function(deck) {
  ind <- which(deck$name == "Tarmogoyf")
  if (length(ind) > 0) {
    deck[ind,]$power = 4
    deck[ind,]$toughness = 5
  }
  ind <- which(deck$name == "Master of Etherium")
  if (length(ind) > 0) {
    deck[ind,]$power = 5
    deck[ind,]$toughness = 5
  }
  ind <- which(deck$name == "Crackling Drake")
  if (length(ind) > 0) {
    deck[ind,]$power = 3
  }
  return(deck)
}