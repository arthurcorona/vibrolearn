from estimators.pipeline import Pipeline, load_function
from dataset.utils import filter_registers_by_key_value_sequence, get_acquisition_data, get_values_by_key, load_matlab_acquisition, prepare_segments_and_targets
import numpy as np
from time import time


class AugmentedPipeline(Pipeline):
    def train(self, list_of_registers, experimental_setup):
        self.experimental_setup = experimental_setup

        start = time()
        X_ori, y_ori = load_function(list_of_registers, self.experimental_setup)
        end = time()
        self.scores["load_data_time"] = end - start

        start = time()
        X_aug, y_aug = get_agumented_data(list_of_registers, self.experimental_setup, 3)
        end = time()
        self.scores["data_augmentation_time"] = end - start

        X = np.concatenate([X_ori, X_aug], axis=0)
        y = np.concatenate([y_ori, y_aug], axis=0)

        start = time()
        self.pipe.fit(X, y)
        end = time()
        self.scores["training_time"] = end - start

        return self


def get_agumented_data(list_of_registers, experimental_setup, repetitions):
    X, y = [], []
    for _ in range(repetitions):
        X_aug, y_aug = augment_acquisition(list_of_registers, experimental_setup)
        X.append(X_aug)
        y.append(y_aug)
    X = np.concatenate(X, axis=0)
    y = np.concatenate(y, axis=0)
    return X, y


def augment_acquisition(list_of_registers, experimental_setup):
    conditions = get_values_by_key(list_of_registers, "condition")
    X, y, = [], []
    for condition in conditions:
        X_agregated, y_agregated = aggregate_load_acquistions(list_of_registers, condition, experimental_setup)
        if X_agregated is None or y_agregated is None:
            continue
        X.append(X_agregated)
        y.append(y_agregated)
    X = np.concatenate(X, axis=0)
    y = np.concatenate(y, axis=0)
    return X, y


def aggregate_load_acquistions(list_of_registers, condition, experimental_setup):
    X, y = [], []
    loads = (list(get_values_by_key(list_of_registers, "load")))
    for load in loads:
        condition_registers = filter_registers_by_key_value_sequence(list_of_registers, [("condition", [condition]), ("load", [load])])
        if len(condition_registers) <= 1:
            continue
        X_mixed, y_mixed = mix_severity_data(condition_registers, experimental_setup)
        X.append(X_mixed)
        y.append(y_mixed)
    if len(X) == 0 or len(y) == 0:
        return None, None
    X = np.concatenate(X, axis=0)
    y = np.concatenate(y, axis=0)
    return X,y


def mix_severity_data(condition_registers, experimental_setup):
    segment_length=experimental_setup["segment_length"]
    acquisitions = []
    X, y = [], []
    for condition_register in condition_registers:
        acquisition = load_original_acquisitions(condition_register, experimental_setup)
        acquisitions.append(acquisition)
    for i in range(len(acquisitions)-1):
        for j in range(i+1, len(acquisitions)):
            mixed_acquisition = mix_two_acquisitions(acquisitions[i], acquisitions[j])
            X_mix, y_mix = prepare_segments_and_targets(segment_length=segment_length, register=condition_registers[i], acquisition=mixed_acquisition)
            X.append(X_mix)
            y.append(y_mix)
    X = np.concatenate(X, axis=0)
    y = np.concatenate(y, axis=0)
    return X, y


def load_original_acquisitions(condition_register, experimental_setup):
    raw_dir_path=experimental_setup["raw_dir_path"]
    channels_columns=experimental_setup["channels_columns"]
    load_acquisition_func=eval(experimental_setup["load_acquisition_func"])
    acquisition = get_acquisition_data(raw_dir_path, channels_columns, load_acquisition_func, condition_register)
    return acquisition


def generate_mixed_segments(condition_registers, severity_acquisitions, severity_levels, X_severity, y_severity, experimental_setup):
    segment_length=experimental_setup["segment_length"]
    X, y = [], []
    for i in range(len(severity_levels)-1):
        for j in range(i+1, len(severity_levels)):
            mixed_acquisition = mix_two_acquisitions(severity_acquisitions[i], severity_acquisitions[j])
            X_mix, y_mix = prepare_segments_and_targets(segment_length=segment_length, register=condition_registers[i], acquisition=mixed_acquisition)
            X.append(X_mix)
            y.append(y_mix)
    X = np.concatenate(X, axis=0)
    y = np.concatenate(y, axis=0)
    return X, y


def mix_two_acquisitions(acq1, acq2):
    min_length = min(acq1.shape[0], acq2.shape[0])
    acq1, acq2 = acq1[:min_length], acq2[:min_length]
    xf1, xf2 = np.fft.rfft(acq1, axis=0), np.fft.rfft(acq2, axis=0)
    xf_mix = (xf1 + xf2)
    return np.fft.irfft(xf_mix, n=max(acq1.shape[0], acq2.shape[0]), axis=0)
