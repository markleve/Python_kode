"""
Created on Fri Mar  9 23:29:03 2018

@author: Marie Klever
"""

"""
Coding the number reckognition algorithm from scratch using a neural network
"""

import numpy as np

# importing the MINST dataset




# splitting the dataset into training, validation and test set


class NeuralNetwork(object):

    def __init__(self, sizes):
        """
        Sizes is a list containing the number of neurons in the respective layers
        An input of [2, 3, 1] indicates 2 neurons in the first layer, 3 neurons
        in the second layer an 1 neuron in the last layer.
        """
        self.num_layers = len(sizes)
        self.sizes = sizes
        # initializing random biases and weights between 0 and 1
        # does not set biases for the first layer, as it is the input layer
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]



    def SGD(self, training_data, epochs, mini_batch_size, eta, test_data=None):
        """
        Training the neural network using mini batch stochastic gradient decent
        (optimization algorithm - learning). The training_data is a list of
        tuples (x, y) representing the training inputs and desired outputs.
        """
        if test_data != None:
            test_data = list(test_data)
            n_test = len(test_data)

        training_data = list(training_data)
        n = len(training_data)

        for j in range(epochs):
            np.random.shuffle(training_data)
            mini_batches = [training_data[k:k+mini_batch_size] for k in range(0, n, mini_batch_size)]

            for mini_batch in mini_batches:
                self.update_mini_batch(mini_batch, eta)

            if test_data != None:
                # Prints the accuracy
                print("Epoch {0}: {1} / {2}".format(j, self.evaluate(test_data), n_test))

            else:
                print("Epoch {0} complete".format(j))


    def evaluate(self, test_data):
        """
        Returns the number of test inputs that the neural network predicts
        the correct result. The output is the neuron in the final layer that
        has the highest output (activation).
        """

        test_results = [(np.argmax(self.feedforward(x)), y) for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)


    def feedforward(self, a):
        """
        Returns the output of the network.
        a is the input.
        The activation function used is the sigmoid function.
        """

        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a) + b)

        return a


    def update_mini_batch(self, mini_batch, eta):
        """
        Updates the neural networks weights and biases by applying gradient
        descent using backpropagation to a single mini batch.

        eta is the learning rate
        """

        # initializes places for the updates weights and biases
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]

        for x, y in mini_batch:
            # calculates the change in the weights and biases
            delta_nabla_b, delta_nabla_w  = self.backprop(x, y)

            # puts the calculated changes in the empty initialized lists
            nabla_b = [nb + dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw + dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]

        self.biases = [b - (eta/len(mini_batch)) * nb for b, nb in zip(self.biases, nabla_b)]
        self.weights = [w - (eta/len(mini_batch)) * nw for w, nw in zip(self.weights, nabla_w)]


    def backprop(self, x, y):
        """
        Returns a tuple (nbla_b, nbla_w) representing the gradient for the
        cost function C_x. nbla_b and nbla_w are layer-by-layer lists.
        """
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]

        # feedforward
        activation = x
        activations = [x]   # store all the activations layer by layer
        zs = []             # store all the z vectors layer by layer

        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation) + b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)


        # backpropagation
        # first from the cost function to the last hidden layer
        delta = self.cost_derivative(activations[-1], y) * sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())

        # then from the last hidden layer to the next to the next and so on
        for l in range(2, self.num_layers):
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sigmoid_prime(zs[-1])
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())

        return (nabla_b, nabla_w)


    def cost_derivative(self, output_activations, y):
        """
        Returns the vector of partial derivatives (partial C_x) for the
        output activations.
        """
        return (output_activations - y)



# Different activation functions 

def sigmoid(z):
    return 1.0/(1.0 + np.exp(-z))

def sigmoid_prime(z):
    """Derivative of the activation function """
    return sigmoid(z) * (1 - sigmoid(z))
