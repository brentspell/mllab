import tensorflow as tf
import pandas as pd
import numpy as np

# parameters
LEARN_RATE  = 0.01
TRAIN_STEPS = 1000
TRAIN_BATCH = 100
FEATURES    = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
CLASSES     = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

# load the iris dataset
columns = FEATURES + ['label']
train   = pd.read_csv('../data/iris/iris_train.csv', header=None, names=columns)
test    = pd.read_csv('../data/iris/iris_test.csv', header=None, names=columns)

# generate the one-hot class columns
for c in CLASSES:
    train[c] = train['label'].map(lambda l: l == c).astype(float)
    test[c]  = test['label'].map(lambda l: l == c).astype(float)

tf.reset_default_graph()

# inputs, weights, and bias
x = tf.placeholder(tf.float32, [None, len(FEATURES)])
w = tf.Variable(tf.zeros([len(FEATURES), len(CLASSES)]), name="w")
b = tf.Variable(tf.zeros([len(CLASSES)]), name="b")

# labels, response, errors, and output
y_ = tf.placeholder(tf.float32, [None, len(CLASSES)])
y  = tf.matmul(x, w) + b
e  = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))
o  = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))

# steps to train and evaluate
do_train = tf.train.AdamOptimizer(LEARN_RATE).minimize(e)
do_eval  = tf.reduce_mean(tf.cast(o, 'float'))

# train the softmax model
session = tf.Session()
session.run(tf.initialize_all_variables())

for i in range(TRAIN_STEPS):
    t = train.sample(TRAIN_BATCH)
    session.run(do_train, feed_dict={x: t[FEATURES], y_: t[CLASSES]})

print()
print('weights:')
print(session.run(w))
print('biases:')
print(session.run(b))
print()

# test the model
print(
    'accuracy:   ',
    session.run(do_eval, feed_dict={x: test[FEATURES], y_: test[CLASSES]})
)

# classify a sample
def classify(xs):
    hits = session.run(tf.argmax(y, 1), feed_dict={x: xs[FEATURES]})
    return [CLASSES[h] for h in hits]

np.random.seed()
s = test.sample(1)
print('features:   ', s[FEATURES].values[0])
print('label:      ', s['label'].values[0])
print('prediction: ', classify(s)[0])
