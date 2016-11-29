import tensorflow as tf
import pandas as pd
import numpy as np
from datetime import datetime
import math
import os
import iris.iris_nn as iris
import iris.iris_nn_io as iris_io

RANDOM_SEED  = 0
LEARN_RATE   = 0.1
TRAIN_EPOCHS = 2000
TRAIN_BATCH  = 100

tf.reset_default_graph()

x, y_ = iris_io.train_batch(["../data/iris/iris_train.csv"],
                            num_epochs=TRAIN_EPOCHS,
                            batch_size=TRAIN_BATCH,
                            seed=RANDOM_SEED)

y = iris.inference(x)

loss = iris.loss(y, y_)

train, global_step = iris.training(loss, LEARN_RATE)

saver = tf.train.Saver(tf.all_variables())
save_path = "../model/iris/"
os.makedirs(save_path, exist_ok=True)
save_path += "model"

summary_path = "../log/iris/" + datetime.now().strftime("%Y%m%d%H%M%S")
os.makedirs(summary_path, exist_ok=True)
summary_op = tf.merge_all_summaries()

step = 0
with tf.Session() as session:
    coord  = tf.train.Coordinator()
    writer = tf.train.SummaryWriter(summary_path, session.graph)

    session.run(tf.initialize_all_variables())
    session.run(tf.initialize_local_variables())

    threads = tf.train.start_queue_runners(coord=coord)

    try:
        while not coord.should_stop():
            _, step = session.run((train, global_step))
            if (step % 100 == 0):
                saver.save(session, save_path, global_step=global_step)
                summary = session.run(summary_op)
                writer.add_summary(summary, step)
                print("step: {0}".format(step))
    except tf.errors.OutOfRangeError:
        pass
    finally:
        saver.save(session, save_path, global_step=global_step)
        writer.flush()
        coord.request_stop()
        coord.join(threads)
