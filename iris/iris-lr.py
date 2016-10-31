import tensorflow as tf
import tensorflow.contrib.learn as tfl
import pandas as pd
import numpy as np

# parameters
RANDOM_SEED = 0
LEARN_RATE  = 0.01
TRAIN_PART  = 0.8
TRAIN_STEPS = 1000
TRAIN_BATCH = 100

# load the iris dataset
iris     = pd.read_csv('iris.csv')
features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
classes  = list(iris['label'].unique())
iris['label_i'] = iris['label'].map(lambda l: classes.index(l))

# permute and partition the dataset
train = iris.sample(frac = TRAIN_PART, random_state = RANDOM_SEED)
test  = iris.drop(train.index)

# train the logistic model
classifier = tfl.LinearClassifier(
    n_classes = len(classes),
    feature_columns = tfl.infer_real_valued_columns_from_input(iris[features])
)
classifier.fit(
    train[features],
    train['label_i'],
    steps = TRAIN_STEPS,
    batch_size = TRAIN_BATCH
)

# test the model
test['predict'] = list(classifier.predict(test[features], as_iterable = True))
print(
    'accuracy:   ',
    (test['predict'] == test['label_i']).astype(float).sum() / len(test)
)

# classify a sample
np.random.seed()
s = test.sample(1)
print('features:   ', s[features].values[0])
print('label:      ', s['label'].values[0])
print('prediction: ', classes[s['predict'].values[0]])
