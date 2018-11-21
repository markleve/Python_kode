"""
Created on Fri Mar  9 21:36:46 2018

@author: Marie Klever
"""

"""
Creating a neural network that reckognizes handwritten numbers.

It demonstrates how a neural network can be defined and executed in Tensorflow
such that it can identify handwritten digits.

Tensorflow is Google`s deep learning library.
"""

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# ----------------------------------------------------------------------------
# Defining the architecture of the neural network
#       Defines a 4 layer neural network: Input, l1, l2 and output layer
# ----------------------------------------------------------------------------

l1_nodes = 200
l2_nodes = 100
final_layer_nodes = 10

# define placeholder for data
X = tf.placeholder(dtype=tf.float32, shape=[None, 784])

# placeholder for correct labels
Y_ = tf.placeholder(dtype=tf.float32)

# define weights / layers here (output from previous layer is input to next layer)
    # ReLU is used as the activation function for the hidden layers
    # Softmax is used as the activation function for the output layer

w1 = tf.Variable(initial_value=tf.truncated_normal([784, l1_nodes], stddev=0.1))
b1 = tf.Variable(initial_value=tf.zeros([l1_nodes]))
Y1 = tf.nn.relu(tf.matmul(X, w1) + b1)

w2 = tf.Variable(initial_value=tf.truncated_normal([l1_nodes, l2_nodes], stddev=0.1))
b2 = tf.Variable(tf.zeros([l2_nodes]))
Y2 = tf.nn.relu(tf.matmul(Y1, w2) + b2)

w3 = tf.Variable(initial_value=tf.truncated_normal([l2_nodes, final_layer_nodes], stddev=0.1))
b3 = tf.Variable(tf.zeros([final_layer_nodes]))
Y = tf.nn.softmax(tf.matmul(Y2, w3) + b3)

# defien cost function and evaluation metric
cross_entropy = -tf.reduce_sum(Y_ * tf.log(Y))
is_correct = tf.equal(tf.argmax(Y, 1), tf.argmax(Y_, 1))
accuracy = tf.reduce_mean(tf.cast(is_correct, tf.float32))

# gradient descent
optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.003)
train_step = optimizer.minimize(loss=cross_entropy)


# ----------------------------------------------------------------------------
# Sets the cost function and optimiser using categorical cross entropy
#   An accuracy measure is also defined
#   The optimizer is set as gradient decent
# ----------------------------------------------------------------------------

init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)

mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
n_iter = 1000

for i in range(n_iter):
    batch_X, batch_y = mnist.train.next_batch(100)
    # associate data with placeholders
    train_data = {X: batch_X, Y_: batch_y}

    # train model
    sess.run(train_step, feed_dict=train_data)
    # capture accuracy and loss metrics
    train_a, train_c = sess.run([accuracy, cross_entropy], feed_dict=train_data)
    # measure performance on test data
    test_data = {X: mnist.test.images, Y_: mnist.test.labels}
    test_a, test_c = sess.run([accuracy, cross_entropy], feed_dict=test_data)

    if i % 100 == 0:
        print("accuracy on test data is {}".format(train_a))
