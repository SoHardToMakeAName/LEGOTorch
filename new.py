import torch
import sys
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
sys.path.append(r'E:/LEGOTorch/venv')
from testmodel import Net
net = Net()
net.to(device)
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])
trainset = torchvisions.datasets.CIFAR(root=E:/LEGOTorch/venv/CIFAR, train=True, transform=transform, download=True)
trainloader = DataLoader(trainset, batch_size=4, shuffle=shuffle, drop_last=<PyQt5.QtWidgets.QCheckBox object at 0x0000028212B4F318>)
criterion = nn.CrossEntropyLoss(reduction=none)
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9, dempening=0, weight_decay=0, nesterov=<PyQt5.QtWidgets.QCheckBox object at 0x0000028212B4FA68>)
epochs = 10
show_every = 2
save_every = 2for epoch in range(epochs):
    running_loss = 0.0
    for i, data in enumerate(trainLoader, 0):
        inputs, labels = data[0].to(device), data[1].to(device)
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        if (i+1) % show_every == 0:
            print('epoch %d loss: %.3f' % (epoch+1, running_loss))
        if (i+1) % save_every == 0:
            torch.save(net.state_dict(), '\save_model_{}'.format(i+1))
