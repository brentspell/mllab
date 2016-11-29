"""Neural network iris flower classification model.

This module creates the tensorflow graph objects needed to train, test, and
apply the iris classifier.

https://en.wikipedia.org/wiki/Iris_flower_data_set
"""

import tensorflow as tf

FEATURES = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
CLASSES  = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']


def inference(samples):
    """Construct the iris neural network prediction model.

    Iris prediction uses a single layer neural network, which outputs
    a one-hot vector y that indicates the class probabilities.

    Args:
        samples: [BATCH_SIZE, NUM_FEATURES] input tensor with feature values.

    Returns:
        logits: [BATCH_SIZE, NUM_CLASSES] one-hot output tensor with
                computed logits.
    """
    with tf.name_scope('softmax_linear'):
        x = samples
        w = tf.Variable(tf.truncated_normal([len(FEATURES), len(CLASSES)]),
                        name='w')
        b = tf.Variable(tf.zeros([len(CLASSES)]),
                        name='b')
        return tf.matmul(x, w) + b


def loss(logits, labels):
    """Calculate the iris loss function

    Args:
        logits: [BATCH_SIZE, NUM_CLASSES] one-hot tensor of iris class
                predictions against the training samples.
        labels: [BATCH_SIZE, NUM_CLASSES] one-hot tensor of training labels.

    Returns:
        loss: Scalar tensor containing the result of the loss function.
    """
    error = tf.nn.softmax_cross_entropy_with_logits(logits,
                                                    labels,
                                                    name='error')
    return tf.reduce_mean(error, name='error_mean')


def training(loss, rate):
    """Create the model training operation tensor

    The training operation executes a single step of gradient descent,
    which calculates the loss function and updates training weights.

    Args:
        loss: Operation to calculate the loss function.
        rate: Learning rate for gradient descent.

    Returns:
        op: Tensorflow op for a single training step
    """
    # Add a summary to snapshot the loss calculation.
    tf.scalar_summary('loss', loss)
    # Track the current training step.
    global_step = tf.Variable(0, name='global_step', trainable=False)
    # Create the gradient adaptive momentum optimizer.
    optimizer = tf.train.AdamOptimizer(rate)
    return (optimizer.minimize(loss, global_step=global_step), global_step)


def evaluation(logits, labels):
    """Evaluate the model against a labeled batch.

    Compare the calculated one-hot logits against the labeled batch,
    computing a hit if the maximum (k=1) index of logits is the same
    as the maximum index of labels.

    Args:
        logits: [BATCH_SIZE, NUM_CLASSES] one-hot tensor of iris class
                predictions against the test samples.
        labels: [BATCH_SIZE, NUM_CLASSES] one-hot tensor of test labels.

    Returns:
        hits:  Tensor containing a 1 for each hit and a 0 for each miss.
    """
    return tf.nn.in_top_k(logits, labels, k=1)
