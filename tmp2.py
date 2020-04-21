import torch
import sys
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
device = torch.device("cpu")
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])])
testset = torchvision.datasets.CIFAR10(root='E:/LEGOTorch/venv/data', train=False, transform=transform, download=True)
testloader = DataLoader(testset, batch_size=4, shuffle=True, drop_last=False)
sys.path.append(r'E:/LEGOTorch/venv')
from testmodel2 import Net
net = Net()
net.to(device)
net.load_state_dict(torch.load('E:/LEGOTorch/venv/save_model_2.pth'))
correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data[0].to(device), data[1].to(device)
        outputs = net(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print('Accuracy of the network on the testset: %d %%' % (100 * correct / total))
