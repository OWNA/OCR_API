from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
import numpy as np
import xgboost as xgb
from tabulate import tabulate
from sklearn.model_selection import KFold
from itertools import groupby
from table.labeller import label_features_legacy
from table.training.reader import TARGET_NAMES, extract

np.random.seed(1234)


def print_results(test_prediction, test_targets, target_names,
                  train_prediction=None, train_targets=None):
    num_classes = len(target_names)
    table = []
    for k in range(num_classes):
        s = [t1 == t2 for t1, t2 in zip(test_prediction, test_targets) if t2 == k]
        table.append([target_names[k], len(s), np.mean(s)])
    if train_prediction is not None and train_targets is not None:
        table.append(['Train', len(train_prediction),
                      np.mean(train_prediction == train_targets)])
    table.append(['Test', len(test_prediction),
                   np.mean(test_prediction == test_targets)])
    m = confusion_matrix(test_targets, test_prediction)
    values = np.array(target_names)
    m = np.concatenate([values.reshape((num_classes, 1)), m], axis=1)
    values = np.insert(target_names, 0, '')
    m = np.concatenate([[values], m], axis=0)
    m = m.tolist()
    print tabulate(m)
    print tabulate(table)

def train(train_file,
          num_rounds=100,
          eta=0.02,
          with_null=False,
          test_files=None,
          dump_file=None,
          model_file=None):
    target_names = ['NULL'] + TARGET_NAMES if with_null else TARGET_NAMES
    train_features, train_targets, train_filenames = extract(
        train_file, with_null)
    print train_features.shape, train_targets.shape, train_filenames.shape
    test_features, test_targets, test_filenames = [], [], []
    num_classes = len(target_names)
    param = {
        'max_depth': 1,
        'eta': eta,
        'silent':1,
        'num_class': num_classes,
        'objective':'multi:softmax'
    }
    if test_files:
        for test_file in test_files:
            ftr, tgt, fn = extract(test_file, with_null)
            test_features.append(ftr)
            test_targets.append(tgt)
            test_filenames.append(fn)
        test_features = np.concatenate(test_features)
        test_filenames = np.concatenate(test_filenames)
        test_targets = np.concatenate(test_targets)
        dtrain = xgb.DMatrix(train_features, label=train_targets)
        dtest = xgb.DMatrix(test_features)
        bst = xgb.train(param, dtrain, num_rounds)
        if model_file:
            bst.save_model(model_file)
        if dump_file:
            bst.dump_model(dump_file)
        train_prediction = bst.predict(dtrain)
        test_prediction = bst.predict(dtest)
    else:
        N = len(train_targets)
        permutation = np.random.permutation(N)
        features = train_features[permutation]
        targets = train_targets[permutation]
        filenames = train_filenames[permutation]
        kf = KFold(n_splits=5)
        train_indices = []
        test_indices = []
        train_predictions = []
        test_predictions = []
        for train_index, test_index in kf.split(features):
            train_features = features[train_index]
            test_features = features[test_index]
            train_targets = targets[train_index]
            test_targets = targets[test_index]
            dtrain = xgb.DMatrix(train_features, label=train_targets)
            dtest = xgb.DMatrix(test_features)
            bst = xgb.train(param, dtrain, num_rounds)
            train_predictions.append(bst.predict(dtrain))
            test_predictions.append(bst.predict(dtest))
            train_indices.append(train_index)
            test_indices.append(test_index)
        dtrain = xgb.DMatrix(features, label=targets)
        bst = xgb.train(param, dtrain, num_rounds)
        lr = LogisticRegression()
        lr.fit(features, targets)
        if model_file:
            bst.save_model(model_file)
        if dump_file:
            bst.dump_model(dump_file)
        train_prediction = np.concatenate(train_predictions)
        test_prediction = np.concatenate(test_predictions)
        train_indices = np.concatenate(train_indices)
        test_indices = np.concatenate(test_indices)
        train_targets = targets[train_indices]
        test_targets = targets[test_indices]
        train_filenames = filenames[train_indices]
        test_filenames = filenames[test_indices]
        train_features = features[train_indices]
        test_features = features[test_indices]
    for t1, t2, f, filename in zip(test_prediction,
                                   test_targets,
                                   test_features,
                                   test_filenames):
        continue
        if t1 != t2 and t2 == 0 and t1 == 4:
            print filename, target_names[t2], target_names[int(t1)]
    print_results(test_prediction, test_targets, target_names,
                  train_prediction, train_targets)


def evaluate_legacy(filename):
    features, targets, filenames = extract(filename, True)
    target_names = ['NULL'] + TARGET_NAMES
    test_targets = []
    test_prediction = []
    for k, g in groupby(zip(features, targets, filenames), lambda x: x[2]):
        columns = []
        targets = []
        for item in g:
            columns.append(item[0])
            targets.append(item[1])
        columns = np.array(columns)
        labels = label_features_legacy(columns)
        labels = [target_names.index(label) for label in labels]
        test_targets += targets
        test_prediction += labels
    test_prediction = np.array(test_prediction)
    test_targets = np.array(test_targets)
    print_results(test_prediction, test_targets, target_names)


if __name__ == '__main__':
    # This should return the highest accuracy (It doesn't)
    train('out/train_synthetic.dat',
          test_files=['out/train_C.dat'],
          num_rounds=200,
          dump_file='out/train_synthetic.dump',
          model_file='out/train_synthetic.model')
    # This should be stable and not too bad, it should not be higher
    # than the previous one as the generation process should be the
    # same (It is higher)
    train('out/train_B.dat',
          num_rounds=200,
          test_files=['out/train_C.dat'],
          dump_file='out/train_B.dump',
          model_file='out/train_B.model')
    # This one should be good as it is the closest to the training
    # base, however, a good synthetic data generator should be able
    # to match it if not to surpass it (Currently it doesn't)
    train('out/train.dat',
          num_rounds=2000,
          dump_file='out/train.dump',
          model_file='out/train.model')
    train('out/train.dat',
          num_rounds=4000,
          with_null=True,
          dump_file='out/train_with_null.dump',
          model_file='out/train_with_null.model')
    evaluate_legacy('out/train.dat')
    exit(1)
