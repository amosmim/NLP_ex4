import xgboost as xgb
import numpy as np


class MyClassifier(object):
    def __init__(self, f2i, lr=0.1, n_estimators=50, max_depth=300, min_child_weight=1,
                 gamma=0, subsample=0.8, colsample_bytree=0.8, scale_pos_weight=1, seed=27):
        self.f2i = f2i
        self.model = xgb.XGBClassifier(learning_rate=lr,
                                       n_estimators=n_estimators,
                                       max_depth=max_depth,
                                       min_child_weight=min_child_weight,
                                       gamma=gamma,
                                       subsample=subsample,
                                       colsample_bytree=colsample_bytree,
                                       scale_pos_weight=scale_pos_weight,
                                       objective='multi:softprob',
                                       seed=seed)

    def transform(self, data):
        """
        encode each feature in the features.
        :param data: list of lists, each list is features.
        :return: matrix that represents the given data.
        """
        transformed = []

        for _, ls in data:
            tranformed_ls = []
            for phrase in ls:
                if phrase not in self.f2i:
                    self.f2i[phrase] = len(self.f2i)
                tranformed_ls.append(self.f2i[phrase])
            transformed.append(tranformed_ls)

        return transformed

    def train_on(self, train_data, train_labels):
        """
        fit the model on the given train-data.
        :param train_data: list of lists, each list is a features-list.
        :param train_labels: list of labels, each is a number.
        """
        train_data = self.transform(train_data)
        train_data, train_labels = np.array(train_data), np.array(train_labels)
        self.model.fit(train_data, train_labels, eval_metric='mlogloss')

    def predict(self, data):
        """
        :param data: list of items to tag.
        :return: list of labels that the model predicted.
        """
        data = self.transform(data)
        preds = self.model.predict(data)
        preds = [round(val) for val in preds]
        return preds
