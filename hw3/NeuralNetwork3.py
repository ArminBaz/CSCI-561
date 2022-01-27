import os
import math
import pandas as pd
import numpy as np
import sys

###    MLP Class    ####
class MLP:
    def __init__(self, batch_size, learning_rate, num_epochs):
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        
        # intialize the weights and biases for the hidden layers
        self.params = {
            'W1':np.random.randn(512, 784) * np.sqrt(1.0 / 784),
            'b1':np.random.randn(512,1) * np.sqrt(1.0 / 748),
            'W2':np.random.randn(256, 512) * np.sqrt(1.0 / 512),
            'b2':np.random.randn(256,1) * np.sqrt(1.0/ 512),
            'W3':np.random.randn(10, 256) * np.sqrt(1.0 / 256),
            'b3':np.random.randn(10,1) * np.sqrt(1.0 / 256)
        }
        
    # define sigmoid activation function
    def sigmoid(self, x):
        x = np.clip(x, -500, 500)
        return 1.0/(1.0 + np.exp(-x))
    
    # sigmoid backward
    def sigmoid_backward(self, dA, Z):
        sig = self.sigmoid(Z)
        return dA * sig * (1 - sig)
    
    # define softmax activation function
    def softmax(self, x):
        exps = np.exp(x - x.max())
        return exps / np.sum(exps, axis=0)
    
    # define cross-entropy cost function
    def cross_entropy_loss(self, Y, out):
        m = Y.shape[1]

        cost = (-1 / m) * np.sum(np.multiply(Y, np.log(out)) + np.multiply(1 - Y, np.log(1 - out)))
        cost = np.squeeze(cost)

        return cost
    
    # compute accuracy of model given x and y inputs
    def get_accuracy(self, X, y):
        predictions = []

        cache = self.forward_pass(X)
        output = cache['A3']
        pred = np.argmax(output, axis=0)
        predictions.append(pred == np.argmax(y, axis=0))
        
        return np.mean(predictions)
        
    
    # splits x and y into a list of mini-batches
    def get_mini_batches(self, X, y, batch_size):
        m = X.shape[1]
        mini_batches = list()
        num_batches = math.floor(m/batch_size)
        for i in range(0, num_batches):
            mb_X = X[:, i * batch_size : (i+1) * batch_size]
            mb_y = y[:, i * batch_size : (i+1) * batch_size]
            mini_batch = (mb_X, mb_y)
            mini_batches.append(mini_batch)

        # end case
        if m % batch_size != 0:
            mb_X = X[:, batch_size * math.floor(m / batch_size) : m]
            mb_y = y[:, batch_size * math.floor(m / batch_size) : m]
            mini_batch = (mb_X, mb_y)
            mini_batches.append(mini_batch)

        return mini_batches

    
    # forward pass
    def forward_pass(self, X):
        cache = dict()
        
        cache['Z1'] = np.dot(self.params['W1'], X) + self.params['b1']
        cache['A1'] = self.sigmoid(cache['Z1'])
        cache['Z2'] = np.dot(self.params['W2'], cache['A1']) + self.params['b2']
        cache['A2'] = self.sigmoid(cache['Z2'])
        cache['Z3'] = np.dot(self.params['W3'], cache['A2']) + self.params['b3']
        cache['A3'] = self.softmax(cache['Z3'])
        
        return cache
    
    # backward pass
    def backward_pass(self, X, Y, cache):
        m = X.shape[1]
        
        # error at last layer
        dZ3 = cache['A3'] - Y
        
        # gradients at last layer
        m3 = cache["A2"].shape[1]
        dW3 = np.dot(dZ3, cache["A2"].T) / m
        db3 = np.sum(dZ3, axis=1, keepdims=True) / m
        
        # back propagate through first layer
        dA2 = np.dot(self.params['W3'].T, dZ3)
        dZ2 = self.sigmoid_backward(dA2, cache['Z2'])
        
        # gradients of middle layer
        m2 = cache['A1'].shape[1]
        dW2 = np.dot(dZ2, cache['A1'].T) / m
        db2 = np.sum(dZ2, axis=1, keepdims=True) / m
        
        # back propagate through middle layer
        dA1 = np.dot(self.params['W2'].T, dZ2)
        dZ1 = self.sigmoid_backward(dA1, cache['Z1'])
        
        # gradients of first layer
        m1 = X.shape[1]
        dW1 = np.dot(dZ1, X.T) / m
        db1 = np.sum(dZ1, axis=1, keepdims=True) / m
    
        grads = {'dW3':dW3, 'db3':db3, 'dW2':dW2, 'db2':db2, 'dW1':dW1, 'db1':db1}
        
        return grads
        
    # main training function 
    def train(self, X, y):
        # loop through number of iterations
        for i in range(0, self.num_epochs):
            # shuffle X and y
            random = np.arange(len(X[1]))
            np.random.shuffle(random)
            X_shuffle = X[:,random]
            y_shuffle = y[:,random]
            
            # get mini-batches of X and y
            mini_batches = self.get_mini_batches(X_shuffle, y_shuffle, self.batch_size)
            
            for mini_batch in mini_batches:
                mb_x, mb_y = mini_batch
                cache = self.forward_pass(mb_x)
                grads = self.backward_pass(mb_x, mb_y, cache) 

                # update parameters
                self.params['W1'] = self.params['W1'] - (self.learning_rate * grads['dW1'])
                self.params['b1'] = self.params['b1'] - (self.learning_rate * grads['db1'])
                self.params['W2'] = self.params['W2'] - (self.learning_rate * grads['dW2'])
                self.params['b2'] = self.params['b2'] - (self.learning_rate * grads['db2'])
                self.params['W3'] = self.params['W3'] - (self.learning_rate * grads['dW3'])
                self.params['b3'] = self.params['b3'] - (self.learning_rate * grads['db3'])


            

####    Read in data    ####
trainX_in = pd.read_csv(sys.argv[1], header=None)
trainY_in = pd.read_csv(sys.argv[2], header=None)
testX_in = pd.read_csv(sys.argv[3], header=None)

# Transpose the matrices to make it fit dimensions of model
trainX = trainX_in.T
trainY = trainY_in.T
testX = testX_in.T

# convert pandas dataframes to numpy arrays
trainX = trainX.values
trainY = trainY.values
testX = testX.values

# convert y train and test to be one hot
onehotY = np.zeros((trainY.size, trainY.max()+1))
onehotY[np.arange(trainY.size), trainY] = 1
onehotY = onehotY.T



####    Create and Train Neural Network    ####

# construct MLP Object
NeuralNetwork = MLP(batch_size=32, learning_rate=0.01, num_epochs=80)

# train MLP
NeuralNetwork.train(trainX, onehotY)

# get predictions on test
cache = NeuralNetwork.forward_pass(testX)
output = cache['A3']
pred = np.argmax(output, axis=0)

# write out the test set predictions
pd.DataFrame(pred).to_csv('test_predictions.csv', header=None, index=None)



