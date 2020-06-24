# NNetBot Training
# daniel.brooks@alumni.caltech.edu and henry.neil.ward@gmail.com
# June 23, 2020 <br>  

# Preprocessing imports
import numpy as np
import os
import pandas as pd
import pickle
from sklearn import preprocessing
from tqdm import tqdm

# Draftsim and NNetBot architecture import
import draftsimtools as ds
from draftsimtools import DraftNet

# Torch imports
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data.dataset import Dataset

######
# UTILITY FUNCTIONS
######

# Loads pickled data
def load_data(path):
    """
    Load a pickle file from disk. 
    """
    with open(path, "rb") as f:
        return pickle.load(f)

######
# PARAMETER SETTING
######

# Sets folder where training data lives
data_folder = "../bots/bots_data/nnet_train/"

# Sets additional parameters
num_epochs = 1
use_features = False
device = torch.device("cpu")

######
# DATA LOADING
######

# Makes label encoder
m19_set = pd.read_csv(data_folder + 'standardized_m19_rating.tsv', delimiter="\t")
m19_set["Color Vector"] = [eval(s) for s in m19_set["Color Vector"]]
le = ds.create_le(m19_set["Name"].values)

# Loads splits of training and validation data
split1_train = load_data(data_folder + 'split1_train.pkl')
split1_train = ds.DraftDataset(split1_train, le)
split1_val = load_data(data_folder + 'split1_val.pkl')
split1_val = ds.DraftDataset(split1_val, le)
split2_train = load_data(data_folder + 'split2_train.pkl')
split2_train = ds.DraftDataset(split2_train, le)
split2_val = load_data(data_folder + 'split2_val.pkl')
split2_val = ds.DraftDataset(split2_val, le)
split3_train = load_data(data_folder + 'split3_train.pkl')
split3_train = ds.DraftDataset(split3_train, le)
split3_val = load_data(data_folder + 'split3_val.pkl')
split3_val = ds.DraftDataset(split3_val, le)

# Loads testing data
drafts_tensor_train = load_data(data_folder + 'drafts_tensor_train.pkl')
train_dataset = ds.DraftDataset(drafts_tensor_train, le)
drafts_tensor_test = load_data(data_folder + 'drafts_tensor_test.pkl')
test_dataset = ds.DraftDataset(drafts_tensor_test, le)

######
# NNET UTILITY FUNCTIONS
######

def create_set_vector(casting_cost, card_type, rarity, color_vector):
    """
    Returns a feature-encoded card property vector. 
    
    There are 21 binary features:
    
    0. cmc=0
    1. cmc=1
    2. cmc=2
    3. cmc=3
    4. cmc=4
    5. cmc=5
    6. cmc=6
    7. cmc>=7
    8. creature?
    9. common?
    10. uncommon?
    11. rare?
    12. mythic?
    13. colorless?
    14. monocolored?
    15. multicolored?
    16. color1?
    17. color2?
    18. color3?
    19. color4?
    20. color5?
    
    :param casting_cost: integer casting cost of card
    :param card_type: "Creature" or other
    :param rarity": "C", "U", "R", or "M"
    "param color_vector": vector corresponding to colors of card, example: [1,0,0,0,1]
    
    """
    # Initialize set vector
    v = [0] * 21
    
    # Encode cmc
    if casting_cost == 0:
        v[0] = 1
    elif casting_cost == 1:
        v[1] = 1
    elif casting_cost == 2:
        v[2] = 1
    elif casting_cost == 3:
        v[3] = 1
    elif casting_cost == 4:
        v[4] = 1
    elif casting_cost == 5:
        v[5] = 1
    elif casting_cost == 6:
        v[6] = 1
    elif casting_cost >= 7:
        v[7] = 1
    else:
        print("WARNING: Undefined casting cost.")
    
    # Encode type
    if card_type == "Creature":
        v[8] = 1
        
    # Encode rarity
    if rarity == "C":
        v[9] = 1
    elif rarity == "U":
        v[10] = 1
    elif rarity == "R":
        v[11] = 1
    elif rarity == "M":
        v[12] = 1
    
    # Process number of colors
    num_colors = len([c for c in color_vector if c > 0])
    if num_colors == 0:
        v[13] = 1
    elif num_colors == 1:
        v[14] = 1
    elif num_colors >= 2:
        v[15] = 1
    
    # Process card color
    if color_vector[0] > 0:
        v[16] = 1
    if color_vector[1] > 0:
        v[17] = 1
    if color_vector[2] > 0:
        v[18] = 1
    if color_vector[3] > 0:
        v[19] = 1
    if color_vector[4] > 0:
        v[20] = 1
    return v

