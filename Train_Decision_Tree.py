import subprocess
from sklearn.tree import DecisionTreeClassifier , export_graphviz
from pandas import read_csv
import pydot
from sklearn.externals import joblib

LABEL_COLUMN_NAME = 'Is live in'


class Train_Decision_Tree :
    def __init__(self, train_feature_csv_name=None):
        if train_feature_csv_name:
            self.df = read_csv(train_feature_csv_name)
        self.tree = None

    @classmethod
    def from_filename(cls, model_file_name):
        c = cls()
        c.tree = joblib.load(model_file_name)
        return c

    def train(self, model_file=None, print_file=None):
        features = list(self.df.columns[1:-1])
        print ("There is {0} feature classes, and they are: {1}".format(len(features), features))
        y = self.df[LABEL_COLUMN_NAME]
        X = self.df[features]
        tree = DecisionTreeClassifier(min_samples_split=20,  random_state=99,presort=True)
        tree.fit(X, y)
        self.tree = tree
        if model_file:
            joblib.dump(tree, model_file)
        if print_file:
            with open("dt.dot", 'w') as f:
                export_graphviz(tree, out_file=f, feature_names=features)
                f.close()
            #    (graph,) = pydot.graph_from_dot_file("dt.dot")  # doesn't work to me ,
            #    graph.write_png(print_file)                    # can use http://webgraphviz.com/ instead

    def predict(self, feature_line):
        if not self.tree:
            self.train()
        return self.tree.predict(feature_line)[0]

