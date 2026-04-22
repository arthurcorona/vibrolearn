from sklearn.pipeline import Pipeline as SklearnPipeline
from dataset.utils import get_X_y, load_matlab_acquisition
from time import time


def load_function(registers, experimental_setup):
    raw_dir_path=experimental_setup["raw_dir_path"]
    channels_columns=experimental_setup["channels_columns"]
    segment_length=experimental_setup["segment_length"]
    load_acquisition_func=eval(experimental_setup["load_acquisition_func"])
    X, y = get_X_y(registers, 
                   raw_dir_path=raw_dir_path, 
                   channels_columns=channels_columns, 
                   segment_length=segment_length, 
                   load_acquisition_func=load_acquisition_func)
    return X, y


class Pipeline():
    def __init__(self, steps):
        self.pipe = SklearnPipeline(steps)
        self.scores = {}
  
    def train(self, list_of_registers, experimental_setup):
        self.experimental_setup = experimental_setup
        start = time()
        X, y = load_function(list_of_registers, self.experimental_setup)
        end = time()
        self.scores["load_data_time"] = end - start
        start = time()
        self.pipe.fit(X, y)
        end = time()
        self.scores["training_time"] = end - start
        return self
    
    def evaluate(self, list_of_registers, list_of_metrics):
        X, y = load_function(list_of_registers, self.experimental_setup)
        start = time()
        y_pred = self.pipe.predict(X)
        end = time()
        self.scores["prediction_time"] = end - start
        scores = {}
        for metric in list_of_metrics:
            scores[metric.__name__] = metric(y, y_pred)
        self.scores = self.scores | scores
        return self.scores