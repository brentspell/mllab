import tensorflow as tf
import pandas as pd
import numpy as np
import math

# parameters
TEST_BATCH     = 100
FEATURES       = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
CLASSES        = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]
CSV_DEFAULTS   = [[1.] for _ in FEATURES] + [[""]]

def class_indexes(input, classes, default):
    def when(c):
        return tf.equal(input, tf.constant(c))
    def then(i):
        return lambda: tf.constant(i)
    cases = [(when(c), then(i)) for i, c in enumerate(classes)]
    return tf.case(cases, default=then(default))

def one_hot_class_indexes(input, classes, default):
    return tf.one_hot(class_indexes(input, classes, default),
                      depth=len(classes))

tf.reset_default_graph()

inputs  = tf.train.string_input_producer(["../data/iris/iris_test.csv"],
                                         num_epochs=1)
_, rows = tf.TextLineReader().read(inputs)
cols    = tf.decode_csv(rows, record_defaults=CSV_DEFAULTS)
x       = tf.pack(cols[:len(FEATURES)])
y_      = one_hot_class_indexes(cols[-1], CLASSES, default=-1)
x, y_   = tf.train.batch((x, y_),
                         batch_size=TEST_BATCH,
                         allow_smaller_final_batch=True)

w = tf.Variable(tf.truncated_normal([len(FEATURES), len(CLASSES)]), name="w")
b = tf.Variable(tf.zeros([len(CLASSES)]), name="b")

y = tf.nn.softmax(tf.matmul(x, w) + b)
e = tf.cast(tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1)), 'int32')

saver = tf.train.Saver([w, b])
save_path = "../model/iris/"

with tf.Session() as session:
    session.run(tf.initialize_all_variables())
    session.run(tf.initialize_local_variables())

    saver.restore(session, tf.train.latest_checkpoint(save_path))

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    total_match = 0
    total_count = 0

    try:
        while True:
            m, c = session.run((tf.reduce_sum(e), tf.shape(e)))
            total_match += m
            total_count += c[0]
    except tf.errors.OutOfRangeError:
        pass
    finally:
        coord.request_stop()
        coord.join(threads)

    print()
    print("model:    ", tf.train.latest_checkpoint(save_path))
    print("matches:  ", total_match)
    print("count:    ", total_count)
    print("accuracy: ", + (total_match / total_count))
