import torch
import torch.nn as nn
import torch.nn.functional as F
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.cov2 = nn.Conv2d(3,33,(3, 3),stride=(1, 1),padding=(0, 0),bias=True)
        self.cov1 = nn.Conv2d(3,33,(2, 2),stride=(1, 1),padding=(0, 0),bias=True)
        self.pool1 = nn.MaxPool2d((3, 3),stride=(1, 1),padding=(0, 0))
        self.lin1 = nn.Linear(3252744,10,bias=True)
    def forward(self,input0):
        cov2 = F.dropout(F.relu(self.cov2(input0)), p=0.5)
        cov1 = F.dropout(F.relu(self.cov1(input0)), p=0.5)
        pool1 = self.pool1(cov1)
        pool1 = F.pad(pool1, (0, 1, 0, 1))
        cov2 = F.pad(cov2, (0, 0, 0, 0))
        cat1 = torch.cat([pool1,cov2], 1)
        lin1 = F.dropout(F.leaky_relu(self.lin1(cat1.view(cat1.size()[0], -1))), p=0.5)
        return lin1