def cmc_from_string(cmc_string):
    """
    Return an integer converted mana cost from cmc_string. 
    
    Each character adds 1 to cmc. 
    
    :param cmc_string: String or integer representation of cmc. Example: "1UBR".
    :returns: Integer cmc. Example: 4.
    """
    # If int, we are done
    if type(cmc_string) is int:
        return cmc_string
    
    # Convert string to integer cmc
    cmc = 0
    digit_string = ""
    letters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    digits = set("1234567890")
        
    for c in cmc_string:        
        if c in letters:
            cmc += 1
        else:
            digit_string += c
    if len(digit_string) > 0:
        cmc += int(digit_string)
    return cmc

def create_set_tensor(magic_set):
    """
    Returns a set tensor which represents the properties of cards in the set.
    
    There are M features and N cards in the set and the tensor is of size M x N.
    
    The features are documented in the create_set_vector() function. 
    """
    set_list = []
    
    # Requires these names to be present in the set file 
    reduced_set = magic_set[["Name", "Casting Cost 1", "Card Type", "Rarity", "Color Vector"]]
    for index, row in reduced_set.iterrows():
        card_vector = create_set_vector(cmc_from_string(row[1]), row[2], row[3], row[4])
        set_list.append(card_vector)
        
    # set_list is currently N x M list of lists 
    set_flipped = torch.Tensor(set_list)
    set_tensor = torch.transpose(set_flipped, 0, 1)
    return set_tensor

######
# NNET TRAINING FUNCTIONS
######

def train_net(net, dataloader, num_epoch, optimizer):
    """Train the network."""
    net.train()    
    my_count = 0
    for epoch in range(num_epoch):
        
        # Loop over x,y for each dataset
        running_loss = 0
        for i, data in enumerate(dataloader):
        
            my_count+=1
            if my_count % 10000 == 0:
                print(my_count)
        
            # Get the inputs, keeping batch size
            x, y = data
            
            # cuda() is needed for GPU mode, not sure why
            if device.type != "cpu":
                x = x.cuda()
                y = y.cuda() # Feature vector
            
            # Zero parameter gradients between batches
            optimizer.zero_grad()
        
            # Perform training
            y_pred = net(x)
            y_integer = torch.argmax(y, 1) # Class indices
            
            # Use cross entropy loss 
            loss = torch.nn.CrossEntropyLoss()
            output = loss(y_pred, y_integer)
            output.backward()
            optimizer.step()
                        
            # Print loss data
            running_loss += output.item()
            step = 1
            if i % len(dataloader) == len(dataloader)-1 and (epoch + 1) % step == 0:
                print('Train Cross-Entropy Loss: %.6f' % (running_loss/len(dataloader)))
                running_loss = 0.0

def val_net(net, dataloader):
    """Compute accuracy on validation set."""
    net.eval()
    correct = 0.0
    total = 0.0
    
    with torch.no_grad():
        for i, data in enumerate(dataloader):
        
            # Get the inputs, keeping batch size
            x, y = data
            
            # cuda() is needed for GPU mode, not sure why
            if device.type != "cpu":
                x = x.cuda()
                y = y.cuda()
            y_integer = torch.argmax(y, 1) # Class indices
            
            # Compute val loss
            y_pred = net(x)
            y_pred_integer = torch.argmax(y_pred, 1)
            
            # Compute accuracy
            correct += int(sum(y_pred_integer == y_integer))
            total += len(y_integer)
            
    accuracy = correct / total
    print("Validation accuracy:", accuracy, " Total picks:", int(total))
    return accuracy

