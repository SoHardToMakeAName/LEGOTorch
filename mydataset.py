from torch.utils.data import DataLoader, Dataset
import torch

class MyDataset(Dataset):

    def __init__(self, root_dir, transform=None):#初始化参数
        self.root_dir = root_dir
        self.images = os.listdir(self.root_dir)


    def __len__(self):#返回整个数据集的大小
        return len(self.images)



    def __getitem__(self, index):#根据索引index返回dataset[index]


