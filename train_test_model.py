import pickle
from models import *
import numpy
numpy.random.seed(42)
from sklearn.preprocessing import OneHotEncoder
import sys
from sklearn.preprocessing import OneHotEncoder
sys.setrecursionlimit(10000)

sample_ratio = 0.025
train_ratio = 0.5
shuffle_data = False
one_hot_as_input = True
embeddings_as_input = False
# saved_embeddings_fname = "embeddings_unshuffled.pickle"  # Use plot_embeddings.ipynb to create
saved_embeddings_fname = "embeddings_shuffled.pickle"

f = open('feature_train_data.pickle', 'rb')
(X, y) = pickle.load(f)

def sample(X, y, n):
    '''random samples'''
    num_row = X.shape[0]
    indices = numpy.random.randint(num_row, size=n)
    indices = numpy.sort(indices)
    return X[indices, :], y[indices]

num_records = len(X)
sample_size = int(sample_ratio * num_records)

X_sample, y_sample = sample(X, y, sample_size)  # Simulate data sparsity

assert(sample_size == X_sample.shape[0])

if shuffle_data:
    print("Using shuffled data")
    sh = numpy.arange(X_sample.shape[0])
    numpy.random.shuffle(sh)
    X_sample = X_sample[sh]
    y_sample = y_sample[sh]

if embeddings_as_input:
    print("Using learned embeddings as input")
    X_sample = embed_features(X_sample, saved_embeddings_fname)

if one_hot_as_input:
    print("Using one-hot encoding as input")
    enc = OneHotEncoder(sparse=False)
    enc.fit(X)
    X_sample = enc.transform(X_sample)

train_size = int(train_ratio * sample_size)

X_train = X_sample[:train_size]
X_val = X_sample[train_size:]
y_train = y_sample[:train_size]
y_val = y_sample[train_size:]

models = []

# print("Fitting NN_with_EntityEmbedding...")
# for i in range(5):
#    models.append(NN_with_EntityEmbedding(X_train, y_train, X_val, y_val))

print("Fitting NN...")
for i in range(5):
    models.append(NN(X_train, y_train, X_val, y_val))

# print("Fitting LinearModel...")
# models.append(LinearModel(sX_train, y_train, X_val, y_val))

# print("Fitting RF...")
# models.append(RF(X_train, y_train, X_val, y_val))

# print("Fitting KNN...")
# models.append(KNN(X_train, y_train, X_val, y_val))

# print("Fitting XGBoost...")
# models.append(XGBoost(X_train, y_train, X_val, y_val))

# print("Fitting HistricalMedian...")
# models.append(HistricalMedian(X_train, y_train, X_val, y_val))

with open('models.pickle', 'wb') as f:
     pickle.dump(models, f)


def evaluate_models(models, X, y):
    assert(min(y) > 0)
    guessed_sales = numpy.array([model.guess(X) for model in models])
    mean_sales = guessed_sales.mean(axis=0)
    relative_err = numpy.absolute((y - mean_sales) / y)
    result = numpy.sum(relative_err) / len(y)
    return result

print("Evaluate combined models...")
print("Training error...")
r_train = evaluate_models(models, X_train, y_train)
print(r_train)

print("Validation error...")
r_val = evaluate_models(models, X_val, y_val)
print(r_val)