######
# MAIN SCRIPT
######

# Makes set tensor
st = create_set_tensor(m19_set)
if device.type != "cpu":
    st = st.cuda()

# Define dataloaders for complete datasets
trainloader = torch.utils.data.DataLoader(train_dataset, batch_size=100, shuffle=True)
testloader = torch.utils.data.DataLoader(test_dataset, batch_size=100, shuffle=False)

# Define dataloaders for cross-validation splits
split1_train_loader = torch.utils.data.DataLoader(split1_train, batch_size=100, shuffle=True)
split1_val_loader = torch.utils.data.DataLoader(split1_val, batch_size=100, shuffle=False)
split2_train_loader = torch.utils.data.DataLoader(split2_train, batch_size=100, shuffle=True)
split2_val_loader = torch.utils.data.DataLoader(split2_val, batch_size=100, shuffle=False)
split3_train_loader = torch.utils.data.DataLoader(split3_train, batch_size=100, shuffle=True)
split3_val_loader = torch.utils.data.DataLoader(split3_val, batch_size=100, shuffle=False)

# Creates networks
split1_net = DraftNet(st, use_features = use_features)
split2_net = DraftNet(st, use_features = use_features)
split3_net = DraftNet(st, use_features = use_features)
final_net = DraftNet(st, use_features = use_features)
if device.type != "cpu":
    split1_net = split1_net.cuda()
    split2_net = split2_net.cuda()
    split3_net = split3_net.cuda()
    final_net = final_net.cuda()

# Makes optimizers
optimizer1 = optim.Adam(split1_net.parameters(), lr=0.001, betas=(0.9, 0.999))
optimizer2 = optim.Adam(split2_net.parameters(), lr=0.001, betas=(0.9, 0.999))
optimizer3 = optim.Adam(split3_net.parameters(), lr=0.001, betas=(0.9, 0.999))

# Trains network on three splits of training data to get 3-fold cross-validated training accuracies
ep = 1
val_acc1 = []
val_acc2 = []
val_acc3 = []
for run in range(num_epochs):
    print("Split 1 epoch:", ep)
    train_net(split1_net, split1_train_loader, 1, optimizer1)
    val_acc1.append(val_net(split1_net, split1_val_loader))
    ep += 1
torch.save(split1_net, "bots_data/draftnet_split1_june23_2020_ep.pt")
ep = 1
for run in range(num_epochs):
    print("Split 2 epoch:", ep)
    train_net(split2_net, split2_train_loader, 1, optimizer2)
    val_acc2.append(val_net(split2_net, split2_val_loader))
    ep += 1
torch.save(split2_net, "bots_data/draftnet_split2_june23_2020_ep.pt")
ep = 1
for run in range(num_epochs):
    print("Split 3 epoch:", ep)
    train_net(split3_net, split3_train_loader, 1, optimizer3)
    val_acc3.append(val_net(split3_net, split3_val_loader))
    ep += 1
torch.save(split3_net, "bots_data/draftnet_split3_june23_2020_ep.pt")

# Joins validation accuracies to dataframe and writes to file
val_accuracies = pd.DataFrame(
    {'split1_acc': val_acc1,
     'split2_acc': val_acc2,
     'split3_acc': val_acc3
    })
val_accuracies.to_csv('bots_data/val_accuracies.csv', index=False)

# Trains final network on entire dataset
optimizer = optim.Adam(final_net.parameters(), lr=0.001, betas=(0.9, 0.999))
ep = 1
test_acc = []
for run in range(num_epochs):
    print("Epoch:", ep)
    train_net(final_net, trainloader, 1, optimizer)
    test_acc.append(val_net(final_net, testloader))
    #torch.save(final_net, "draftnet_june23_2020_ep" + str(ep)  + ".pt")
    ep += 1

# Writes final network and test accuracy to file
torch.save(final_net, "bots_data/draftnet_june23_2020_ep.pt")
with open('bots_data/test_accuracies.txt', 'w') as f:
    for line in test_acc:
        f.write("%s\n" % line)

