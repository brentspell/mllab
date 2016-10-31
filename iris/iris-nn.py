import tensorflow as tf
import pandas as pd
import numpy as np

# parameters
RANDOM_SEED = 0
LEARN_RATE  = 0.01
TRAIN_PART  = 0.8
TRAIN_STEPS = 1000
TRAIN_BATCH = 100

# load the iris dataset and generate the one-hot class columns
iris     = pd.read_csv('iris.csv')
features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
classes  = iris['label'].unique()
for c in classes:
    iris[c] = iris['label'].map(lambda l: l == c).astype(float)

# permute and partition the dataset
train = iris.sample(frac = TRAIN_PART, random_state = RANDOM_SEED)
test  = iris.drop(train.index)

# inputs, weights, and bias
x = tf.placeholder(tf.float32, [None, len(features)])
w = tf.Variable(tf.zeros([len(features), len(classes)]))
b = tf.Variable(tf.zeros([len(classes)]))

# labels, response, errors, and output
y_ = tf.placeholder(tf.float32, [None, len(classes)])
y  = tf.nn.softmax(tf.matmul(x, w) + b)
e  = -tf.reduce_sum(y_ * tf.log(y))
o  = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))

# steps to train and evaluate
do_train = tf.train.AdamOptimizer(LEARN_RATE).minimize(e)
do_eval  = tf.reduce_mean(tf.cast(o, 'float'))

# train the softmax model
session = tf.Session()
session.run(tf.initialize_all_variables())

for i in range(TRAIN_STEPS):
    t = train.sample(TRAIN_BATCH)
    session.run(
        do_train,
        feed_dict = {x:  train[features],
                     y_: train[classes]})

# test the model
print()
print(
    'accuracy:   ',
    session.run(
        do_eval,
        feed_dict = {x:  test[features],
                     y_: test[classes]}
    )
)

# classify a sample
def classify(xs):
    hits = session.run(tf.argmax(y, 1), feed_dict = {x: xs[features]})
    return [classes[h] for h in hits]

np.random.seed()
s = test.sample(1)
print('features:   ', s[features].values[0])
print('label:      ', s['label'].values[0])
print('prediction: ', classify(s)[0])
