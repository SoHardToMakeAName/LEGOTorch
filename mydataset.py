from torch.utils.data import DataLoader, Dataset
import torch

class MyDataset(Dataset):

    def __init__(self, root_dir, transform=None):#��ʼ������
        self.root_dir = root_dir
        self.images = os.listdir(self.root_dir)


    def __len__(self):#�����������ݼ��Ĵ�С
        return len(self.images)



    def __getitem__(self, index):#��������index����dataset[index]


