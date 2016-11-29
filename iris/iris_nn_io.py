"""Iris dataset input/output processor.

This module creates the tensorflow graph objects needed to load the iris
dataset from CSV files.
"""

import tensorflow as tf
import iris.iris_nn as iris

_csv_defaults = [[1.] for _ in iris.FEATURES] + [[""]]

def _class_indexes(input, classes, default):
    """Map an input tensor of string class names to indexes in the class list.

    This function constructs a TF node that maps string class names
    to offsets in the class name list, using the TF case mechanism.
    """
    def when(c):
        return tf.equal(input, tf.constant(c))
    def then(i):
        return lambda: tf.constant(i)
    cases = [(when(c), then(i)) for i, c in enumerate(classes)]
    return tf.case(cases, default=then(default))


def _one_hot_class_indexes(input, classes, default):
    """Map an input tensor of string class names to a one-hot tensor."""
    return tf.one_hot(_class_indexes(input, classes, default),
                      depth=len(classes))


def _input_model(paths, num_epochs, seed):
    """Parse a set of iris CSV files into sample tensors."""
    inputs = tf.train.string_input_producer(paths,
                                            num_epochs=num_epochs,
                                            seed=seed)
    _, rows = tf.TextLineReader().read(inputs)
    cols = tf.decode_csv(rows, record_defaults=_csv_defaults)
    x = tf.pack(cols[:len(iris.FEATURES)])
    y = _one_hot_class_indexes(cols[-1], iris.CLASSES, default=-1)
    return (x, y)


def train_batch(paths, num_epochs, batch_size, seed=None):
    """Create an op to load an iris training batch.

    Args:
        paths: list of training CSV file paths
        batch_size: number of rows to read at a time into each batch
        num_epochs: number of times to read all training files
        seed: random seed

    Returns:
        x: feature batch tensor
        y: one-hot class tensor
    """
    model = _input_model(paths, num_epochs, seed)
    return tf.train.shuffle_batch(model,
                                  batch_size=batch_size,
                                  capacity=2*batch_size,
                                  min_after_dequeue=batch_size,
                                  seed=seed)


def eval_batch(paths, batch_size):
    """Create an op to load an iris test/validation batch.

    Args:
        paths: list of training CSV file paths
        batch_size: number of rows to read at a time into each batch

    Returns:
        x: feature batch tensor
        y: one-hot class tensor
    """
    model = _input_model(paths, num_epochs=1, seed=0)
    return tf.train.batch(model,
                          batch_size=batch_size,
                          allow_smaller_final_batch=True)
