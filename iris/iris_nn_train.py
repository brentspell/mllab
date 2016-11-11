import tensorflow as tf
import pandas as pd
import numpy as np
from datetime import datetime
import math
import os

RANDOM_SEED  = 0
LEARN_RATE   = 0.1
TRAIN_EPOCHS = 2000
TRAIN_BATCH  = 100
FEATURES     = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
CLASSES      = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
CSV_DEFAULTS = [[1.] for _ in FEATURES] + [[""]]

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

inputs  = tf.train.string_input_producer(["../data/iris/iris_train.csv"],
                                         num_epochs=TRAIN_EPOCHS,
                                         seed=RANDOM_SEED)
_, rows = tf.TextLineReader().read(inputs)
cols    = tf.decode_csv(rows, record_defaults=CSV_DEFAULTS)
x       = tf.pack(cols[:len(FEATURES)])
y_      = one_hot_class_indexes(cols[-1], CLASSES, default=-1)
x, y_   = tf.train.shuffle_batch((x, y_),
                                 num_threads=8,
                                 batch_size=TRAIN_BATCH,
                                 capacity=2*TRAIN_BATCH,
                                 min_after_dequeue=TRAIN_BATCH,
                                 seed=RANDOM_SEED)

w = tf.Variable(tf.truncated_normal([len(FEATURES), len(CLASSES)]), name='w')
b = tf.Variable(tf.zeros([len(CLASSES)]), name='b')

y = tf.matmul(x, w) + b
global_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))
tf.scalar_summary('loss', global_loss)

global_step = tf.Variable(0, name='global_step', trainable=False)
optimizer   = tf.train.AdamOptimizer(LEARN_RATE)
train_op    = optimizer.minimize(global_loss, global_step=global_step)

saver = tf.train.Saver(tf.all_variables())
save_path = "../model/iris/"
os.makedirs(save_path, exist_ok=True)
save_path += "model"

summary_path = "../log/iris/" + datetime.now().strftime("%Y%m%d%H%M%S")
os.makedirs(summary_path, exist_ok=True)
summary_op = tf.merge_all_summaries()

with tf.Session() as session:
    coord  = tf.train.Coordinator()
    writer = tf.train.SummaryWriter(summary_path, session.graph)

    session.run(tf.initialize_all_variables())
    session.run(tf.initialize_local_variables())

    threads = tf.train.start_queue_runners(coord=coord)

    try:
        while not coord.should_stop():
            _, step, loss = session.run((train_op, global_step, global_loss))
            assert not np.isnan(loss), "model diverged with loss = NaN"
            if (step % 100 == 0):
                saver.save(session, save_path, global_step=global_step)
                summary = session.run(summary_op)
                writer.add_summary(summary, step)
                print("step: {0} loss: {1}".format(step, loss))
    except tf.errors.OutOfRangeError:
        pass
    finally:
        saver.save(session, save_path, global_step=global_step)
        writer.flush()
        coord.request_stop()
        coord.join(threads)

# todo: push changes, disable logging, rename venv .venv
# unsupervised sentiment analysis
# send scott http://neuralnetworksanddeeplearning.com/
# lstm for generation?
# send link to arjun
