# Torch imports      
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data.dataset import Dataset

# Implements NN
class DraftNet(nn.Module):
    
    def __init__(self, set_tensor):
        """Placeholder NN. Currently does nothing.
        
        param ss: number of cards in set
        param set_tensor: Mxss set tensor describing the set
        """
        super(DraftNet, self).__init__()
        
        # Load set tensor.
        self.set_tensor = set_tensor
        self.set_tensor_tranpose = torch.transpose(set_tensor, 0, 1)
        self.M, self.ss = self.set_tensor.shape
        self.half_ss = self.ss / 2
        
        # Specify layer sizes. 
        size_in = self.ss + self.M
        #size_in = self.ss
        size1 = self.ss
        size2 = self.ss
        size3 = self.ss
        size4 = self.ss
        size5 = self.ss
        size6 = self.ss
        size7 = self.ss
        size8 = self.ss
        
        self.ns = 0.01
        
        self.bn = nn.BatchNorm1d(self.ss + self.M)
        
        self.linear1 = torch.nn.Linear(size_in, size1)
        self.bn1 = nn.BatchNorm1d(size1)
        self.relu1 = torch.nn.LeakyReLU(negative_slope = self.ns)
        self.dropout1 = nn.Dropout(0.5)
        
        self.linear2 = torch.nn.Linear(size1, size2)
        self.bn2 = nn.BatchNorm1d(size2)
        self.relu2 = torch.nn.LeakyReLU(negative_slope = self.ns)
        self.dropout2 = nn.Dropout(0.5)
        
        self.linear3 = torch.nn.Linear(size2, size3)
        self.bn3 = nn.BatchNorm1d(size3)
        self.relu3 = torch.nn.LeakyReLU(negative_slope = self.ns)
        self.dropout3 = nn.Dropout(0.5)
        
        self.linear4 = torch.nn.Linear(size3, size4)
        self.relu4 = torch.nn.LeakyReLU(negative_slope = self.ns)
        self.dropout4 = nn.Dropout(0.5)
        
        self.linear5 = torch.nn.Linear(size3, size5)
        self.relu5 = torch.nn.LeakyReLU(negative_slope = self.ns)
        self.dropout5 = nn.Dropout(0.5)
        
        self.linear6 = torch.nn.Linear(size3, size6)
        self.relu6 = torch.nn.LeakyReLU(negative_slope = self.ns)
        self.dropout6 = nn.Dropout(0.5)
        
        self.linear7 = torch.nn.Linear(size3, size7)
        self.relu7 = torch.nn.LeakyReLU(negative_slope = self.ns)
        self.dropout7 = nn.Dropout(0.5)
        
        self.linear8 = torch.nn.Linear(size3, size8)
        self.relu8 = torch.nn.LeakyReLU(negative_slope = self.ns)
        
        
        #self.sm = torch.nn.Softmax()
                
    def forward(self, x):
        
        collection = x[:, :self.ss]
        
        #collection = self.bn(collection)
        
        pack = x[:, self.ss:]
        
        # Get features from set tensor. 
        features = torch.mm(collection, self.set_tensor_tranpose)
        collection_and_features = torch.cat((collection, features), 1)
        
        collection_and_features = self.bn(collection_and_features)
        
        #y = self.linear1(collection_and_features)
        y = self.linear1(collection_and_features)
        y = self.bn1(y)
        y = self.relu1(y)
        y = self.dropout1(y)
        
        y = self.linear2(y)
        y = self.bn2(y)
        y = self.relu2(y)
        y = self.dropout2(y)
        
        y = self.linear3(y)
        y = self.bn3(y)
        y = self.relu3(y)
        y = self.dropout3(y)

        y = self.linear4(y)
        #y = self.relu4(y)
        #y = self.dropout4(y)
        
        #y = self.linear5(y)
        #y = self.relu5(y)
        #y = self.dropout5(y)
        
        #y = self.linear6(y)
        #y = self.relu6(y)
        #y = self.dropout6(y)
        
        #y = self.linear7(y)
        #y = self.relu7(y)
        #y = self.dropout7(y)
        
        #y = self.linear8(y)
        #y = self.relu8(y)
        
        y = y * pack # Enforce cards in pack only.
        
        return y
        self.le = le
        self.cards_in_set = len(self.le.classes_)
        self.pack_size = int(self.drafts_tensor.shape[1]/3)
        self.draft_size = self.pack_size*3
        
    def __getitem__(self, index):
        """Return a training example.
        """
        #Grab information on current draft.
        pick_num = index % self.draft_size #0-self.pack_size*3-1
        draft_num = int((index - pick_num)/self.draft_size)
        
        #Generate.
        x = self.create_new_x(pick_num, draft_num)
        y = self.create_new_y(pick_num, draft_num)
        return x, y
    
    def create_new_x(self, pick_num, draft_num):
        """Generate x, input, as a row vector.
        0:n     : collection vector
                  x[i]=n -> collection has n copies of card i
        n:2n    : pack vector
                  0 -> card not in pack
                  1 -> card in pack
        Efficiency optimization possible. Iterative adds to numpy array.
        """
        #Initialize collection / cards in pack vector.
        x = np.zeros([self.cards_in_set * 2], dtype = "int16")
        
        #Fill in collection vector excluding current pick (first half).
        for n in self.drafts_tensor[draft_num, :pick_num, 0]:
            x[n] += 1
            
        #Fill in pack vector.
        cards_in_pack =  self.pack_size - pick_num%self.pack_size #Cards in current pack.
        for n in self.drafts_tensor[draft_num, pick_num, :cards_in_pack]:
            x[n + self.cards_in_set] = 1
            
        #Convert to Torch tensor.
        x = torch.Tensor(x)
        return x
    
    def create_new_y(self, pick_num, draft_num, not_in_pack=0.5):
        """Generate y, a target pick row vector.
        Picked card is assigned a value of 1.
        Other cards are assigned a value of 0.
        """
        #Initialize target vector.
        #y = np.array([0] * self.cards_in_set)
        y = np.zeros([self.cards_in_set], dtype = "int16")
            
        #Add picked card.
        y[self.drafts_tensor[draft_num, pick_num, 0]] = 1
        #y = torch.Tensor(y, dtype=torch.int64) # Needed as target.
        y = torch.tensor(y, dtype=torch.int64, device=device) # Needed as target.
        return y
    
    def __len__(self):
        return len(self.drafts_tensor) * self.draft_size