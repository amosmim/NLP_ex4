from sklearn.tree import DecisionTreeClassifier , export_graphviz
import pandas as pd
import graphviz
from sklearn.externals import joblib

LABEL_COLUMN_NAME = 'Is live in'


class Train_Decision_Tree :
    def __init__(self, train_feature_csv_name):
        self.df = pd.read_csv(train_feature_csv_name, index_col=0)
        self.tree = None

    def train(self, model_file=None, print_file=None):
        features = list(self.df[:-2])
        print ("There is {0} feature classes, and they are: {1}".format(len(features), features))
        y = self.df[LABEL_COLUMN_NAME]
        X = self.df[features]
        tree = DecisionTreeClassifier(min_samples_split=0.05, presort=True)
        tree.fit(X, y)
        self.tree = tree
        if model_file:
            joblib.dump(tree, model_file)
        if print_file:
            with open(print_file, 'w') as f:
                dot_data = export_graphviz(tree, out_file=f, feature_names=features)
                print(graphviz.Source(dot_data))

    def predict(self, feature_line):
        if not self.tree:
            self.train()
        return self.tree.predict(feature_line)[0]