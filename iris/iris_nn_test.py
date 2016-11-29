import tensorflow as tf
import pandas as pd
import numpy as np
import math
import iris.iris_nn as iris
import iris.iris_nn_io as iris_io

# parameters
TEST_BATCH = 100

tf.reset_default_graph()

x, y_ = iris_io.eval_batch(["../data/iris/iris_test.csv"],
                           batch_size=TEST_BATCH)

y = iris.inference(x)
e = iris.evaluation(y, y_)

saver = tf.train.Saver()
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
