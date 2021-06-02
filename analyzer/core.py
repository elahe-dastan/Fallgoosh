import pickle
import config
import os
import sklearn


class SentimentAnalyse:
    def __init__(self):
        self.name = ""
        self.filename = ""
        self.loaded_model = ""

    def predict(self, y):
        print("Hello my name is " + self.name)


class SVM(SentimentAnalyse):
    def __init__(self):
        super().__init__()
        self.name = "SVM"
        self.filename = config.SVM
        self.loaded_model = pickle.load(open(self.filename, 'rb'))

    def predict(self, y):
        prediction = self.loaded_model.predict([y])
        return prediction
