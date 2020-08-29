import torch
import torch.nn as nn

# Neural network architecture
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