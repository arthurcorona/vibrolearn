from sklearn.pipeline import Pipeline as SklearnPipeline
from dataset.utils import get_X_y, load_matlab_acquisition
from timed_decorator.simple_timed import timed

@timed(return_time=True, use_seconds=True)
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


@timed(return_time=True, use_seconds=True)
def timed_fit(pipe, X, y):
    return pipe.fit(X, y)

@timed(return_time=True, use_seconds=True)
def timed_predict(pipe, X):
    return pipe.predict(X)

class Pipeline():
    def __init__(self, steps):
        self.pipe = SklearnPipeline(steps)
        self.scores = {}
  
    def train(self, list_of_registers, experimental_setup):
        self.experimental_setup = experimental_setup
        (X, y), load_time = load_function(list_of_registers, self.experimental_setup)
        self.scores["load_data_time"] = load_time
        _, training_time = timed_fit(self.pipe, X, y)
        self.scores["training_time"] = training_time
        return self
    
    def evaluate(self, list_of_registers, list_of_metrics):
        (X, y), _ = load_function(list_of_registers, self.experimental_setup)
        y_pred, prediction_time = timed_predict(self.pipe, X)
        self.scores["prediction_time"] = prediction_time
        scores = {}
        for metric in list_of_metrics:
            scores[metric.__name__] = metric(y, y_pred)
        self.scores = self.scores | scores
        return self.scores