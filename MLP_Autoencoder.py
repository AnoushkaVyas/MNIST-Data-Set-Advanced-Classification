# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16JFVjyBlxOYykmgRUmfZxE_O5yxtffKf
"""

import torch
import torch.nn as nn
import torchvision
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import torch.nn.init as weight_init
import matplotlib.pyplot as plt
import pdb


#parameters
batch_size = 1000

preprocess = transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])

#Loading the train set file
dataset = datasets.MNIST(root='./data',
                            transform=preprocess,  
                            download=True)

loader = torch.utils.data.DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

class AE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(28*28, 256),
            nn.ReLU(),
            nn.Linear(256,64),
            nn.ReLU(),
            nn.Linear(64,2),
        )
        self.decoder = nn.Sequential(
            nn.Linear(2, 64),
            nn.ReLU(),
            nn.Linear(64, 256),
            nn.ReLU(),
            nn.Linear(256, 28*28),
            nn.Tanh()
        )
    
    def forward(self,x):
        h = self.encoder(x)
        xr = self.decoder(h)
        return xr,h

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")
print('Using CUDA ', use_cuda)

net = AE()
net = net.to(device)

#Mean square loss function
criterion = nn.MSELoss()

#Parameters
learning_rate = 1e-2
weight_decay = 1e-5

#Optimizer and Scheduler
optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate, weight_decay=weight_decay)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, threshold=0.001, patience=5, verbose = True)

num_epochs = 5

#Training
for epoch in range(num_epochs):
    total_loss, cntr = 0, 0
    
    for i,(images,_) in enumerate(loader):
        
        images = images.view(-1, 28*28)
        images = images.to(device)
        
        # Initialize gradients to 0
        optimizer.zero_grad()
        
        # Forward pass (this calls the "forward" function within Net)
        outputs, _ = net(images)
        
        # Find the loss
        loss = criterion(outputs, images)
        
        # Find the gradients of all weights using the loss
        loss.backward()
        
        # Update the weights using the optimizer and scheduler
        optimizer.step()
       
        total_loss += loss.item()
        cntr += 1
    
    scheduler.step(total_loss/cntr)

test_dataset = datasets.MNIST(root='./data',
                            transform=preprocess,  
                            download=True,train=False)
test_loader = torch.utils.data.DataLoader(dataset=dataset, batch_size=batch_size, shuffle=False)

ndata = len(dataset)
hSize = 2


iMat = torch.zeros((ndata,28*28))
rMat = torch.zeros((ndata,28*28))
featMat_train = torch.zeros((ndata,hSize))
labelMat_train = torch.zeros((ndata))
cntr=0

with torch.no_grad():
    for i,(images,labels) in enumerate(loader):

        images = images.view(-1, 28*28)
        images = images.to(device)
        
        rImg, hFeats = net(images)
        
        iMat[cntr:cntr+batch_size,:] = images
        rMat[cntr:cntr+batch_size,:] = (rImg+0.1307)*0.3081
        
        featMat_train[cntr:cntr+batch_size,:] = hFeats
        labelMat_train[cntr:cntr+batch_size] = labels
        
        cntr+=batch_size
        
        if cntr>=ndata:
            break

ndata = len(test_dataset)
hSize = 2


iMat = torch.zeros((ndata,28*28))
rMat = torch.zeros((ndata,28*28))
featMat_test = torch.zeros((ndata,hSize))
labelMat_test = torch.zeros((ndata))
cntr=0

with torch.no_grad():
    for i,(images,labels) in enumerate(test_loader):

        images = images.view(-1, 28*28)
        images = images.to(device)
        
        rImg, hFeats = net(images)
        
        iMat[cntr:cntr+batch_size,:] = images
        rMat[cntr:cntr+batch_size,:] = (rImg+0.1307)*0.3081
        
        featMat_test[cntr:cntr+batch_size,:] = hFeats
        labelMat_test[cntr:cntr+batch_size] = labels
        
        cntr+=batch_size
        
        if cntr>=ndata:
            break

# Parameters 
input_size = 2
hidden_size = 256
num_classes = 10
num_epochs = 15
learning_rate = 0.1
momentum_rate = 0.9

class Net(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size) 
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)
        
        #Weight Initialization
        for m in self.modules():
          if isinstance(m,nn.Linear):
            weight_init.xavier_normal_(m.weight)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.softmax(out)
        return out

net1 = Net(input_size, hidden_size, num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(net1.parameters(), lr=learning_rate, momentum=momentum_rate)

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")
print('Using CUDA ', use_cuda)

#Transfer to GPU device if available
net1 = net1.to(device)


# Training1
for epoch in range(num_epochs):
    
    i=0
    # For each batch of images in train set
    while(i<len(dataset)):        
        images = featMat_train[i:i+batch_size]
        labels = labelMat_train[i:i+batch_size].type(torch.LongTensor)
        i=i+batch_size
        images, labels = images.to(device), labels.to(device)
        
        # Initialize gradients to 0
        optimizer.zero_grad()
        
        # Forward pass (this calls the "forward" function within Net)
        outputs = net1(images)
        
        # Find the loss
        loss = criterion(outputs, labels)
        
        # Backward pass (Find the gradients of all weights using the loss)
        loss.backward()
        
        # Update the weights using the optimizer
        # For e.g.: w = w - (delta_w)*lr
        optimizer.step()

correct = 0
total = 0
i=0
# For each batch of images in test set
with torch.no_grad():
  while i<len(test_dataset):
      # Get the images
      images = featMat_test[i:i+batch_size]
      labels=labelMat_test[i:i+batch_size]
      images = images.to(device)
      i=i+batch_size
      # Find the output by doing a forward pass through the network
      outputs = net1(images)

      # Find the class of each sample by taking a max across the probabilities of each class
      _, predicted = torch.max(outputs.data, 1)

      # Increment 'total', and 'correct' according to whether the prediction was correct or not
      total += labels.size(0)
      correct += (predicted.cpu() == labels).sum()
acc1=100*correct/total
print('Accuracy of the network on the 10000 test images (features): %d %%' % (100 * correct / total))

# Parameters 
input_size = 784
hidden_size = 256
num_classes = 10
num_epochs = 15
learning_rate = 0.1
momentum_rate = 0.9

class Net(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size) 
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)
        
        #Weight Initialization
        for m in self.modules():
          if isinstance(m,nn.Linear):
            weight_init.xavier_normal_(m.weight)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.softmax(out)
        return out

net2 = Net(input_size, hidden_size, num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(net2.parameters(), lr=learning_rate, momentum=momentum_rate)

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")
print('Using CUDA ', use_cuda)

#Transfer to GPU device if available
net2 = net2.to(device)


# Training
for epoch in range(num_epochs):
    
    # For each batch of images in train set
    for i, (images, labels) in enumerate(loader):
        
        images = images.view(-1, 28*28)
        labels = labels
        
        images, labels = images.to(device), labels.to(device)
        
        # Initialize gradients to 0
        optimizer.zero_grad()
        
        # Forward pass (this calls the "forward" function within Net)
        outputs = net2(images)
        
        # Find the loss
        loss = criterion(outputs, labels)
        
        # Backward pass (Find the gradients of all weights using the loss)
        loss.backward()
        
        # Update the weights using the optimizer
        # For e.g.: w = w - (delta_w)*lr
        optimizer.step()

correct = 0
total = 0

# For each batch of images in test set
with torch.no_grad():
  for images, labels in test_loader:

      # Get the images
      images = images.view(-1, 28*28)

      images = images.to(device)

      # Find the output by doing a forward pass through the network
      outputs = net2(images)

      # Find the class of each sample by taking a max across the probabilities of each class
      _, predicted = torch.max(outputs.data, 1)

      # Increment 'total', and 'correct' according to whether the prediction was correct or not
      total += labels.size(0)
      correct += (predicted.cpu() == labels).sum()
acc2=100*correct/total
print('Accuracy of the network on the 10000 test images (raw pixels): %d %%' % (100 * correct / total))

import numpy as np
objects = ('Features', 'Raw Pixel')
y_pos = np.arange(len(objects))
plt.bar(y_pos, [acc1,acc2], align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.xlabel('Type of Data')
plt.title('Accuracy')
plt.show()